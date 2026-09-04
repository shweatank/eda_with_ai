"""
Neo4j schema bootstrap.

Every constraint and index is created from Python when FastAPI starts --
nothing has to be typed into the Neo4j browser by hand.
"""
from __future__ import annotations

import logging
from typing import List

from backend.database.neo4j_client import Neo4jClient

log = logging.getLogger(__name__)

# One uniqueness constraint per node label, on its natural key.
CONSTRAINTS: List[str] = [
    "CREATE CONSTRAINT project_id IF NOT EXISTS "
    "FOR (n:Project) REQUIRE n.projectId IS UNIQUE",

    "CREATE CONSTRAINT rtl_id IF NOT EXISTS "
    "FOR (n:RTLModule) REQUIRE n.rtlId IS UNIQUE",

    "CREATE CONSTRAINT testbench_id IF NOT EXISTS "
    "FOR (n:Testbench) REQUIRE n.testbenchId IS UNIQUE",

    "CREATE CONSTRAINT job_id IF NOT EXISTS "
    "FOR (n:VerificationJob) REQUIRE n.jobId IS UNIQUE",

    "CREATE CONSTRAINT simulation_id IF NOT EXISTS "
    "FOR (n:Simulation) REQUIRE n.simulationId IS UNIQUE",

    "CREATE CONSTRAINT test_id IF NOT EXISTS "
    "FOR (n:Test) REQUIRE n.testId IS UNIQUE",

    "CREATE CONSTRAINT failure_id IF NOT EXISTS "
    "FOR (n:Failure) REQUIRE n.failureId IS UNIQUE",

    "CREATE CONSTRAINT waveform_id IF NOT EXISTS "
    "FOR (n:Waveform) REQUIRE n.waveformId IS UNIQUE",

    "CREATE CONSTRAINT analysis_id IF NOT EXISTS "
    "FOR (n:AIAnalysis) REQUIRE n.analysisId IS UNIQUE",
]

INDEXES: List[str] = [
    "CREATE INDEX job_status IF NOT EXISTS "
    "FOR (n:VerificationJob) ON (n.status)",

    "CREATE INDEX failure_category IF NOT EXISTS "
    "FOR (n:Failure) ON (n.category)",
]


def initialize_schema(client: Neo4jClient) -> dict:
    """
    Apply every constraint/index. Idempotent thanks to IF NOT EXISTS.

    Returns a small report so /health and the startup log can show what
    happened without crashing the app if AuraDB is briefly unreachable.
    """
    applied, failed = 0, []

    for statement in CONSTRAINTS + INDEXES:
        try:
            client.run(statement)
            applied += 1
        except Exception as exc:
            name = statement.split()[2] if len(statement.split()) > 2 else "?"
            failed.append(f"{name}: {type(exc).__name__}")
            log.warning("Schema statement failed (%s): %s", name, exc)

    report = {
        "statements": len(CONSTRAINTS) + len(INDEXES),
        "applied": applied,
        "failed": failed,
    }
    log.info("Neo4j schema init: %s", report)
    return report
