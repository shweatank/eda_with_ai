from pathlib import Path
import json,html
def build_report(state,summary=''):
    return {'job_id':state.job_id,'prompt':state.prompt,'status':state.status,'plan':state.plan,'steps':{n:{'status':s.status,'attempts':s.attempts,'metrics':s.metrics,'error':s.error,'output':s.output[-4000:]} for n,s in state.steps.items()},'artifacts':state.artifacts,'repair_history':state.repair_history,'review':summary}
def write_report(workspace,report):
    d=workspace/'reports'; d.mkdir(parents=True,exist_ok=True); (d/'report.json').write_text(json.dumps(report,indent=2))
    rows=''.join(f"<tr><td>{html.escape(n)}</td><td>{html.escape(v['status'])}</td><td>{v['attempts']}</td><td><pre>{html.escape(v['output'])}</pre></td></tr>" for n,v in report['steps'].items())
    page=f'''<!doctype html><meta charset="utf-8"><title>RTL Agent Report</title><style>body{{font-family:Arial;max-width:1200px;margin:40px auto}}table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:8px;vertical-align:top}}pre{{white-space:pre-wrap}}</style><h1>RTL Agent Report</h1><p>Status: {html.escape(report['status'])}</p><h2>Request</h2><pre>{html.escape(report['prompt'])}</pre><h2>Steps</h2><table><tr><th>Step</th><th>Status</th><th>Attempts</th><th>Output</th></tr>{rows}</table><h2>Repair history</h2><pre>{html.escape(json.dumps(report['repair_history'],indent=2))}</pre><h2>Reviewer</h2><pre>{html.escape(report['review'])}</pre>'''
    (d/'report.html').write_text(page)
