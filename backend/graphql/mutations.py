"""GraphQL mutations: createProject and runVerification."""
from __future__ import annotations

import logging

import strawberry

from backend.graphql.types import ProjectType, VerificationJobType
from backend.services.neo4j_service import neo4j_service
from backend.services.verification_service import (
    VerificationError,
    verification_service,
)

log = logging.getLogger(__name__)


@strawberry.type
class Mutation:

    @strawberry.mutation(description="Create (or update) a Project node in Neo4j.")
    def createProject(
        self,
        projectId: str,
        name: str,
        description: str = "",
    ) -> ProjectType:
        row = neo4j_service.create_project(projectId, name, description)
        return ProjectType(
            projectId=row.get("projectId") or projectId,
            name=row.get("name") or name,
            description=row.get("description") or description,
            createdAt=row.get("createdAt") or "",
        )

    @strawberry.mutation(
        description=(
            "Compile + simulate one example with Icarus Verilog in the "
            "background. Returns the job id immediately. "
            "example: traffic_light | alu   scenario: passing | failing"
        )
    )
    def runVerification(
        self,
        projectId: str,
        example: str,
        scenario: str,
    ) -> VerificationJobType:
        try:
            result = verification_service.submit(projectId, example, scenario)
        except VerificationError as exc:
            # a bad example/scenario, or a missing .sv file
            raise ValueError(str(exc)) from exc

        return VerificationJobType(
            jobId=result.job_id,
            status=result.status.value,
            progress=result.progress,
            example=result.example,
            scenario=result.scenario,
        )
