from backend.config import MOCK_EDA
from backend.eda.base import MockAdapter
from backend.eda.shell import run_command
class Yosys:
    async def run(self,workspace):
        if MOCK_EDA: return await MockAdapter('MOCK: Yosys synthesis passed',{'cell_count':34,'area':1234.0}).run(workspace)
        return await run_command(['yosys','-s','synthesis.ys'],workspace,300)
