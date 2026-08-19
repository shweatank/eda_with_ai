from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.simulator import (
    run_simulation,
    PROJECTS_DIR,
    RESULTS_DIR,
    LOGS_DIR,
    WAVEFORMS_DIR,
)


app = FastAPI(
    title="RTL Verification API",
    description="API for running RTL simulation and verification",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Root API
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "name": "RTL Verification API",
        "version": "1.0.0",
        "status": "running",
    }


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/api/health")
def health():

    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# List projects
# ---------------------------------------------------------

@app.get("/api/projects")
def list_projects():

    if not PROJECTS_DIR.exists():

        return {
            "projects": []
        }

    projects = []

    for path in PROJECTS_DIR.iterdir():

        if path.is_dir():

            projects.append({
                "name": path.name,
                "path": str(path),
                "has_makefile": (
                    path / "Makefile"
                ).exists(),
                "has_rtl": (
                    len(
                        list(path.glob("*.sv"))
                    ) > 0
                ),
                "has_tests": (
                    len(
                        list(path.glob("test_*.py"))
                    ) > 0
                ),
            })

    return {
        "projects": projects
    }


# ---------------------------------------------------------
# Project information
# ---------------------------------------------------------

@app.get("/api/projects/{project_name}")
def project_info(project_name: str):

    project_path = (
        PROJECTS_DIR / project_name
    )

    if not project_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    rtl_files = [
        p.name
        for p in project_path.glob("*.sv")
    ]

    test_files = [
        p.name
        for p in project_path.glob("test_*.py")
    ]

    return {
        "name": project_name,
        "path": str(project_path),
        "rtl_files": rtl_files,
        "test_files": test_files,
        "makefile": (
            project_path / "Makefile"
        ).exists(),
    }


# ---------------------------------------------------------
# Run simulation
# ---------------------------------------------------------

@app.post("/api/projects/{project_name}/run")
def run_project(project_name: str):

    project_path = (
        PROJECTS_DIR / project_name
    )

    if not project_path.exists():

        raise HTTPException(
            status_code=404,
            detail=f"Project '{project_name}' not found"
        )

    makefile = project_path / "Makefile"

    if not makefile.exists():

        raise HTTPException(
            status_code=400,
            detail="Makefile not found"
        )

    try:

        result = run_simulation(
            project_name
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ---------------------------------------------------------
# List logs
# ---------------------------------------------------------

@app.get("/api/results/logs")
def list_logs():

    if not LOGS_DIR.exists():

        return {
            "logs": []
        }

    logs = []

    for path in sorted(
        LOGS_DIR.glob("*.log"),
        reverse=True
    ):

        logs.append({
            "name": path.name,
            "path": str(path),
            "size_bytes": path.stat().st_size,
        })

    return {
        "logs": logs
    }


# ---------------------------------------------------------
# List waveforms
# ---------------------------------------------------------

@app.get("/api/results/waveforms")
def list_waveforms():

    if not WAVEFORMS_DIR.exists():

        return {
            "waveforms": []
        }

    waveforms = []

    for path in sorted(
        WAVEFORMS_DIR.glob("*.vcd"),
        reverse=True
    ):

        waveforms.append({
            "name": path.name,
            "path": str(path),
            "size_bytes": path.stat().st_size,
        })

    return {
        "waveforms": waveforms
    }


# ---------------------------------------------------------
# List all results
# ---------------------------------------------------------

@app.get("/api/results")
def list_results():

    logs = []

    if LOGS_DIR.exists():

        logs = [
            p.name
            for p in sorted(
                LOGS_DIR.glob("*.log"),
                reverse=True
            )
        ]

    waveforms = []

    if WAVEFORMS_DIR.exists():

        waveforms = [
            p.name
            for p in sorted(
                WAVEFORMS_DIR.glob("*.vcd"),
                reverse=True
            )
        ]

    return {
        "logs": logs,
        "waveforms": waveforms,
    }