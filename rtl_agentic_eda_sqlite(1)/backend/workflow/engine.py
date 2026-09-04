import json
from datetime import datetime, timezone

from backend.config import WORKSPACE_ROOT, MAX_RETRIES, REVIEWER_MODEL
from backend.db import init_db, save_snapshot
from backend.workflow.models import JobState, StepResult
from backend.workflow.events import event_bus
from backend.agent.planner import Planner
from backend.agent.coder import Coder
from backend.agent.reviewer import Reviewer
from backend.agent.llm import OllamaClient, parse_json
from backend.agent.prompts import DEBUG_SYSTEM
from backend.eda.simulator import Simulator
from backend.eda.yosys import Yosys
from backend.eda.opensta import OpenSTA
from backend.eda.openlane import OpenLane
from backend.reports.generator import build_report, write_report

init_db()


class WorkflowEngine:
    def __init__(self, job_id):
        self.state = JobState(job_id, '')
        self.workspace = WORKSPACE_ROOT / job_id
        self.planner = Planner()
        self.coder = Coder()
        self.reviewer = Reviewer()
        self.debugger = OllamaClient(REVIEWER_MODEL)
        self.simulator = Simulator()
        self.yosys = Yosys()
        self.sta = OpenSTA()
        self.openlane = OpenLane()

    def snapshot(self):
        return {
            'job_id': self.state.job_id,
            'prompt': self.state.prompt,
            'status': self.state.status,
            'plan': self.state.plan,
            'steps': {k: vars(v) for k, v in self.state.steps.items()},
            'artifacts': self.state.artifacts,
            'repair_history': self.state.repair_history,
            'report': self.state.report,
        }

    def persist(self):
        save_snapshot(self.snapshot(), datetime.now(timezone.utc).isoformat())

    async def emit(self, event_type, **data):
        self.persist()
        await event_bus.emit(self.state.job_id, event_type, **data)
        self.persist()

    async def write(self, rel, text):
        p = self.workspace / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
        self.state.artifacts[rel] = str(p)
        self.persist()
        return p

    async def run(self, prompt):
        self.state.prompt = prompt
        self.state.status = 'planning'
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.persist()
        await self.emit('pipeline_started', prompt=prompt)
        try:
            await self.emit('step_started', step='planning')
            self.state.plan = await self.planner.plan(prompt)
            await self.write('plan.json', json.dumps(self.state.plan, indent=2))
            self.state.status = 'running'
            await self.emit('step_completed', step='planning', status='passed', result=self.state.plan)

            rtl = await self.generate('rtl', lambda: self.coder.rtl(self.state.plan, prompt), 'rtl/design.sv')
            if rtl is None:
                return await self.fail('rtl')
            tb = await self.generate('testbench', lambda: self.coder.testbench(self.state.plan, rtl), 'testbench/test_design.py')
            if tb is None:
                return await self.fail('testbench')

            for name, runner in [
                ('simulation', self.simulator.run),
                ('synthesis', self.yosys.run),
                ('sta', self.sta.run),
                ('physical_design', self.openlane.physical_design),
                ('physical_verification', self.openlane.physical_verification),
            ]:
                if name == 'synthesis':
                    await self.write('synthesis.ys', f"read_verilog -sv rtl/design.sv\nhierarchy -top {self.state.plan.get('top_module','top')}\nproc; opt; memory; opt; techmap; opt; abc; clean\nwrite_verilog synthesized.v\nwrite_json synthesized.json\nstat\n")
                if name == 'sta':
                    await self.write('sta.tcl', f"# Configure Liberty and SDC for your PDK.\n# read_liberty <technology_library>.lib\nread_verilog synthesized.v\nlink_design {self.state.plan.get('top_module','top')}\n# read_sdc constraints.sdc\nreport_checks\nreport_wns\nreport_tns\nexit\n")
                if not await self.tool(name, runner):
                    return await self.fail(name)

            self.state.status = 'completed'
            self.state.report = build_report(self.state, await self.reviewer.summarize(self.snapshot()))
            write_report(self.workspace, self.state.report)
            self.persist()
            await self.emit('pipeline_completed', report=self.state.report)
        except Exception as e:
            self.state.status = 'failed'
            self.state.report = build_report(self.state, f'Unhandled exception: {e}')
            write_report(self.workspace, self.state.report)
            self.persist()
            await self.emit('pipeline_failed', error=str(e), report=self.state.report)

    async def debug(self, stage, error, log):
        try:
            return parse_json(await self.debugger.chat(DEBUG_SYSTEM, f'Stage:{stage}\nFailure:{error}\nLog:\n{log}'))
        except Exception:
            return {'diagnosis': error, 'target': 'flow', 'patch_instructions': 'Inspect the tool log.'}

    async def generate(self, name, fn, rel):
        s = self.state.steps.setdefault(name, StepResult(name))
        for attempt in range(1, MAX_RETRIES + 1):
            s.attempts = attempt
            s.start()
            self.persist()
            await self.emit('step_started', step=name, attempt=attempt)
            try:
                x = await fn()
                await self.write(rel, x)
                s.finish(True, 'Generated successfully')
                self.persist()
                await self.emit('step_completed', step=name, status='passed', attempt=attempt)
                return x
            except Exception as e:
                s.finish(False, error=str(e))
                d = await self.debug(name, str(e), '')
                self.state.repair_history.append({'stage': name, 'attempt': attempt, 'diagnosis': d})
                self.persist()
                await self.emit('agent_repair', step=name, attempt=attempt, diagnosis=d)
        return None

    async def tool(self, name, runner):
        s = self.state.steps.setdefault(name, StepResult(name))
        for attempt in range(1, MAX_RETRIES + 1):
            s.attempts = attempt
            s.start()
            self.persist()
            await self.emit('step_started', step=name, attempt=attempt)
            out = await runner(self.workspace)
            s.finish(
                out['success'],
                out.get('output', ''),
                out.get('metrics', {}),
                None if out['success'] else out.get('output', ''),
            )
            self.persist()
            if out['success']:
                await self.emit('step_completed', step=name, status='passed', attempt=attempt, metrics=s.metrics, output=s.output[-3000:])
                return True
            await self.emit('step_failed', step=name, attempt=attempt, error=s.error, output=s.output[-3000:])
            d = await self.debug(name, s.error or s.output, s.output)
            self.state.repair_history.append({'stage': name, 'attempt': attempt, 'diagnosis': d})
            self.persist()
            await self.emit('agent_repair', step=name, attempt=attempt, diagnosis=d)
        return False

    async def fail(self, stage):
        self.state.status = 'failed'
        self.state.report = build_report(self.state, f'Pipeline stopped at {stage}.')
        write_report(self.workspace, self.state.report)
        self.persist()
        await self.emit('pipeline_failed', failed_step=stage, report=self.state.report)
