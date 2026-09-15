/* No network requests: the guide remains usable as a single saved HTML file. */
(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('trip-data').textContent);
  const $ = id => document.getElementById(id);
  const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let route = 'changbai';
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
    const r = data[route];
    const rooms = Number($('rooms').value);
    const person = $('budget-person').value;
    const share = (r.sharedDistance[0]+r.sharedDistance[1]) / (r.distance[0]+r.distance[1]);
    const choose = (user,companion) => person==='user'?user:person==='companion'?companion:user.map((v,i)=>v+companion[i]);
    const rows = [
      ['住宿', `共同6晚 × ${rooms}间平分，后3晚你独住；¥400–700/间夜`, choose([400,700].map(v=>v*(3*rooms+3)),[400,700].map(v=>v*3*rooms))],
      ['往返油费', `共同段平分，单人段独担；8–10L/100km × 假设¥8–9/L`, choose([.64,.9].map((v,i)=>v*(r.sharedDistance[i]/2+r.soloDistance[i])),[.64,.9].map((v,i)=>v*r.sharedDistance[i]/2))],
      ['过路费预留', '按两段里程比例粗分，未扣假日减免',choose(r.toll.map(v=>v*(1-share/2)),r.toll.map(v=>v*share/2))],
      ['停车预留','按两段里程比例粗分，非逐日收费',choose(r.parking.map(v=>v*(1-share/2)),r.parking.map(v=>v*share/2))],
      ['门票与景区交通','共同景区各付一份；单人可选游览另预留',choose(r.ticket.map((v,i)=>v+r.soloTicket[i]),r.ticket)],
      ['餐饮','你10天，对方7天；按¥100–150/人天',choose([1000,1500],[700,1050])]
    ];
    $('budget-route').textContent = {user:'你的费用 · 10天9晚',companion:'同行者费用 · 7天6晚，不含青岛票',total:'两人合计 · 不含青岛票'}[person];
    $('budget-number').textContent = range([0,1].map(i=>Math.ceil(rows.reduce((sum,row)=>sum+row[2][i],0)*1.15/10)*10));
    $('budget-table').innerHTML = rows.map(([title,note,cost])=>`<div class="budget-row"><span>${escape(title)}<small>${escape(note)}</small></span><strong>${range(cost)}</strong></div>`).join('');
  }
  function render(key, updateURL = true) {
    route = Object.hasOwn(data,key) ? key : 'changbai';
    const r = data[route];
    $('route-mileage').textContent = `自家车全程约${money(r.distance[0])}–${money(r.distance[1])}公里 · 逐日估算合计，非导航结果`;
    for (const [id, prop] of Object.entries({'route-title':'title','route-intro':'intro','route-nights':'nights','route-effort':'effort','route-buffer':'buffer'})) $(id).textContent = r[prop];
    $('route-path').innerHTML = r.path.map(p=>`<span>${escape(p)}</span>`).join('<i aria-hidden="true">→</i>');
    $('route-warnings').innerHTML = r.warnings.map(w=>`<li>${escape(w)}</li>`).join('');
    document.querySelectorAll('[data-route]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.route===route)));
    $('day-cards').innerHTML = r.days.map(d=>{
      const target = d.mapQuery || d.place.split(/[→⇄/]/).map(s=>s.trim()).filter(Boolean).at(-1);
      return `<article class="day-card ${d.tag==='整天转场'?'transfer':''}" id="day-${d.n}"><div class="day-top"><div class="day-no">${String(d.n).padStart(2,'0')}</div><div class="day-date">${escape(d.date)} <span>${escape(d.week)} · ${escape(d.holiday)} · ${escape(d.phase)}</span></div><span class="tag">${escape(d.tag)}</span></div><h3>${escape(d.title)}</h3><p class="place">${escape(d.place)}</p><div class="highlights">${d.highlights.map(h=>`<span>${escape(h)}</span>`).join('')}</div><div class="logistics"><p><b>怎么走</b>${escape(d.transport)}</p><p><b>住哪里</b>${escape(d.stay)}</p></div><details><summary>展开当天安排与备选 <span aria-hidden="true">＋</span></summary><ol>${d.plan.map(p=>`<li>${escape(p)}</li>`).join('')}</ol><p class="backup"><b>如果计划有变</b><br>${escape(d.backup)}</p><a class="text-link" href="https://map.baidu.com/search/${encodeURIComponent(target)}" target="_blank" rel="noopener noreferrer">在百度地图查位置 ↗</a></details></article>`;
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
    e.preventDefault(); render('changbai'); $('itinerary').scrollIntoView();
  }));
  ['rooms','budget-person'].forEach(id=>$(id).addEventListener('change',budget));
  const checks = [...document.querySelectorAll('[data-check]')];
  function checkProgress() { $('check-progress').textContent = `已完成 ${checks.filter(c=>c.checked).length} / ${checks.length} 项`; }
  checks.forEach(c=>{
    try { c.checked = localStorage.getItem(`northeast-2026-split-v3-${c.dataset.check}`)==='true'; } catch (_) { /* private/offline mode */ }
    c.addEventListener('change',()=>{
      try { localStorage.setItem(`northeast-2026-split-v3-${c.dataset.check}`,String(c.checked)); } catch (_) { toast('浏览器未允许保存，清单仅在本次打开期间有效'); }
      checkProgress();
    });
  });
  checkProgress();
  $('share').addEventListener('click',async()=>{
    if (!/^https?:$/.test(location.protocol)) { toast('当前是离线文件，请分享HTML文件或打开GitHub Pages网址'); return; }
    const url = new URL(location.href); url.searchParams.set('route',route); url.hash='';
    if (navigator.share) {
      try { await navigator.share({title:`北京自驾东北十日 · ${data[route].name}`,url:url.href}); return; }
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
