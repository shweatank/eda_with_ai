"""
Neo4j graph service -- creates every node and relationship from Python.

Graph shape
-----------
    (Project)-[:HAS_RTL]->(RTLModule)
    (Project)-[:HAS_TESTBENCH]->(Testbench)
    (Project)-[:HAS_JOB]->(VerificationJob)
    (VerificationJob)-[:USES_RTL]->(RTLModule)
    (VerificationJob)-[:USES_TESTBENCH]->(Testbench)
    (VerificationJob)-[:PRODUCED]->(Simulation)
    (Simulation)-[:HAS_TEST]->(Test)
    (Simulation)-[:HAS_FAILURE]->(Failure)
    (Simulation)-[:GENERATED]->(Waveform)
    (Failure)-[:ANALYZED_BY]->(AIAnalysis)

Every statement is parameterised Cypher -- no value is ever interpolated
into a query string.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from backend.database.neo4j_client import Neo4jClient, neo4j_client
from backend.models.schemas import (
    AIAnalysis,
    FailureInfo,
    ParsedLog,
    TestResult,
    utcnow_iso,
)

log = logging.getLogger(__name__)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


class Neo4jService:
    def __init__(self, client: Neo4jClient | None = None) -> None:
        self.client = client or neo4j_client

    # =================================================================
    # Project
    # =================================================================
    def create_project(
        self, project_id: str, name: str, description: str = ""
    ) -> Dict[str, Any]:
        rows = self.client.run(
            """
            MERGE (p:Project {projectId: $projectId})
            ON CREATE SET p.name        = $name,
                          p.description = $description,
                          p.createdAt   = $createdAt
            ON MATCH  SET p.name        = coalesce($name, p.name),
                          p.description = coalesce($description, p.description)
            RETURN p.projectId   AS projectId,
                   p.name        AS name,
                   p.description AS description,
                   p.createdAt   AS createdAt
            """,
            {
                "projectId": project_id,
                "name": name,
                "description": description,
                "createdAt": utcnow_iso(),
            },
        )
        return rows[0] if rows else {}

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        rows = self.client.run(
            """
            MATCH (p:Project {projectId: $projectId})
            RETURN p.projectId   AS projectId,
                   p.name        AS name,
                   p.description AS description,
                   p.createdAt   AS createdAt
            """,
            {"projectId": project_id},
        )
        return rows[0] if rows else None

    def list_projects(self) -> List[Dict[str, Any]]:
        return self.client.run(
            """
            MATCH (p:Project)
            RETURN p.projectId   AS projectId,
                   p.name        AS name,
                   p.description AS description,
                   p.createdAt   AS createdAt
            ORDER BY p.createdAt DESC
            """
        )

    # =================================================================
    # RTL module / testbench
    # =================================================================
    def upsert_rtl_module(
        self,
        project_id: str,
        rtl_id: str,
        module_name: str,
        file_name: str,
        file_path: str,
    ) -> Dict[str, Any]:
        rows = self.client.run(
            """
            MATCH (p:Project {projectId: $projectId})
            MERGE (r:RTLModule {rtlId: $rtlId})
            SET   r.moduleName = $moduleName,
                  r.fileName   = $fileName,
                  r.filePath   = $filePath
            MERGE (p)-[:HAS_RTL]->(r)
            RETURN r.rtlId      AS rtlId,
                   r.moduleName AS moduleName,
                   r.fileName   AS fileName,
                   r.filePath   AS filePath
            """,
            {
                "projectId": project_id,
                "rtlId": rtl_id,
                "moduleName": module_name,
                "fileName": file_name,
                "filePath": file_path,
            },
        )
        return rows[0] if rows else {}

    def upsert_testbench(
        self,
        project_id: str,
        testbench_id: str,
        file_name: str,
        file_path: str,
    ) -> Dict[str, Any]:
        rows = self.client.run(
            """
            MATCH (p:Project {projectId: $projectId})
            MERGE (t:Testbench {testbenchId: $testbenchId})
            SET   t.fileName = $fileName,
                  t.filePath = $filePath
            MERGE (p)-[:HAS_TESTBENCH]->(t)
            RETURN t.testbenchId AS testbenchId,
                   t.fileName    AS fileName,
                   t.filePath    AS filePath
            """,
            {
                "projectId": project_id,
                "testbenchId": testbench_id,
                "fileName": file_name,
                "filePath": file_path,
            },
        )
        return rows[0] if rows else {}

    # =================================================================
    # VerificationJob
    # =================================================================
    def create_job(
        self,
        job_id: str,
        project_id: str,
        example: str,
        scenario: str,
        status: str = "QUEUED",
        progress: int = 0,
    ) -> Dict[str, Any]:
        rows = self.client.run(
            """
            MERGE (p:Project {projectId: $projectId})
            ON CREATE SET p.name        = $projectId,
                          p.description = 'auto-created by runVerification',
                          p.createdAt   = $createdAt
            MERGE (j:VerificationJob {jobId: $jobId})
            SET   j.status       = $status,
                  j.progress     = $progress,
                  j.createdAt    = $createdAt,
                  j.completedAt  = null,
                  j.errorMessage = null,
                  j.example      = $example,
                  j.scenario     = $scenario
            MERGE (p)-[:HAS_JOB]->(j)
            RETURN j.jobId AS jobId, j.status AS status, j.progress AS progress
            """,
            {
                "jobId": job_id,
                "projectId": project_id,
                "example": example,
                "scenario": scenario,
                "status": status,
                "progress": progress,
                "createdAt": utcnow_iso(),
            },
        )
        return rows[0] if rows else {}

    def update_job_status(
        self,
        job_id: str,
        status: str,
        progress: int,
        error_message: Optional[str] = None,
        completed: bool = False,
    ) -> None:
        self.client.run(
            """
            MATCH (j:VerificationJob {jobId: $jobId})
            SET j.status   = $status,
                j.progress = $progress,
                j.errorMessage = CASE WHEN $errorMessage IS NULL
                                      THEN j.errorMessage ELSE $errorMessage END,
                j.completedAt  = CASE WHEN $completed
                                      THEN $now ELSE j.completedAt END
            """,
            {
                "jobId": job_id,
                "status": status,
                "progress": progress,
                "errorMessage": error_message,
                "completed": completed,
                "now": utcnow_iso(),
            },
        )

    def link_job_sources(
        self, job_id: str, rtl_id: str, testbench_id: str
    ) -> None:
        self.client.run(
            """
            MATCH (j:VerificationJob {jobId: $jobId})
            MATCH (r:RTLModule       {rtlId: $rtlId})
            MATCH (t:Testbench       {testbenchId: $testbenchId})
            MERGE (j)-[:USES_RTL]->(r)
            MERGE (j)-[:USES_TESTBENCH]->(t)
            """,
            {"jobId": job_id, "rtlId": rtl_id, "testbenchId": testbench_id},
        )

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        rows = self.client.run(
            """
            MATCH (j:VerificationJob {jobId: $jobId})
            RETURN j.jobId        AS jobId,
                   j.status       AS status,
                   j.progress     AS progress,
                   j.createdAt    AS createdAt,
                   j.completedAt  AS completedAt,
                   j.errorMessage AS errorMessage,
                   j.example      AS example,
                   j.scenario     AS scenario
            """,
            {"jobId": job_id},
        )
        return rows[0] if rows else None

    # =================================================================
    # Simulation + Test + Waveform
    # =================================================================
    def create_simulation(
        self,
        job_id: str,
        simulation_id: str,
        parsed: ParsedLog,
        duration: float,
    ) -> Dict[str, Any]:
        rows = self.client.run(
            """
            MATCH (j:VerificationJob {jobId: $jobId})
            MERGE (s:Simulation {simulationId: $simulationId})
            SET   s.status       = $status,
                  s.totalTests   = $totalTests,
                  s.passedTests  = $passedTests,
                  s.failedTests  = $failedTests,
                  s.duration     = $duration
            MERGE (j)-[:PRODUCED]->(s)
            RETURN s.simulationId AS simulationId,
                   s.status       AS status,
                   s.totalTests   AS totalTests,
                   s.passedTests  AS passedTests,
                   s.failedTests  AS failedTests,
                   s.duration     AS duration
            """,
            {
                "jobId": job_id,
                "simulationId": simulation_id,
                "status": parsed.status.value,
                "totalTests": parsed.total_tests,
                "passedTests": parsed.passed_tests,
                "failedTests": parsed.failed_tests,
                "duration": float(duration),
            },
        )
        return rows[0] if rows else {}

    def add_tests(self, simulation_id: str, tests: List[TestResult]) -> None:
        """Create every Test node -- passed AND failed -- in one round trip."""
        if not tests:
            return
        self.client.run(
            """
            MATCH (s:Simulation {simulationId: $simulationId})
            UNWIND $tests AS t
              MERGE (n:Test {testId: t.testId})
              SET   n.name     = t.name,
                    n.status   = t.status,
                    n.expected = t.expected,
                    n.actual   = t.actual,
                    n.message  = t.message,
                    n.number   = t.number
              MERGE (s)-[:HAS_TEST]->(n)
            """,
            {
                "simulationId": simulation_id,
                "tests": [
                    {
                        # scope the id to the simulation so reruns do not collide
                        "testId": f"{simulation_id}:{t.test_id}",
                        "name": t.name,
                        "status": t.status.value,
                        "expected": t.expected,
                        "actual": t.actual,
                        "message": t.message,
                        "number": t.test_number,
                    }
                    for t in tests
                ],
            },
        )

    def add_failures(
        self, simulation_id: str, failures: List[FailureInfo]
    ) -> None:
        if not failures:
            return
        self.client.run(
            """
            MATCH (s:Simulation {simulationId: $simulationId})
            UNWIND $failures AS f
              MERGE (n:Failure {failureId: f.failureId})
              SET   n.category = f.category,
                    n.severity = f.severity,
                    n.expected = f.expected,
                    n.actual   = f.actual,
                    n.message  = f.message,
                    n.testId   = f.testId,
                    n.testName = f.testName
              MERGE (s)-[:HAS_FAILURE]->(n)
            """,
            {
                "simulationId": simulation_id,
                "failures": [
                    {
                        "failureId": f.failure_id,
                        "category": f.category.value,
                        "severity": f.severity.value,
                        "expected": f.expected,
                        "actual": f.actual,
                        "message": f.message,
                        "testId": f.test_id,
                        "testName": f.test_name,
                    }
                    for f in failures
                ],
            },
        )

    def add_waveform(
        self, simulation_id: str, waveform_id: str, file_name: str, file_path: str
    ) -> None:
        self.client.run(
            """
            MATCH (s:Simulation {simulationId: $simulationId})
            MERGE (w:Waveform {waveformId: $waveformId})
            SET   w.fileName = $fileName,
                  w.filePath = $filePath
            MERGE (s)-[:GENERATED]->(w)
            """,
            {
                "simulationId": simulation_id,
                "waveformId": waveform_id,
                "fileName": file_name,
                "filePath": file_path,
            },
        )

    # =================================================================
    # AIAnalysis
    # =================================================================
    def add_ai_analysis(
        self, failure_id: str, analysis_id: str, analysis: AIAnalysis
    ) -> None:
        self.client.run(
            """
            MATCH (f:Failure {failureId: $failureId})
            MERGE (a:AIAnalysis {analysisId: $analysisId})
            SET   a.rootCause      = $rootCause,
                  a.explanation    = $explanation,
                  a.recommendation = $recommendation,
                  a.confidence     = $confidence,
                  a.createdAt      = $createdAt
            MERGE (f)-[:ANALYZED_BY]->(a)
            """,
            {
                "failureId": failure_id,
                "analysisId": analysis_id,
                "rootCause": analysis.rootCause,
                "explanation": analysis.explanation,
                "recommendation": analysis.recommendation,
                "confidence": float(analysis.confidence),
                "createdAt": utcnow_iso(),
            },
        )

    # =================================================================
    # Reads used by GraphQL
    # =================================================================
    def get_verification_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Everything the UI needs for one job, in a single query."""
        rows = self.client.run(
            """
            MATCH (p:Project)-[:HAS_JOB]->(j:VerificationJob {jobId: $jobId})
            OPTIONAL MATCH (j)-[:USES_RTL]->(r:RTLModule)
            OPTIONAL MATCH (j)-[:USES_TESTBENCH]->(tb:Testbench)
            OPTIONAL MATCH (j)-[:PRODUCED]->(s:Simulation)
            OPTIONAL MATCH (s)-[:GENERATED]->(w:Waveform)
            WITH p, j, r, tb, s, w
            OPTIONAL MATCH (s)-[:HAS_TEST]->(t:Test)
            WITH p, j, r, tb, s, w,
                 [x IN collect(DISTINCT t) | {
                     testId:   x.testId,
                     number:   x.number,
                     name:     x.name,
                     status:   x.status,
                     expected: x.expected,
                     actual:   x.actual,
                     message:  x.message
                 }] AS tests
            OPTIONAL MATCH (s)-[:HAS_FAILURE]->(f:Failure)
            OPTIONAL MATCH (f)-[:ANALYZED_BY]->(a:AIAnalysis)
            WITH p, j, r, tb, s, w, tests,
                 collect(DISTINCT {
                     failureId: f.failureId,
                     category:  f.category,
                     severity:  f.severity,
                     expected:  f.expected,
                     actual:    f.actual,
                     message:   f.message,
                     testId:    f.testId,
                     testName:  f.testName
                 }) AS rawFailures,
                 collect(DISTINCT {
                     analysisId:     a.analysisId,
                     rootCause:      a.rootCause,
                     explanation:    a.explanation,
                     recommendation: a.recommendation,
                     confidence:     a.confidence,
                     createdAt:      a.createdAt
                 }) AS rawAnalyses
            RETURN
                p.projectId    AS projectId,
                p.name         AS projectName,
                j.jobId        AS jobId,
                j.status       AS status,
                j.progress     AS progress,
                j.createdAt    AS createdAt,
                j.completedAt  AS completedAt,
                j.errorMessage AS errorMessage,
                j.example      AS example,
                j.scenario     AS scenario,
                r.moduleName   AS rtlModuleName,
                r.fileName     AS rtlFileName,
                r.filePath     AS rtlFilePath,
                tb.fileName    AS testbenchFileName,
                tb.filePath    AS testbenchFilePath,
                s.simulationId AS simulationId,
                s.status       AS simulationStatus,
                s.totalTests   AS totalTests,
                s.passedTests  AS passedTests,
                s.failedTests  AS failedTests,
                s.duration     AS duration,
                w.fileName     AS waveformFileName,
                w.filePath     AS waveformFilePath,
                tests          AS tests,
                [x IN rawFailures  WHERE x.failureId  IS NOT NULL] AS failures,
                [x IN rawAnalyses  WHERE x.analysisId IS NOT NULL] AS aiAnalyses
            """,
            {"jobId": job_id},
        )
        return rows[0] if rows else None

    def get_failures(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if job_id:
            return self.client.run(
                """
                MATCH (j:VerificationJob {jobId: $jobId})-[:PRODUCED]->
                      (:Simulation)-[:HAS_FAILURE]->(f:Failure)
                RETURN f.failureId AS failureId, f.category AS category,
                       f.severity  AS severity,  f.expected AS expected,
                       f.actual    AS actual,    f.message  AS message,
                       f.testId    AS testId,    f.testName AS testName
                ORDER BY f.testId
                """,
                {"jobId": job_id},
            )
        return self.client.run(
            """
            MATCH (f:Failure)
            RETURN f.failureId AS failureId, f.category AS category,
                   f.severity  AS severity,  f.expected AS expected,
                   f.actual    AS actual,    f.message  AS message,
                   f.testId    AS testId,    f.testName AS testName
            LIMIT 200
            """
        )

    def get_ai_analysis(self, job_id: str) -> List[Dict[str, Any]]:
        return self.client.run(
            """
            MATCH (j:VerificationJob {jobId: $jobId})-[:PRODUCED]->
                  (:Simulation)-[:HAS_FAILURE]->(f:Failure)
                  -[:ANALYZED_BY]->(a:AIAnalysis)
            RETURN a.analysisId     AS analysisId,
                   a.rootCause      AS rootCause,
                   a.explanation    AS explanation,
                   a.recommendation AS recommendation,
                   a.confidence     AS confidence,
                   a.createdAt      AS createdAt,
                   f.failureId      AS failureId,
                   f.category       AS category
            """,
            {"jobId": job_id},
        )

    # =================================================================
    # Traceability
    # =================================================================
    def trace_job(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Full chain:
          Project -> RTLModule -> Testbench -> VerificationJob ->
          Simulation -> Test -> Failure -> AIAnalysis

        Returns one row per (failure, analysis) pair, or a single row with
        nulls when the run passed.
        """
        return self.client.run(
            """
            MATCH (p:Project)-[:HAS_JOB]->(j:VerificationJob {jobId: $jobId})
            OPTIONAL MATCH (j)-[:USES_RTL]->(r:RTLModule)
            OPTIONAL MATCH (j)-[:USES_TESTBENCH]->(tb:Testbench)
            OPTIONAL MATCH (j)-[:PRODUCED]->(s:Simulation)
            OPTIONAL MATCH (s)-[:HAS_FAILURE]->(f:Failure)
            OPTIONAL MATCH (f)-[:ANALYZED_BY]->(a:AIAnalysis)
            OPTIONAL MATCH (s)-[:HAS_TEST]->(t:Test)
                      WHERE f IS NOT NULL AND t.testId ENDS WITH f.testId
            RETURN p.name         AS project,
                   r.moduleName   AS rtlModule,
                   r.fileName     AS rtlFile,
                   tb.fileName    AS testbench,
                   j.jobId        AS job,
                   j.status       AS jobStatus,
                   s.simulationId AS simulation,
                   s.status       AS simulationStatus,
                   t.name         AS test,
                   t.status       AS testStatus,
                   f.category     AS failureCategory,
                   f.severity     AS failureSeverity,
                   a.rootCause    AS aiRootCause,
                   a.confidence   AS aiConfidence
            ORDER BY f.testId
            """,
            {"jobId": job_id},
        )


neo4j_service = Neo4jService()
