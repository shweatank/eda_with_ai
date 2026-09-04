from backend.config import PLANNER_MODEL
from backend.agent.llm import OllamaClient,parse_json
from backend.agent.prompts import PLANNER_SYSTEM
class Planner:
    def __init__(self): self.llm=OllamaClient(PLANNER_MODEL)
    async def plan(self,request): return parse_json(await self.llm.chat(PLANNER_SYSTEM,request))
