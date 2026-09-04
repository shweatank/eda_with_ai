import json,httpx
from backend.config import OLLAMA_BASE_URL
class OllamaClient:
    def __init__(self,model): self.model=model
    async def chat(self,system,prompt):
        payload={'model':self.model,'messages':[{'role':'system','content':system},{'role':'user','content':prompt}],'stream':False,'options':{'temperature':0.1}}
        async with httpx.AsyncClient(timeout=900) as c:
            r=await c.post(f'{OLLAMA_BASE_URL}/api/chat',json=payload); r.raise_for_status(); return r.json()['message']['content']
def strip_fences(t):
    t=t.strip()
    if t.startswith('```'):
        x=t.splitlines()[1:]
        if x and x[-1].strip()=='```': x=x[:-1]
        return '\n'.join(x)
    return t
def parse_json(t): return json.loads(strip_fences(t))
