import asyncio
async def run_command(command,cwd,timeout=300):
    p=await asyncio.create_subprocess_exec(*command,cwd=str(cwd),stdout=asyncio.subprocess.PIPE,stderr=asyncio.STDOUT)
    lines=[]
    try:
        while True:
            line=await p.stdout.readline()
            if not line: break
            lines.append(line.decode(errors='replace').rstrip())
        code=await asyncio.wait_for(p.wait(),timeout)
    except asyncio.TimeoutError:
        p.kill(); await p.wait(); return {'success':False,'return_code':-1,'output':'TIMEOUT\n'+'\n'.join(lines),'metrics':{}}
    return {'success':code==0,'return_code':code,'output':'\n'.join(lines),'metrics':{}}
