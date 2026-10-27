from pathlib import Path
import json,urllib.request,urllib.error
keys=dict(line.strip().split('=',1) for line in Path('backend/.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
body={'coordinates':[[-87.6298,41.8781],[-86.1581,39.7684]],'alternative_routes':{'target_count':3}}
req=urllib.request.Request('https://api.openrouteservice.org/v2/directions/driving-hgv/geojson',data=json.dumps(body).encode(),headers={'Authorization':keys['ORS_API_KEY'],'Content-Type':'application/json'})
try:
 with urllib.request.urlopen(req,timeout=40) as r:print('status',r.status,'rate limit',r.headers.get('X-Ratelimit-Limit'));print('routes',len(json.load(r)['features']))
except urllib.error.HTTPError as e:print(e.code,'rate limit',e.headers.get('X-Ratelimit-Limit'),e.read().decode()[:1000])
