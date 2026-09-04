from backend.config import MOCK_EDA
from backend.eda.base import MockAdapter
from backend.eda.shell import run_command
class OpenSTA:
    async def run(self,workspace):
        if MOCK_EDA: return await MockAdapter('MOCK: OpenSTA passed',{'wns_ns':0.42,'tns_ns':0.0}).run(workspace)
        return await run_command(['sta','sta.tcl'],workspace,300)
