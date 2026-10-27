from pathlib import Path
import json
p=Path('tmp/live-analysis.json'); data=json.loads(p.read_text()); data['mode']='demo'; Path('frontend/public').mkdir(exist_ok=True); Path('frontend/public/demo.json').write_text(json.dumps(data,separators=(',',':')))
p=Path('tmp/ors-probe.json'); d=json.loads(p.read_text()); print('Probe points', [len(f['geometry']['coordinates']) for f in d['features']]); print('Recorded demo',len(data['routes']),'routes',len(data['heatmap']['points']),'corridor samples')
