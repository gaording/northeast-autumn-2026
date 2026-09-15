"""Build one portable HTML from template, data, original art and JS. No dependencies."""
import html
import json
import math
from pathlib import Path
from urllib.parse import quote
import scenes
ROOT=Path(__file__).resolve().parent
E=html.escape

def detail(day):
    plan=''.join(f'<li>{E(p)}</li>' for p in day['plan'])
    return f'''<div class="logistics"><div><b>怎么走</b>{E(day['transport'])}</div><div><b>住在哪里</b>{E(day['stay'])}</div></div><div class="story-block"><h4>当天节奏 / 不追打卡</h4><ol>{plan}</ol></div><div class="story-block"><h4>步行与留白</h4><p>{E(day['walk'])}</p></div><div class="story-block"><h4>当天怎么穿</h4><p>{E(day['clothes'])}</p></div><p class="backup"><b>天气或计划有变</b><br>{E(day['backup'])}</p><a class="text-link" href="https://map.baidu.com/search/{quote(day['mapQuery'])}" target="_blank" rel="noopener noreferrer">在地图查位置 ↗</a>'''

def cards(days):
    parts=[]
    phases={1:'ACT I / 两人一起 · 向森林出发',7:'ACT II / 10月2日 · 在长春候选分流',8:'ACT III / 你单人驾驶 · 慢慢南返'}
    for d in days:
        if d['n'] in phases:parts.append(f'<p class="phase-label">{phases[d["n"]]}</p>')
        parts.append(f'''<article class="day-card" id="day-{d['n']}"><div class="date-pin"><strong>{E(d['date'])}</strong><span>{E(d['week'])}</span></div><button type="button" class="chapter-open" data-day="{d['n']}" aria-haspopup="dialog" aria-controls="chapter-dialog" aria-label="打开{E(d['date'])}章节：{E(d['title'])}"><span class="chapter-image" style="--scene:var(--scene-{d['scene']})"><span class="chapter-badge">{E(d['tag'])}</span><span class="chapter-mood">{E(d['mood'])}</span></span><span class="chapter-text"><span class="chapter-kicker">CHAPTER {d['n']:02d} / {E(d['phase'])}</span><span class="chapter-title">{E(d['title'])}</span><span class="chapter-place">{E(d['place'])}</span><span class="chapter-foot"><span>约{d['km'][0]}–{d['km'][1]}km · 规划估算</span><span class="chapter-enter">进入章节 ↗</span></span></span></button><details class="chapter-details"><summary>展开文字安排 · 无脚本也可阅读</summary>{detail(d)}</details></article>''')
    return ''.join(parts)
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
    data=json.loads((ROOT/'trip-data.json').read_text())
    route=data['changbai']
    art={key:scenes.scene(key) for key in scenes.PALETTES}
    (ROOT/'assets').mkdir(exist_ok=True)
    for key,svg in art.items():(ROOT/'assets'/f'{key}.svg').write_text(svg)
    css=':root{'+''.join(f'--scene-{key}:url("data:image/svg+xml,{quote(svg,safe="")}");' for key,svg in art.items())+'}\n'+(ROOT/'styles.css').read_text()
    costs=budget_rows(route)
    total=[math.ceil(sum(row[2][i] for row in costs)*1.15/10)*10 for i in range(2)]
    budget=''.join(f'<div class="budget-row"><span>{E(title)}<small>{E(note)}</small></span><strong>¥{math.floor(v[0]+.5):,}–{math.floor(v[1]+.5):,}</strong></div>' for title,note,v in costs)
    tabs=''.join(f'<button type="button" class="tab" id="tab-{key}" data-route="{key}" aria-pressed="{str(key=="changbai").lower()}" aria-controls="route-content"><span class="letter">ROUTE {i+1:02d}</span><b>{E(value["name"])}</b><small>{E(value["label"])}</small></button>' for i,(key,value) in enumerate(data.items()))
    replacements={
        'STYLES':css,'APP':(ROOT/'app.js').read_text().replace('</script','<\\/script'),
        'HERO_STYLE':'--scene:var(--scene-forest)','TABS':tabs,
        'FOREST':E(route['forest']),'ROUTE_TITLE':E(route['title']),'ROUTE_INTRO':E(route['intro']),
        'ROUTE_PATH':'<i aria-hidden="true">→</i>'.join('<span>'+E(p)+'</span>' for p in route['path']),
        'NIGHTS':E(route['nights']),'EFFORT':E(route['effort']),
        'MILEAGE':f"全程约{route['distance'][0]:,}–{route['distance'][1]:,}公里 · 逐日估算合计，非实时导航",
        'WARNINGS':''.join('<li>'+E(w)+'</li>' for w in route['warnings']),
        'CARDS':cards(route['days']),'BUDGET_TOTAL':f'¥{total[0]:,}–{total[1]:,}',
        'BUDGET_ROWS':budget,'SOURCES':(ROOT/'sources.html').read_text(),
        'DATA':json.dumps(data,ensure_ascii=False,indent=2).replace('<','\\u003c'),
        'SCENES':json.dumps(list(art))}
    text=(ROOT/'index.template.html').read_text()
    for key,value in replacements.items():text=text.replace('@@'+key+'@@',value)
    assert '@@' not in text,'unresolved template token'
    (ROOT/'index.html').write_text(text)
if __name__=='__main__':build()
