"""Assemble the Strawberry schema served at /graphql."""
from __future__ import annotations

import strawberry

from backend.graphql.mutations import Mutation
from backend.graphql.queries import Query

schema = strawberry.Schema(query=Query, mutation=Mutation)
