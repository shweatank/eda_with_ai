"""
Inspect the Neo4j verification graph from the terminal.

    python scripts/show_graph.py              # summary + recent jobs
    python scripts/show_graph.py <jobId>      # full trace for one job

A convenience view of the same data the Neo4j Browser shows -- handy when
you want the numbers without leaving the terminal.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import settings                       # noqa: E402
from backend.database.neo4j_client import neo4j_client    # noqa: E402

NODE_LABELS = [
    "Project", "RTLModule", "Testbench", "VerificationJob",
    "Simulation", "Test", "Failure", "Waveform", "AIAnalysis",
]
REL_TYPES = [
    "HAS_RTL", "HAS_TESTBENCH", "HAS_JOB", "USES_RTL", "USES_TESTBENCH",
    "PRODUCED", "HAS_TEST", "HAS_FAILURE", "GENERATED", "ANALYZED_BY",
]


def rule(title: str) -> None:
    print(f"\n{title}\n{'=' * len(title)}")


def summary() -> None:
    rule("NODES")
    for label in NODE_LABELS:
        count = neo4j_client.run(
            f"MATCH (n:{label}) RETURN count(n) AS n"
        )[0]["n"]
        print(f"  {label:<18} {count:>5}")

    rule("RELATIONSHIPS")
    for rel in REL_TYPES:
        count = neo4j_client.run(
            f"MATCH ()-[r:{rel}]->() RETURN count(r) AS n"
        )[0]["n"]
        print(f"  {rel:<18} {count:>5}")

    rule("PROJECTS")
    for row in neo4j_client.run(
        "MATCH (p:Project) RETURN p.projectId AS id, p.name AS name "
        "ORDER BY p.createdAt DESC"
    ):
        print(f"  {row['id']:<8} {row['name']}")

    rule("10 MOST RECENT VERIFICATION JOBS")
    print(f"  {'JOB ID':<20} {'EXAMPLE':<15} {'SCENARIO':<9} "
          f"{'PASS':>4} {'FAIL':>4}  STATUS")
    for row in neo4j_client.run(
        """
        MATCH (j:VerificationJob)-[:PRODUCED]->(s:Simulation)
        RETURN j.jobId AS job, j.example AS example, j.scenario AS scenario,
               s.passedTests AS passed, s.failedTests AS failed,
               s.status AS status
        ORDER BY j.createdAt DESC LIMIT 10
        """
    ):
        print(
            f"  {row['job']:<20} {row['example'] or '?':<15} "
            f"{row['scenario'] or '?':<9} {row['passed']:>4} "
            f"{row['failed']:>4}  {row['status']}"
        )

    rule("FAILURE CATEGORIES SEEN")
    for row in neo4j_client.run(
        "MATCH (f:Failure) RETURN f.category AS category, "
        "f.severity AS severity, count(*) AS n ORDER BY n DESC"
    ):
        print(f"  {row['category']:<20} {row['severity']:<10} {row['n']:>4}")

    print("\nRun `python scripts/show_graph.py <jobId>` for a full trace.")


def trace(job_id: str) -> None:
    rows = neo4j_client.run(
        """
        MATCH (p:Project)-[:HAS_JOB]->(j:VerificationJob {jobId: $jobId})
        OPTIONAL MATCH (j)-[:USES_RTL]->(r:RTLModule)
        OPTIONAL MATCH (j)-[:USES_TESTBENCH]->(tb:Testbench)
        OPTIONAL MATCH (j)-[:PRODUCED]->(s:Simulation)
        OPTIONAL MATCH (s)-[:GENERATED]->(w:Waveform)
        RETURN p.name AS project, r.moduleName AS module, r.fileName AS rtl,
               tb.fileName AS testbench, j.status AS jobStatus,
               s.simulationId AS sim, s.status AS simStatus,
               s.totalTests AS total, s.passedTests AS passed,
               s.failedTests AS failed, w.filePath AS waveform
        """,
        {"jobId": job_id},
    )
    if not rows:
        print(f"No job found with id {job_id!r}.")
        return
    row = rows[0]

    rule(f"TRACE FOR {job_id}")
    print(f"  Project          : {row['project']}")
    print(f"        ↓")
    print(f"  RTL Module       : {row['module']} ({row['rtl']})")
    print(f"        ↓")
    print(f"  Testbench        : {row['testbench']}")
    print(f"        ↓")
    print(f"  Verification Job : {job_id}  [{row['jobStatus']}]")
    print(f"        ↓")
    print(f"  Simulation       : {row['sim']}  [{row['simStatus']}]  "
          f"{row['passed']}/{row['total']} passed")

    print(f"        ↓")
    print(f"  Tests:")
    for t in neo4j_client.run(
        """
        MATCH (:VerificationJob {jobId: $jobId})-[:PRODUCED]->
              (:Simulation)-[:HAS_TEST]->(t:Test)
        RETURN t.number AS number, t.name AS name, t.status AS status,
               t.expected AS expected, t.actual AS actual
        ORDER BY t.number
        """,
        {"jobId": job_id},
    ):
        mark = "✓" if t["status"] == "PASS" else "✗"
        detail = (
            "" if t["status"] == "PASS"
            else f"   expected={t['expected']} actual={t['actual']}"
        )
        print(f"    {mark} TEST_{t['number']} {t['name']} — "
              f"{t['status']}{detail}")

    failures = neo4j_client.run(
        """
        MATCH (:VerificationJob {jobId: $jobId})-[:PRODUCED]->
              (:Simulation)-[:HAS_FAILURE]->(f:Failure)
        OPTIONAL MATCH (f)-[:ANALYZED_BY]->(a:AIAnalysis)
        RETURN f.category AS category, f.severity AS severity,
               f.expected AS expected, f.actual AS actual,
               a.rootCause AS rootCause, a.recommendation AS recommendation,
               a.confidence AS confidence
        """,
        {"jobId": job_id},
    )
    print(f"        ↓")
    if not failures:
        print("  Failure          : none")
        print(f"        ↓")
        print("  AI Analysis      : not required (no failures)")
    else:
        for f in failures:
            print(f"  Failure          : {f['category']} / {f['severity']}"
                  f"   expected={f['expected']} actual={f['actual']}")
            print(f"        ↓")
            print(f"  AI Analysis      : {f['rootCause']}")
            print(f"    recommendation : {f['recommendation']}")
            print(f"    confidence     : {f['confidence']}")
            print()

    if row["waveform"]:
        print(f"  Waveform         : {row['waveform']}")
        print(f"                     open with: gtkwave {row['waveform']}")


def main() -> int:
    if not neo4j_client.connect():
        print(f"Could not connect to Neo4j: {neo4j_client.last_error}")
        print("Check NEO4J_* in your .env file.")
        return 1
    print(f"Connected to {settings.NEO4J_URI} "
          f"(database={settings.NEO4J_DATABASE})")
    try:
        if len(sys.argv) > 1:
            trace(sys.argv[1])
        else:
            summary()
    finally:
        neo4j_client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
