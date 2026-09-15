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
assert all(n==1 for n in Counter(p.ids).values()), 'duplicate ids'
assert all(url[1:] in p.ids for url in p.links if url.startswith('#') and len(url)>1), 'broken anchors'
assert not p.remote,'HTML must be self contained'
assert json.loads(re.search(r'<script type="application/json" id="trip-data">(.*?)</script>',page,re.S)[1])==data
assert (root/'app.js').read_text().strip() in page
for name,route in data.items():
    assert len(route['days'])==7
    for i,day in enumerate(route['days']):
        date=datetime.date(2026,9,26)+datetime.timedelta(days=i)
        assert day['date']==date.strftime('%m.%d')
        assert day['week']=='周'+'一二三四五六日'[date.weekday()]
        assert day['n']==i+1 and day['plan'] and day['backup']
assert build.cards(data['all']['days']) in page
assert all(w in page for w in data['all']['warnings'])
build.build()
assert page==(root/'index.html').read_text(),'build must be idempotent'
print('PASS: dates, 14 day cards, embedded JSON/JS, static content, anchors, unique IDs, offline resources and build idempotence')
