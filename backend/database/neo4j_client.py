"""
Neo4j AuraDB driver lifecycle.

A single driver instance is shared by the whole application. It is opened
when FastAPI starts and closed on shutdown.
"""
from __future__ import annotations

import logging
import threading
from typing import Any, Dict, List, Optional

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from backend.config import settings

log = logging.getLogger(__name__)


class Neo4jClient:
    """Thin, thread-safe wrapper around the official Neo4j Python driver."""

    def __init__(self) -> None:
        self._driver: Optional[Driver] = None
        self._lock = threading.Lock()
        self._last_error: Optional[str] = None

    # ------------------------------------------------------------- lifecycle
    def connect(self) -> bool:
        """Open and verify the driver. Returns True on success."""
        with self._lock:
            if self._driver is not None:
                return True

            if not settings.neo4j_configured:
                self._last_error = (
                    "NEO4J_URI / NEO4J_PASSWORD are not set. Copy .env.example "
                    "to .env and fill in your AuraDB credentials."
                )
                log.error("Neo4j not configured: %s", self._last_error)
                return False

            try:
                driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
                    max_connection_lifetime=3600,
                )
                driver.verify_connectivity()
            except Exception as exc:
                # Never echo the password back into a log or an API response.
                self._last_error = f"{type(exc).__name__}: {self._scrub(str(exc))}"
                log.error("Neo4j connection failed: %s", self._last_error)
                self._driver = None
                return False

            self._driver = driver
            self._last_error = None
            log.info(
                "Connected to Neo4j at %s (database=%s)",
                settings.NEO4J_URI,
                settings.NEO4J_DATABASE,
            )
            return True

    def close(self) -> None:
        with self._lock:
            if self._driver is not None:
                try:
                    self._driver.close()
                    log.info("Neo4j driver closed")
                except Exception as exc:                     # pragma: no cover
                    log.warning("Error closing Neo4j driver: %s", exc)
                finally:
                    self._driver = None

    # ------------------------------------------------------------- health
    @property
    def connected(self) -> bool:
        return self._driver is not None

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    def health(self) -> str:
        """
        Return "connected" / "disconnected" for the /health endpoint.

        AuraDB drops idle connections, so the first probe after a quiet
        spell can hit a defunct pooled connection. That is not an outage:
        the driver simply discards it and dials again. We therefore retry
        once before declaring the database down.
        """
        if self._driver is None:
            return "disconnected"

        last_exc: Optional[Exception] = None
        for _ in range(2):
            try:
                self.run("RETURN 1 AS ok")
                self._last_error = None
                return "connected"
            except Exception as exc:
                last_exc = exc

        self._last_error = (
            f"{type(last_exc).__name__}: {self._scrub(str(last_exc))}"
        )
        return "disconnected"

    # ------------------------------------------------------------- queries
    def run(
        self, cypher: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a *parameterised* Cypher statement and materialise the rows.

        All call sites pass values via ``parameters`` -- no string
        interpolation into Cypher anywhere in this project.
        """
        if self._driver is None:
            if not self.connect():
                raise ConnectionError(
                    self._last_error or "Neo4j driver is not connected"
                )

        assert self._driver is not None
        try:
            with self._driver.session(database=settings.NEO4J_DATABASE) as session:
                result = session.run(cypher, parameters or {})
                return [record.data() for record in result]
        except (ServiceUnavailable, Neo4jError) as exc:
            self._last_error = f"{type(exc).__name__}: {self._scrub(str(exc))}"
            raise

    # ------------------------------------------------------------- helpers
    @staticmethod
    def _scrub(text: str) -> str:
        """Remove anything that could be a credential from an error string."""
        out = text
        for secret in (settings.NEO4J_PASSWORD, settings.GROQ_API_KEY):
            if secret:
                out = out.replace(secret, "***")
        return out


# module-level singleton used across the app
neo4j_client = Neo4jClient()
