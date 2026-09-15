"""Sync portable HTML from public data and JS; uses Python standard library only."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
E = html.escape

def cards(days):
    from urllib.parse import quote
    result = []
    for d in days:
        target = d.get('mapQuery') or [s.strip() for s in re.split(r'[→⇄/]', d['place']) if s.strip()][-1]
        highlights = ''.join(f'<span>{E(h)}</span>' for h in d['highlights'])
        steps = ''.join(f'<li>{E(p)}</li>' for p in d['plan'])
        result.append(f'''<article class="day-card {'transfer' if d['tag']=='整天转场' else ''}" id="day-{d['n']}"><div class="day-top"><div class="day-no">{d['n']:02d}</div><div class="day-date">{E(d['date'])} <span>{E(d['week'])} · {E(d['holiday'])} · {E(d['phase'])}</span></div><span class="tag">{E(d['tag'])}</span></div><h3>{E(d['title'])}</h3><p class="place">{E(d['place'])}</p><div class="highlights">{highlights}</div><div class="logistics"><p><b>怎么走</b>{E(d['transport'])}</p><p><b>住哪里</b>{E(d['stay'])}</p></div><details><summary>展开当天安排与备选 <span aria-hidden="true">＋</span></summary><ol>{steps}</ol><p class="backup"><b>如果计划有变</b><br>{E(d['backup'])}</p><a class="text-link" href="https://map.baidu.com/search/{quote(target)}" target="_blank" rel="noopener noreferrer">在百度地图查位置 ↗</a></details></article>''')
    return ''.join(result)

def budget_rows(route, rooms=1, person='user'):
    share=sum(route['sharedDistance'])/sum(route['distance'])
    def choose(user, companion):
        return user if person=='user' else companion if person=='companion' else [u+c for u,c in zip(user,companion)]
    return [
        ('住宿',f'共同6晚 × {rooms}间平分，后3晚你独住；¥400–700/间夜',choose([v*(3*rooms+3) for v in [400,700]],[v*3*rooms for v in [400,700]])),
        ('往返油费','共同段平分，单人段独担；8–10L/100km × 假设¥8–9/L',choose([v*(route['sharedDistance'][i]/2+route['soloDistance'][i]) for i,v in enumerate([.64,.9])],[v*route['sharedDistance'][i]/2 for i,v in enumerate([.64,.9])])),
        ('过路费预留','按两段里程比例粗分，未扣假日减免',choose([v*(1-share/2) for v in route['toll']],[v*share/2 for v in route['toll']])),
        ('停车预留','按两段里程比例粗分，非逐日收费',choose([v*(1-share/2) for v in route['parking']],[v*share/2 for v in route['parking']])),
        ('门票与景区交通','共同景区各付一份；单人可选游览另预留',choose([v+route['soloTicket'][i] for i,v in enumerate(route['ticket'])],route['ticket'])),
        ('餐饮','你10天，对方7天；按¥100–150/人天',choose([1000,1500],[700,1050]))]

def build():
    data = json.loads((ROOT/'trip-data.json').read_text())
    page = (ROOT/'index.html').read_text()
    for id_, field in {'route-title':'title','route-intro':'intro','route-nights':'nights','route-effort':'effort','route-buffer':'buffer'}.items():
        page = re.sub(r'(<(?:h3|p|span) id="'+id_+r'">).*?(</(?:h3|p|span)>)', lambda m:m[1]+E(data['changbai'][field])+m[2],page, flags=re.S)
    page = re.sub(r'(<ul id="route-warnings">).*?(</ul>)',lambda m:m[1]+''.join('<li>'+E(w)+'</li>' for w in data['changbai']['warnings'])+m[2],page,flags=re.S)
    page = re.sub(r'(<div class="route-path" id="route-path">).*?(</div>)',lambda m:m[1]+'<i aria-hidden="true">→</i>'.join('<span>'+E(p)+'</span>' for p in data['changbai']['path'])+m[2],page,flags=re.S)
    page = re.sub(r'(?<=<!-- DAYS_START -->).*?(?=<!-- DAYS_END -->)',lambda _:cards(data['changbai']['days']),page,flags=re.S)
    route = data['changbai']
    page = re.sub(r'(<p class="small" id="route-mileage">).*?(</p>)', lambda m:m[1]+f"自家车全程约{route['distance'][0]:,}–{route['distance'][1]:,}公里 · 逐日估算合计，非导航结果"+m[2], page,flags=re.S)
    costs = budget_rows(route)
    import math
    total = [math.ceil(sum(row[2][i] for row in costs)*1.15/10)*10 for i in range(2)]
    page = re.sub(r'(<div class="budget-number" id="budget-number">).*?(</div>)',lambda m:m[1]+f'¥{total[0]:,}–{total[1]:,}'+m[2],page,flags=re.S)
    table = ''.join(f'<div class="budget-row"><span>{E(title)}<small>{E(note)}</small></span><strong>¥{math.floor(v[0]+.5):,}–{math.floor(v[1]+.5):,}</strong></div>' for title,note,v in costs)
    page = re.sub(r'(?<=<!-- BUDGET_START -->).*?(?=<!-- BUDGET_END -->)',lambda _:table,page,flags=re.S)
    raw = json.dumps(data,ensure_ascii=False,indent=2).replace('<','\\u003c')
    page = re.sub(r'(<script type="application/json" id="trip-data">).*?(</script>)',lambda m:m[1]+'\n'+raw+'\n'+m[2],page,flags=re.S)
    js = (ROOT/'app.js').read_text().replace('</script','<\\/script')
    page = re.sub(r'(?<=<!-- APP_START -->).*?(?=<!-- APP_END -->)',lambda _:'\n<script>\n'+js+'\n</script>\n',page,flags=re.S)
    (ROOT/'index.html').write_text(page)

if __name__ == '__main__':
    build()
