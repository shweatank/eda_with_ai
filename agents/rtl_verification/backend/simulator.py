import subprocess
from pathlib import Path
from datetime import datetime
import shutil


BASE_DIR = Path(__file__).resolve().parent.parent

PROJECTS_DIR = BASE_DIR / "projects"
RESULTS_DIR = BASE_DIR / "results"

LOGS_DIR = RESULTS_DIR / "logs"
WAVEFORMS_DIR = RESULTS_DIR / "waveforms"


def get_project_path(project_name: str) -> Path:
    """
    Return the project directory.

    Example:
        all_gates -> projects/all_gates
    """

    project_path = PROJECTS_DIR / project_name

    if not project_path.exists():
        raise FileNotFoundError(
            f"Project '{project_name}' does not exist"
        )

    if not project_path.is_dir():
        raise ValueError(
            f"Project '{project_name}' is not a directory"
        )

    return project_path


def run_simulation(project_name: str) -> dict:

    project_path = get_project_path(project_name)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_file = LOGS_DIR / f"{project_name}_{timestamp}.log"

    waveform_file = WAVEFORMS_DIR / f"{project_name}_{timestamp}.vcd"

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    WAVEFORMS_DIR.mkdir(parents=True, exist_ok=True)

    make_path = shutil.which("make")

    if make_path is None:
        raise RuntimeError(
            "make command not found. Install GNU make."
        )

    command = [
        make_path,
        "SIM=icarus",
    ]

    start_time = datetime.now()

    try:

        result = subprocess.run(
            command,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120,
        )

        end_time = datetime.now()

        duration = (
            end_time - start_time
        ).total_seconds()

        output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        log_file.write_text(
            output,
            encoding="utf-8"
        )

        success = result.returncode == 0

        # Look for generated VCD files
        generated_vcd = list(
            project_path.glob("*.vcd")
        )

        waveform_path = None

        if generated_vcd:

            source_waveform = generated_vcd[0]

            shutil.copy2(
                source_waveform,
                waveform_file
            )

            waveform_path = str(
                waveform_file
            )

        return {
            "project": project_name,
            "status": "PASS" if success else "FAIL",
            "return_code": result.returncode,
            "duration_seconds": duration,
            "log_file": str(log_file),
            "waveform_file": waveform_path,
            "output": output,
        }

    except subprocess.TimeoutExpired:

        timeout_message = (
            "Simulation timed out after 120 seconds."
        )

        log_file.write_text(
            timeout_message,
            encoding="utf-8"
        )

        return {
            "project": project_name,
            "status": "TIMEOUT",
            "return_code": -1,
            "duration_seconds": 120,
            "log_file": str(log_file),
            "waveform_file": None,
            "output": timeout_message,
        }