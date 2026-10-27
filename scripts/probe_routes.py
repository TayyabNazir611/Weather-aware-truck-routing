import json,urllib.request,urllib.error
from pathlib import Path
keys=dict(line.strip().split('=',1) for line in Path('backend/.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
body={'coordinates':[[-87.6298,41.8781],[-87.3311,41.4731]],'alternative_routes':{'target_count':3,'share_factor':0.8,'weight_factor':1.8},'instructions':True}
req=urllib.request.Request('https://api.openrouteservice.org/v2/directions/driving-hgv/geojson',data=json.dumps(body).encode(),headers={'Authorization':keys['ORS_API_KEY'],'Content-Type':'application/json'})
try:
 with urllib.request.urlopen(req,timeout=40) as r: data=json.load(r)
 Path('tmp/ors-probe.json').write_text(json.dumps(data)); print('ORS genuine HGV routes:',len(data.get('features',[]))); print([f['properties']['summary'] for f in data.get('features',[])])
except urllib.error.HTTPError as e: print('ORS HTTP',e.code,e.read().decode()[:1500])
except Exception as e: print(type(e).__name__)
