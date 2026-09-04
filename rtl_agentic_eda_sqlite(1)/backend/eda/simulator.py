from backend.config import MOCK_EDA
from backend.eda.base import MockAdapter
from backend.eda.shell import run_command
class Simulator:
    async def run(self,workspace):
        if MOCK_EDA: return await MockAdapter('MOCK: 32 tests passed',{'tests':32,'passed':32,'failed':0}).run(workspace)
        return await run_command(['pytest','-q','-s'],workspace,300)
