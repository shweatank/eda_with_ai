import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from backend.db import get_job, list_jobs
from backend.workflow.engine import WorkflowEngine

router = APIRouter(prefix='/api')
jobs: dict[str, WorkflowEngine] = {}


class DesignRequest(BaseModel):
    prompt: str


@router.post('/design')
async def create_design(request: DesignRequest):
    job_id = str(uuid4())
    engine = WorkflowEngine(job_id)
    jobs[job_id] = engine
    asyncio.create_task(engine.run(request.prompt))
    return {'job_id': job_id, 'status': 'started'}


@router.get('/designs')
async def get_designs(limit: int = Query(50, ge=1, le=200)):
    return {'jobs': list_jobs(limit)}


@router.get('/design/{job_id}')
async def get_design(job_id: str):
    if job_id in jobs:
        return jobs[job_id].snapshot()
    snapshot = get_job(job_id)
    if snapshot is None:
        raise HTTPException(404, 'Job not found')
    return snapshot


@router.get('/design/{job_id}/artifact', response_class=PlainTextResponse)
async def artifact(job_id: str, path: str = Query(...)):
    engine = jobs.get(job_id)
    snapshot = engine.snapshot() if engine else get_job(job_id)
    if snapshot is None:
        raise HTTPException(404, 'Job not found')

    workspace = Path(snapshot['artifacts'].get(path, ''))
    if not workspace.is_file():
        raise HTTPException(404, 'Artifact not found')
    return workspace.read_text(encoding='utf-8', errors='replace')
