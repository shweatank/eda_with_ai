"""
Compilation service -- drives the real `iverilog` binary.

    iverilog -g2012 -o simulation.vvp <rtl_file> <testbench_file>

Safety rules enforced here:
  * subprocess is always called with shell=False and an argv *list*
  * os.system() is never used
  * stdout, stderr, return code and wall-clock duration are all captured
"""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import List

from backend.config import settings
from backend.models.schemas import CompilationResult


class CompilationError(RuntimeError):
    pass


def iverilog_version() -> str:
    """Return `iverilog -V` first line, or an explanatory error string."""
    binary = shutil.which(settings.IVERILOG_BIN)
    if binary is None:
        return f"not found on PATH (looked for {settings.IVERILOG_BIN!r})"
    try:
        proc = subprocess.run(
            [binary, "-V"],
            shell=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
        first = (proc.stdout or proc.stderr).strip().splitlines()
        return first[0] if first else "unknown version"
    except Exception as exc:                                # pragma: no cover
        return f"error querying version: {exc}"


def compile_design(
    rtl_file: Path,
    testbench_file: Path,
    work_dir: Path,
    output_name: str = "simulation.vvp",
) -> CompilationResult:
    """
    Compile one RTL file plus its testbench into a .vvp image.

    Never raises for a *compilation* failure -- that is a normal, expected
    outcome and is reported via ``CompilationResult.success``. Only genuine
    environment problems (missing tool / missing file) raise.
    """
    # resolve to absolute paths: iverilog runs with cwd=work_dir, so a
    # relative source path would not be found
    rtl_file = Path(rtl_file).resolve()
    testbench_file = Path(testbench_file).resolve()
    work_dir = Path(work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    # ---- environment / input validation ----
    binary = shutil.which(settings.IVERILOG_BIN)
    if binary is None:
        raise CompilationError(
            f"Icarus Verilog not found. Install it (e.g. `sudo apt install iverilog`) "
            f"or set IVERILOG_BIN in .env. Looked for {settings.IVERILOG_BIN!r}."
        )
    for f in (rtl_file, testbench_file):
        if not f.is_file():
            raise CompilationError(f"Source file not found: {f}")

    vvp_path = work_dir / output_name
    command: List[str] = [
        binary,
        "-g2012",
        "-o",
        str(vvp_path),
        str(rtl_file),
        str(testbench_file),
    ]

    started = time.perf_counter()
    try:
        proc = subprocess.run(
            command,
            shell=False,                       # never shell=True
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=settings.SIM_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return CompilationResult(
            success=False,
            command=command,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + "\nCompilation timed out.",
            return_code=-1,
            duration_seconds=round(time.perf_counter() - started, 4),
            error_message=(
                f"iverilog timed out after {settings.SIM_TIMEOUT_SECONDS}s"
            ),
        )
    duration = round(time.perf_counter() - started, 4)

    produced = vvp_path.is_file()
    success = proc.returncode == 0 and produced

    error_message = None
    if not success:
        if proc.returncode != 0:
            error_message = (
                f"iverilog exited with code {proc.returncode}. "
                f"{(proc.stderr or proc.stdout or '').strip()[:1500]}"
            )
        else:
            error_message = (
                "iverilog reported success but produced no simulation image at "
                f"{vvp_path}"
            )

    return CompilationResult(
        success=success,
        command=command,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
        return_code=proc.returncode,
        duration_seconds=duration,
        vvp_path=str(vvp_path) if produced else None,
        error_message=error_message,
    )
