import os,sys
from pathlib import Path
sys.path.insert(0,str(Path('backend').resolve()));os.environ['DJANGO_SETTINGS_MODULE']='config.settings'
import django
django.setup()
from trips.providers import routes
r,w=routes([-87.6298,41.8781],[-86.1581,39.7684]);print('Chicago to Indianapolis',len(r),'distinct routes',[(x['provider'],round(x['distance_meters']/1609.344,1)) for x in r],w)
