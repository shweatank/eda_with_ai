"""
Simulation service -- runs the compiled image with the real `vvp` engine.

    vvp simulation.vvp

Writes the combined output to `simulation.log` inside the job's work
directory, and locates the `waveform.vcd` the testbench dumped.
"""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import List, Optional

from backend.config import settings
from backend.models.schemas import SimulationRun


class SimulationError(RuntimeError):
    pass


def run_simulation(
    vvp_file: Path,
    work_dir: Path,
    log_name: str = "simulation.log",
    vcd_name: str = "waveform.vcd",
) -> SimulationRun:
    """
    Execute the simulation and persist its output.

    A simulation that runs but reports failing tests is a *successful*
    run: ``success`` describes the execution, not the verification verdict.
    """
    # vvp runs with cwd=work_dir so the VCD lands there; the image path
    # must therefore be absolute
    vvp_file = Path(vvp_file).resolve()
    work_dir = Path(work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    binary = shutil.which(settings.VVP_BIN)
    if binary is None:
        raise SimulationError(
            f"`vvp` not found on PATH (part of Icarus Verilog). "
            f"Looked for {settings.VVP_BIN!r}."
        )
    if not vvp_file.is_file():
        raise SimulationError(f"Compiled simulation image not found: {vvp_file}")

    log_path = work_dir / log_name
    command: List[str] = [binary, str(vvp_file)]

    started = time.perf_counter()
    timed_out = False
    try:
        proc = subprocess.run(
            command,
            shell=False,                       # never shell=True
            cwd=str(work_dir),                 # so $dumpfile lands here
            capture_output=True,
            text=True,
            timeout=settings.SIM_TIMEOUT_SECONDS,
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        return_code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + (
            f"\nSimulation timed out after {settings.SIM_TIMEOUT_SECONDS}s."
        )
        return_code = -1

    duration = round(time.perf_counter() - started, 4)

    # ---- persist the combined output as simulation.log ----
    combined = stdout
    if stderr.strip():
        combined = f"{stdout}\n--- stderr ---\n{stderr}"
    try:
        log_path.write_text(combined, encoding="utf-8")
    except OSError as exc:                                  # pragma: no cover
        raise SimulationError(f"Could not write {log_path}: {exc}") from exc

    # ---- locate the VCD the testbench dumped ----
    vcd_path: Optional[Path] = work_dir / vcd_name
    if not vcd_path.is_file():
        candidates = sorted(work_dir.glob("*.vcd"))
        vcd_path = candidates[0] if candidates else None

    error_message = None
    if timed_out:
        error_message = f"Simulation timed out after {settings.SIM_TIMEOUT_SECONDS}s"
    elif return_code != 0:
        error_message = (
            f"vvp exited with code {return_code}. {stderr.strip()[:1500]}"
        )
    elif not stdout.strip():
        error_message = "Simulation produced no output to parse"

    return SimulationRun(
        success=(not timed_out and return_code == 0 and bool(stdout.strip())),
        command=command,
        stdout=stdout,
        stderr=stderr,
        return_code=return_code,
        duration_seconds=duration,
        log_path=str(log_path),
        vcd_path=str(vcd_path) if vcd_path else None,
        error_message=error_message,
        timed_out=timed_out,
    )
