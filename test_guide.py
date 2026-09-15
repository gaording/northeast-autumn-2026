"""Offline regression checks; no external dependencies or network calls."""
import datetime,json,re,math
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import build,scenes
ROOT=Path(__file__).resolve().parent
page=(ROOT/'index.html').read_text();data=json.loads((ROOT/'trip-data.json').read_text())
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.remote=[];self.buttons=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a':self.links.append(a.get('href',''))
  if tag in ['img','script','iframe'] and a.get('src'):self.remote.append(a['src'])
  if tag=='button' and 'data-day' in a:self.buttons.append(a)
p=Parse();p.feed(page)
assert set(data)=={'changbai','forest4','yichun','arxan'}
assert all(n==1 for n in Counter(p.ids).values()),'duplicate IDs'
assert all(h[1:] in p.ids for h in p.links if h.startswith('#') and len(h)>1),'broken hash target'
assert not p.remote,'page must work offline without external resources'
assert len(p.buttons)==10 and all(x.get('aria-haspopup')=='dialog' for x in p.buttons)
assert json.loads(re.search(r'<script type="application/json" id="trip-data">(.*?)</script>',page,re.S)[1])==data
assert (ROOT/'app.js').read_text().strip() in page
assert 'aria-labelledby="dialog-title"' in page and '@@' not in page
assert '较厚羽绒' in page and '非目的地实拍' in page
assert len(re.findall(r'data-check="',page.split('<script type=')[0]))==12
for key,r in data.items():
 assert len(r['days'])==10
 assert r['days'][0]['place'].startswith('北京') and r['days'][-1]['place'].endswith('北京')
 assert r['distance']==[sum(d['km'][i] for d in r['days']) for i in range(2)]
 assert r['distance']==[r['sharedDistance'][i]+r['soloDistance'][i] for i in range(2)]
 assert '青岛' in r['days'][6]['title'] and '长春' in r['days'][5]['stay']
 assert all(d['phase']=='你单人驾驶' for d in r['days'][7:])
 for i,d in enumerate(r['days']):
  date=datetime.date(2026,9,26)+datetime.timedelta(days=i)
  assert d['date']==date.strftime('%m.%d') and d['week']=='周'+'一二三四五六日'[date.weekday()]
  assert d['n']==i+1 and d['scene'] in scenes.PALETTES
  assert all(d[f] for f in ['walk','clothes','mapQuery','mood','backup','plan'])
 for rooms in [1,2]:
  u,c,t=[build.budget_rows(r,rooms,p) for p in ['user','companion','total']]
  for row in range(len(u)):
   assert all(math.isclose(u[row][2][i]+c[row][2][i],t[row][2][i]) for i in range(2))
assert '4晚' in data['forest4']['forest'] and '3晚' in data['changbai']['forest']
assert '8–10' in data['forest4']['days'][0]['transport']
assert '四晚版首日' in data['forest4']['warnings'][0]
assert build.cards(data['changbai']['days']) in page
for name in scenes.PALETTES:assert (ROOT/'assets'/f'{name}.svg').read_text()==scenes.scene(name)
build.build();assert page==(ROOT/'index.html').read_text(),'non-idempotent build'
print('PASS: 4 routes / 40 day records, dates, split phases, kilometers, budget conservation, 10 chapter triggers, 12 checklist items, accessible dialog, offline art, static/JS data and idempotent build')
