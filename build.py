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
        target = [s.strip() for s in re.split(r'[→⇄/]', d['place']) if s.strip()][-1]
        highlights = ''.join(f'<span>{E(h)}</span>' for h in d['highlights'])
        steps = ''.join(f'<li>{E(p)}</li>' for p in d['plan'])
        result.append(f'''<article class="day-card {'transfer' if d['tag']=='整天转场' else ''}" id="day-{d['n']}"><div class="day-top"><div class="day-no">{d['n']:02d}</div><div class="day-date">{E(d['date'])} <span>{E(d['week'])} · {E(d['holiday'])}</span></div><span class="tag">{E(d['tag'])}</span></div><h3>{E(d['title'])}</h3><p class="place">{E(d['place'])}</p><div class="highlights">{highlights}</div><div class="logistics"><p><b>怎么走</b>{E(d['transport'])}</p><p><b>住哪里</b>{E(d['stay'])}</p></div><details><summary>展开当天安排与备选 <span aria-hidden="true">＋</span></summary><ol>{steps}</ol><p class="backup"><b>如果计划有变</b><br>{E(d['backup'])}</p><a class="text-link" href="https://map.baidu.com/search/{quote(target)}" target="_blank" rel="noopener noreferrer">在百度地图查位置 ↗</a></details></article>''')
    return ''.join(result)

def build():
    data = json.loads((ROOT/'trip-data.json').read_text())
    page = (ROOT/'index.html').read_text()
    for id_, field in {'route-title':'title','route-intro':'intro','route-nights':'nights','route-effort':'effort','route-buffer':'buffer'}.items():
        page = re.sub(r'(<(?:h3|p|span) id="'+id_+r'">).*?(</(?:h3|p|span)>)', lambda m:m[1]+E(data['all'][field])+m[2],page, flags=re.S)
    page = re.sub(r'(<ul id="route-warnings">).*?(</ul>)',lambda m:m[1]+''.join('<li>'+E(w)+'</li>' for w in data['all']['warnings'])+m[2],page,flags=re.S)
    page = re.sub(r'(<div class="route-path" id="route-path">).*?(</div>)',lambda m:m[1]+'<i aria-hidden="true">→</i>'.join('<span>'+E(p)+'</span>' for p in data['all']['path'])+m[2],page,flags=re.S)
    page = re.sub(r'(?<=<!-- DAYS_START -->).*?(?=<!-- DAYS_END -->)',lambda _:cards(data['all']['days']),page,flags=re.S)
    raw = json.dumps(data,ensure_ascii=False,indent=2).replace('<','\\u003c')
    page = re.sub(r'(<script type="application/json" id="trip-data">).*?(</script>)',lambda m:m[1]+'\n'+raw+'\n'+m[2],page,flags=re.S)
    js = (ROOT/'app.js').read_text().replace('</script','<\\/script')
    page = re.sub(r'(?<=<!-- APP_START -->).*?(?=<!-- APP_END -->)',lambda _:'\n<script>\n'+js+'\n</script>\n',page,flags=re.S)
    (ROOT/'index.html').write_text(page)

if __name__ == '__main__':
    build()
