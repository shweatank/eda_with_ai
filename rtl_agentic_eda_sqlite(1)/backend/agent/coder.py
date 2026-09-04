from backend.config import CODER_MODEL
from backend.agent.llm import OllamaClient,strip_fences
from backend.agent.prompts import CODER_SYSTEM,TB_SYSTEM
class Coder:
    def __init__(self): self.llm=OllamaClient(CODER_MODEL)
    async def rtl(self,plan,request): return strip_fences(await self.llm.chat(CODER_SYSTEM,f'Request:\n{request}\nPlan:\n{plan}'))
    async def testbench(self,plan,rtl): return strip_fences(await self.llm.chat(TB_SYSTEM,f'Plan:\n{plan}\nRTL:\n{rtl}'))
    async def repair(self,target,artifact,diagnosis,log):
        system=CODER_SYSTEM if target=='rtl' else TB_SYSTEM
        return strip_fences(await self.llm.chat(system,f'Target:{target}\nDiagnosis:{diagnosis}\nArtifact:\n{artifact}\nFailure log:\n{log}\nReturn complete corrected artifact.'))
