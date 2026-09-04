"""
FastAPI application entry point.

    uvicorn backend.main:app --reload --port 8000

Endpoints:
    GET  /health    -> {"status": "ok", "neo4j": "connected"}
    ANY  /graphql   -> Strawberry GraphQL (GraphiQL IDE in the browser)
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from backend.config import settings
from backend.database.neo4j_client import neo4j_client
from backend.database.neo4j_schema import initialize_schema
from backend.graphql.schema import schema
from backend.services.compilation_service import iverilog_version
from backend.services.verification_service import verification_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
)
log = logging.getLogger("rtl_platform")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------------------------- startup -------------------------
    log.info("Starting AI-Powered RTL Verification & Debugging Platform")
    log.info("Configuration: %s", settings.safe_summary())
    log.info("Icarus Verilog: %s", iverilog_version())

    settings.JOBS_DIR.mkdir(parents=True, exist_ok=True)

    if neo4j_client.connect():
        report = initialize_schema(neo4j_client)
        log.info(
            "Neo4j ready (constraints/indexes applied: %d/%d)",
            report["applied"], report["statements"],
        )
    else:
        # The app still starts so /health can explain what is wrong.
        log.error(
            "Neo4j is NOT connected: %s",
            neo4j_client.last_error or "unknown error",
        )

    yield

    # ------------------------- shutdown ------------------------
    log.info("Shutting down: stopping workers and closing Neo4j driver")
    verification_service.shutdown()
    neo4j_client.close()


app = FastAPI(
    title="AI-Powered RTL Verification & Debugging Platform",
    description=(
        "Verifies SystemVerilog RTL with Icarus Verilog, stores the "
        "verification graph in Neo4j AuraDB, and explains failures with Groq."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Streamlit runs on a different port, so allow local cross-origin calls.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(GraphQLRouter(schema), prefix="/graphql")


@app.get("/health", tags=["health"])
def health() -> dict:
    """Never returns a credential -- only whether one is configured."""
    return {
        "status": "ok",
        "neo4j": neo4j_client.health(),
        "neo4j_error": neo4j_client.last_error,
        "groq": "configured" if settings.groq_configured else "not configured",
        "groq_model": settings.GROQ_MODEL,
        "iverilog": iverilog_version(),
    }


@app.get("/", tags=["health"])
def root() -> dict:
    return {
        "service": "AI-Powered RTL Verification & Debugging Platform",
        "graphql": "/graphql",
        "health": "/health",
    }
