"""Strawberry GraphQL types -- the wire format of the platform."""
from __future__ import annotations

from typing import List, Optional

import strawberry


@strawberry.type
class ProjectType:
    projectId: str
    name: str
    description: str = ""
    createdAt: str = ""


@strawberry.type
class RTLModuleType:
    rtlId: str
    moduleName: str
    fileName: str
    filePath: str


@strawberry.type
class TestbenchType:
    testbenchId: str
    fileName: str
    filePath: str


@strawberry.type
class VerificationJobType:
    jobId: str
    status: str
    progress: int
    createdAt: str = ""
    completedAt: Optional[str] = None
    errorMessage: Optional[str] = None
    example: str = ""
    scenario: str = ""


@strawberry.type
class SimulationType:
    simulationId: str
    status: str
    totalTests: int
    passedTests: int
    failedTests: int
    duration: float


@strawberry.type
class TestType:
    testId: str
    name: str
    status: str
    expected: str = ""
    actual: str = ""
    message: str = ""


@strawberry.type
class FailureType:
    failureId: str
    category: str
    severity: str
    expected: str = ""
    actual: str = ""
    message: str = ""
    testId: str = ""
    testName: str = ""


@strawberry.type
class WaveformType:
    waveformId: str
    fileName: str
    filePath: str


@strawberry.type
class AIAnalysisType:
    analysisId: str
    rootCause: str
    explanation: str
    recommendation: str
    confidence: float
    createdAt: str = ""
    failureId: str = ""
    category: str = ""


@strawberry.type
class TraceStepType:
    """One hop of the Neo4j traceability chain, ready to render."""
    level: int
    label: str
    value: str


@strawberry.type
class VerificationResultType:
    jobId: str
    projectId: str
    projectName: str = ""
    example: str = ""
    scenario: str = ""
    status: str = "QUEUED"
    progress: int = 0
    errorMessage: Optional[str] = None

    rtlModule: Optional[RTLModuleType] = None
    testbench: Optional[TestbenchType] = None
    simulation: Optional[SimulationType] = None
    waveform: Optional[WaveformType] = None

    tests: List[TestType] = strawberry.field(default_factory=list)
    failures: List[FailureType] = strawberry.field(default_factory=list)
    aiAnalyses: List[AIAnalysisType] = strawberry.field(default_factory=list)
    traceability: List[TraceStepType] = strawberry.field(default_factory=list)

    simulationLog: str = ""


@strawberry.type
class HealthType:
    status: str
    neo4j: str
    groq: str
    iverilog: str
