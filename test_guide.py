"""Deterministic offline checks for the published guide."""
import datetime
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import build

root = Path(__file__).resolve().parent
page = (root/'index.html').read_text()
data = json.loads((root/'trip-data.json').read_text())
class Parse(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]; self.remote=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.links.append(a.get('href',''))
        if tag in ['script','img','iframe'] and a.get('src'):self.remote.append(a['src'])
p=Parse();p.feed(page)
assert set(data)=={'changbai','arxan','yichun'}
assert '往返油费' in page and '过路费预留' in page
assert '包车 / 当地交通' not in page
assert '出发城市待确认' not in page
assert all(n==1 for n in Counter(p.ids).values()), 'duplicate ids'
assert all(url[1:] in p.ids for url in p.links if url.startswith('#') and len(url)>1), 'broken anchors'
assert not p.remote,'HTML must be self contained'
assert json.loads(re.search(r'<script type="application/json" id="trip-data">(.*?)</script>',page,re.S)[1])==data
assert (root/'app.js').read_text().strip() in page
for name,route in data.items():
    assert len(route['days'])==10
    assert route['distance']==[sum(day['km'][i] for day in route['days']) for i in range(2)]
    assert route['days'][0]['place'].startswith('北京')
    assert route['days'][-1]['place'].endswith('北京')
    assert 'rail' not in route and 'shared' not in route
    assert route['days'][6]['date']=='10.02' and '青岛' in route['days'][6]['title']
    assert '长春' in route['days'][5]['stay']
    assert all(day['phase']=='你单人驾驶' for day in route['days'][7:])
    assert route['distance']==[route['sharedDistance'][i]+route['soloDistance'][i] for i in range(2)]
    for rooms in [1,2]:
        u,c,t=[build.budget_rows(route,rooms,p) for p in ['user','companion','total']]
        for row in range(len(u)):
            assert all(abs(u[row][2][i]+c[row][2][i]-t[row][2][i])<1e-6 for i in range(2))
    for i,day in enumerate(route['days']):
        date=datetime.date(2026,9,26)+datetime.timedelta(days=i)
        assert day['date']==date.strftime('%m.%d')
        assert day['week']=='周'+'一二三四五六日'[date.weekday()]
        assert day['n']==i+1 and day['plan'] and day['backup']
assert build.cards(data['changbai']['days']) in page
assert all(w in page for w in data['changbai']['warnings'])
build.build()
assert page==(root/'index.html').read_text(),'build must be idempotent'
print('PASS: dates, 30 day cards, embedded JSON/JS, static content, anchors, unique IDs, offline resources and build idempotence')
