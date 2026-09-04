from backend.config import MOCK_EDA
from backend.eda.base import MockAdapter
from backend.eda.shell import run_command
class OpenLane:
    async def physical_design(self,workspace):
        if MOCK_EDA: return await MockAdapter('MOCK: OpenLane/OpenROAD passed',{'floorplan':'pass','placement':'pass','cts':'pass','routing':'pass'}).run(workspace)
        return await run_command(['openlane','config.json'],workspace,1800)
    async def physical_verification(self,workspace):
        if MOCK_EDA: return await MockAdapter('MOCK: DRC/LVS passed',{'drc':'pass','lvs':'pass'}).run(workspace)
        return await run_command(['bash','verify.sh'],workspace,1800)
