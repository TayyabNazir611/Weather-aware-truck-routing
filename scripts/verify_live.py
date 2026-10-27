import os,sys,json
from pathlib import Path
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(Path('backend').resolve())); os.environ['DJANGO_SETTINGS_MODULE']='config.settings'
import django
django.setup()
from trips.service import analyze_trip
from trips.providers import routes
r,w=routes([-87.6298,41.8781],[-87.3311,41.4731]); print('Distinct routes',len(r),[(x['provider'],x['distance_meters']) for x in r],w,flush=True)
data=analyze_trip({'origin':{'coordinates':[-87.6298,41.8781]},'destination':{'coordinates':[-87.3311,41.4731]},'departure':datetime.now(timezone.utc)+timedelta(hours=2),'load_lb':35000,'interval_miles':10})
Path('tmp/live-analysis.json').write_text(json.dumps(data)); print('Complete analysis',len(data['routes']),data['recommended_id'],len(data['heatmap']['points']),data['warnings'],flush=True)
