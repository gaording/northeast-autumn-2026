/* No network requests: the guide remains usable as a single saved HTML file. */
(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('trip-data').textContent);
  const $ = id => document.getElementById(id);
  const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let route = 'all';
  let toastTimer;
  const money = n => Math.round(n).toLocaleString('zh-CN');
  const range = values => `¥${money(values[0])}–${money(values[1])}`;
  function toast(message) {
    $('toast').textContent = message;
    $('toast').classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => $('toast').classList.remove('show'), 3500);
  }
  function budget() {
    const p = Number($('people').value);
    const r = data[route];
    const rooms = Math.ceil(p / 2);
    const rows = [
      ['住宿', `6晚 × ${rooms}间 × ¥400–700 ÷ ${p}人`, [6*rooms*400/p,6*rooms*700/p]],
      ['包车 / 当地交通', `全队${range(r.shared)} ÷ ${p}人`, r.shared.map(v=>v/p)],
      ['铁路 / 城际交通预留', '不包含出发城市往返东北的大交通', r.rail],
      ['门票与景区交通', '按计划预留，非官方票价', r.ticket],
      ['吃饭', '7天 × ¥100–150/人', [700,1050]]
    ];
    $('budget-route').textContent = `${r.name} · 7天6晚`;
    $('budget-number').textContent = range([0,1].map(i=>Math.ceil(rows.reduce((s,row)=>s+row[2][i],0)*1.15/10)*10));
    $('budget-table').innerHTML = rows.map(([title,note,cost])=>`<div class="budget-row"><span>${escape(title)}<small>${escape(note)}</small></span><strong>${range(cost)}</strong></div>`).join('');
  }
  function render(key, updateURL = true) {
    route = Object.hasOwn(data,key) ? key : 'all';
    const r = data[route];
    for (const [id, prop] of Object.entries({'route-title':'title','route-intro':'intro','route-nights':'nights','route-effort':'effort','route-buffer':'buffer'})) $(id).textContent = r[prop];
    $('route-path').innerHTML = r.path.map(p=>`<span>${escape(p)}</span>`).join('<i aria-hidden="true">→</i>');
    $('route-warnings').innerHTML = r.warnings.map(w=>`<li>${escape(w)}</li>`).join('');
    document.querySelectorAll('[data-route]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.route===route)));
    $('day-cards').innerHTML = r.days.map(d=>{
      const target = d.place.split(/[→⇄/]/).map(s=>s.trim()).filter(Boolean).at(-1);
      return `<article class="day-card ${d.tag==='整天转场'?'transfer':''}" id="day-${d.n}"><div class="day-top"><div class="day-no">${String(d.n).padStart(2,'0')}</div><div class="day-date">${escape(d.date)} <span>${escape(d.week)} · ${escape(d.holiday)}</span></div><span class="tag">${escape(d.tag)}</span></div><h3>${escape(d.title)}</h3><p class="place">${escape(d.place)}</p><div class="highlights">${d.highlights.map(h=>`<span>${escape(h)}</span>`).join('')}</div><div class="logistics"><p><b>怎么走</b>${escape(d.transport)}</p><p><b>住哪里</b>${escape(d.stay)}</p></div><details><summary>展开当天安排与备选 <span aria-hidden="true">＋</span></summary><ol>${d.plan.map(p=>`<li>${escape(p)}</li>`).join('')}</ol><p class="backup"><b>如果计划有变</b><br>${escape(d.backup)}</p><a class="text-link" href="https://map.baidu.com/search/${encodeURIComponent(target)}" target="_blank" rel="noopener noreferrer">在百度地图查位置 ↗</a></details></article>`;
    }).join('');
    budget();
    if (updateURL && /^https?:$/.test(location.protocol)) {
      const url = new URL(location.href);
      url.searchParams.set('route',route);
      history.replaceState(null,'',url);
    }
  }
  document.querySelectorAll('[data-route]').forEach(b=>b.addEventListener('click',()=>{
    render(b.dataset.route); toast(`已切换：${data[route].name}，每日安排与预算已更新`);
  }));
  ['recommend','notice-easy'].forEach(id=>$(id).addEventListener('click',e=>{
    e.preventDefault(); render('easy'); $('itinerary').scrollIntoView();
  }));
  $('people').addEventListener('change',budget);
  const checks = [...document.querySelectorAll('[data-check]')];
  function checkProgress() { $('check-progress').textContent = `已完成 ${checks.filter(c=>c.checked).length} / ${checks.length} 项`; }
  checks.forEach(c=>{
    try { c.checked = localStorage.getItem(`northeast-2026-${c.dataset.check}`)==='true'; } catch (_) { /* private/offline mode */ }
    c.addEventListener('change',()=>{
      try { localStorage.setItem(`northeast-2026-${c.dataset.check}`,String(c.checked)); } catch (_) { toast('浏览器未允许保存，清单仅在本次打开期间有效'); }
      checkProgress();
    });
  });
  checkProgress();
  $('share').addEventListener('click',async()=>{
    if (!/^https?:$/.test(location.protocol)) { toast('当前是离线文件，请分享HTML文件或打开GitHub Pages网址'); return; }
    const url = new URL(location.href); url.searchParams.set('route',route); url.hash='';
    if (navigator.share) {
      try { await navigator.share({title:`东北七日赏秋 · ${data[route].name}`,url:url.href}); return; }
      catch (e) { if (e.name==='AbortError') return; }
    }
    try { await navigator.clipboard.writeText(url.href); toast('已复制当前路线链接，可以发给朋友了'); }
    catch (_) { $('share-fallback').hidden=false; $('share-url').value=url.href; $('share-url').focus(); $('share-url').select(); toast('请复制选中的链接'); }
  });
  let printState;
  window.addEventListener('beforeprint',()=>{
    if (printState) return;
    printState=[...document.querySelectorAll('details')].map(d=>[d,d.open]);
    printState.forEach(([d])=>{d.open=true;});
  });
  window.addEventListener('afterprint',()=>{ if(printState) printState.forEach(([d,open])=>{d.open=open;}); printState=null; });
  $('print').addEventListener('click',()=>window.print());
  document.querySelectorAll('a[href^="#source-"]').forEach(a=>a.addEventListener('click',()=>{$('sources').open=true;}));
  window.addEventListener('popstate',()=>render(new URL(location.href).searchParams.get('route'),false));
  render(new URL(location.href).searchParams.get('route'),false);
})();
