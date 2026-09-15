/* Portable, dependency-free forest chapters. No tracking or external requests. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const data=JSON.parse($('trip-data').textContent);
  const sceneNames=JSON.parse($('scene-data').textContent);
  const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const money=n=>Math.round(n).toLocaleString('zh-CN');
  const range=values=>`¥${money(values[0])}–${money(values[1])}`;
  const dialog=$('chapter-dialog');
  let route='changbai', activeDay=null, opener=null, toastTimer, oldOverflow='', printState;
  function toast(text){$('toast').textContent=text;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),4000);}
  function setURL(day=null){
    if(!/^https?:$/.test(location.protocol))return;
    const url=new URL(location.href);url.searchParams.set('route',route);
    if(day)url.hash=`day-${day}`;
    else if(/^#day-\d+$/.test(url.hash))url.hash='itinerary';
    history.replaceState(null,'',url);
  }
  function detail(d){
    return `<div class="logistics"><div><b>怎么走</b>${escape(d.transport)}</div><div><b>住在哪里</b>${escape(d.stay)}</div></div><div class="story-block"><h4>当天节奏 / 不追打卡</h4><ol>${d.plan.map(p=>`<li>${escape(p)}</li>`).join('')}</ol></div><div class="story-block"><h4>步行与留白</h4><p>${escape(d.walk)}</p></div><div class="story-block"><h4>当天怎么穿</h4><p>${escape(d.clothes)}</p></div><p class="backup"><b>天气或计划有变</b><br>${escape(d.backup)}</p><a class="text-link" href="https://map.baidu.com/search/${encodeURIComponent(d.mapQuery)}" target="_blank" rel="noopener noreferrer">在地图查位置 ↗</a>`;
  }
  function cards(days){
    const phases={1:'ACT I / 两人一起 · 向森林出发',7:'ACT II / 10月2日 · 在长春候选分流',8:'ACT III / 你单人驾驶 · 慢慢南返'};
    return days.map(d=>`${phases[d.n]?`<p class="phase-label">${phases[d.n]}</p>`:''}<article class="day-card" id="day-${d.n}"><div class="date-pin"><strong>${escape(d.date)}</strong><span>${escape(d.week)}</span></div><button type="button" class="chapter-open" data-day="${d.n}" aria-haspopup="dialog" aria-controls="chapter-dialog" aria-label="打开${escape(d.date)}章节：${escape(d.title)}"><span class="chapter-image" style="--scene:var(--scene-${sceneNames.includes(d.scene)?d.scene:'forest'})"><span class="chapter-badge">${escape(d.tag)}</span><span class="chapter-mood">${escape(d.mood)}</span></span><span class="chapter-text"><span class="chapter-kicker">CHAPTER ${String(d.n).padStart(2,'0')} / ${escape(d.phase)}</span><span class="chapter-title">${escape(d.title)}</span><span class="chapter-place">${escape(d.place)}</span><span class="chapter-foot"><span>约${d.km[0]}–${d.km[1]}km · 规划估算</span><span class="chapter-enter">进入章节 ↗</span></span></span></button><details class="chapter-details"><summary>展开文字安排 · 无脚本也可阅读</summary>${detail(d)}</details></article>`).join('');
  }
  function budget(){
    const r=data[route],rooms=Number($('rooms').value),person=$('budget-person').value;
    const share=(r.sharedDistance[0]+r.sharedDistance[1])/(r.distance[0]+r.distance[1]);
    const choose=(user,companion)=>person==='user'?user:person==='companion'?companion:user.map((v,i)=>v+companion[i]);
    const rows=[
      ['住宿',`共同6晚 × ${rooms}间平分，后3晚你独住；¥400–700/间夜`,choose([400,700].map(v=>v*(3*rooms+3)),[400,700].map(v=>v*3*rooms))],
      ['往返油费','共同段平分，单人段独担；8–10L/100km × 假设¥8–9/L',choose([.64,.9].map((v,i)=>v*(r.sharedDistance[i]/2+r.soloDistance[i])),[.64,.9].map((v,i)=>v*r.sharedDistance[i]/2))],
      ['过路费预留','按两段里程比例粗分，未扣假日减免',choose(r.toll.map(v=>v*(1-share/2)),r.toll.map(v=>v*share/2))],
      ['停车预留','按两段里程比例粗分，非逐日收费',choose(r.parking.map(v=>v*(1-share/2)),r.parking.map(v=>v*share/2))],
      ['门票与景区交通','共同景区各付一份；单人可选游览另预留',choose(r.ticket.map((v,i)=>v+r.soloTicket[i]),r.ticket)],
      ['餐饮','你10天，对方7天；按¥100–150/人天',choose([1000,1500],[700,1050])]
    ];
    $('budget-route').textContent={user:'你的费用 · 10天9晚',companion:'同行者费用 · 7天6晚，不含青岛票',total:'两人合计 · 不含青岛票'}[person];
    $('budget-number').textContent=range([0,1].map(i=>Math.ceil(rows.reduce((sum,row)=>sum+row[2][i],0)*1.15/10)*10));
    $('budget-table').innerHTML=rows.map(([title,note,cost])=>`<div class="budget-row"><span>${escape(title)}<small>${escape(note)}</small></span><strong>${range(cost)}</strong></div>`).join('');
  }
  function showChapter(n,trigger=null,updateURL=true){
    const d=data[route].days[n-1];if(!d)return;
    if(typeof dialog.showModal!=='function'){
      const text=$(`day-${n}`).querySelector('details');text.style.display='block';text.open=true;text.scrollIntoView();return;
    }
    if(!dialog.open){opener=trigger||document.querySelector(`[data-day="${n}"]`);oldOverflow=document.body.style.overflow;document.body.style.overflow='hidden';}
    activeDay=n;
    $('dialog-counter').textContent=`CHAPTER ${String(n).padStart(2,'0')} / ${data[route].days.length}`;
    $('dialog-position').textContent=`${d.date} · ${d.phase}`;
    $('dialog-title').textContent=d.title;
    $('dialog-mood').textContent=d.mood;
    $('dialog-scene').style.setProperty('--scene',`var(--scene-${sceneNames.includes(d.scene)?d.scene:'forest'})`);
    $('dialog-meta').innerHTML=[d.date,d.week,d.holiday,d.tag].map(v=>`<span>${escape(v)}</span>`).join('');
    $('dialog-detail').innerHTML=detail(d);
    $('prev-chapter').disabled=n===1;$('next-chapter').disabled=n===data[route].days.length;
    if(!dialog.open){dialog.showModal();$('close-dialog').focus({preventScroll:true});}
    if(document.activeElement.disabled)$('close-dialog').focus({preventScroll:true});
    $('chapter-share-status').textContent='';$('chapter-share-fallback').hidden=true;
    dialog.scrollTop=0;
    if(updateURL)setURL(n);
  }
  function finishClose(updateURL=true){
    if(activeDay===null)return;
    document.body.style.overflow=oldOverflow;activeDay=null;if(updateURL)setURL();
    if(opener?.isConnected)opener.focus({preventScroll:true});
  }
  function closeChapter(updateURL=true){if(dialog.open){dialog.close();finishClose(updateURL);}}
  dialog.addEventListener('close',()=>{if(!dialog.open)finishClose();});
  $('close-dialog').addEventListener('click',()=>closeChapter());
  dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeChapter();}});
  $('prev-chapter').addEventListener('click',()=>showChapter(activeDay-1));
  $('next-chapter').addEventListener('click',()=>showChapter(activeDay+1));
  dialog.addEventListener('keydown',e=>{
    if(e.key==='Tab'){
      const focusable=[...dialog.querySelectorAll('button:not(:disabled),a[href],input,select,textarea,[tabindex="0"]')].filter(el=>el.getClientRects().length);
      const first=focusable[0],last=focusable.at(-1);
      if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
      else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
      return;
    }
    if(e.altKey||e.ctrlKey||e.metaKey||['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName))return;
    if(e.key==='ArrowRight'&&activeDay<data[route].days.length){e.preventDefault();showChapter(activeDay+1);}
    if(e.key==='ArrowLeft'&&activeDay>1){e.preventDefault();showChapter(activeDay-1);}
  });
  $('day-cards').addEventListener('click',e=>{const b=e.target.closest('[data-day]');if(b)showChapter(Number(b.dataset.day),b);});
  function render(key,updateURL=true){
    if(dialog.open)closeChapter(false);route=Object.hasOwn(data,key)?key:'changbai';const r=data[route];
    for(const [id,field] of Object.entries({'route-title':'title','route-intro':'intro','route-nights':'nights','route-effort':'effort','route-forest':'forest'}))$(id).textContent=r[field];
    $('route-mileage').textContent=`全程约${money(r.distance[0])}–${money(r.distance[1])}公里 · 逐日估算合计，非实时导航`;
    $('route-path').innerHTML=r.path.map(p=>`<span>${escape(p)}</span>`).join('<i aria-hidden="true">→</i>');
    $('route-warnings').innerHTML=r.warnings.map(w=>`<li>${escape(w)}</li>`).join('');
    document.querySelectorAll('[data-route]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.route===route)));
    $('day-cards').innerHTML=cards(r.days);budget();if(updateURL)setURL();
  }
  document.querySelectorAll('[data-route]').forEach(b=>b.addEventListener('click',()=>{render(b.dataset.route);toast(`已切换：${data[route].name}，时间轴与预算已更新`);}));
  ['rooms','budget-person'].forEach(id=>$(id).addEventListener('change',budget));
  const checks=[...document.querySelectorAll('[data-check]')];
  function checkProgress(){$('check-progress').textContent=`已完成 ${checks.filter(c=>c.checked).length} / ${checks.length} 项`;}
  checks.forEach(c=>{try{c.checked=localStorage.getItem(`forest-packing-v4-${c.dataset.check}`)==='true';}catch(_){}
    c.addEventListener('change',()=>{try{localStorage.setItem(`forest-packing-v4-${c.dataset.check}`,String(c.checked));}catch(_){toast('浏览器不允许保存，勾选仅本次有效');}checkProgress();});});checkProgress();
  async function shareTrip(){
    const notify=text=>{if(dialog.open)$('chapter-share-status').textContent=text;else toast(text);};
    if(!/^https?:$/.test(location.protocol)){notify('当前为离线文件，请分享HTML文件或打开GitHub Pages网址');return;}
    const url=new URL(location.href);url.searchParams.set('route',route);url.hash=activeDay?`day-${activeDay}`:'';
    if(navigator.share){try{await navigator.share({title:`森林慢旅行 · ${data[route].name}`,url:url.href});return;}catch(e){if(e.name==='AbortError')return;}}
    try{await navigator.clipboard.writeText(url.href);notify(activeDay?'已复制这一章的链接':'已复制旅程链接，可以发给朋友');}catch(_){const prefix=dialog.open?'chapter-':'';$(prefix+'share-fallback').hidden=false;$(prefix+'share-url').value=url.href;$(prefix+'share-url').focus();$(prefix+'share-url').select();notify('请复制选中的地址');}
  }
  $('share').addEventListener('click',shareTrip);$('share-chapter').addEventListener('click',shareTrip);
  window.addEventListener('beforeprint',()=>{if(printState)return;printState=[...document.querySelectorAll('details')].map(d=>[d,d.open]);printState.forEach(([d])=>{d.open=true;});});
  window.addEventListener('afterprint',()=>{if(printState)printState.forEach(([d,open])=>{d.open=open;});printState=null;});
  $('print').addEventListener('click',()=>window.print());
  document.querySelectorAll('a[href^="#source-"]').forEach(a=>a.addEventListener('click',()=>{$('sources').open=true;}));
  function fromURL(){const url=new URL(location.href),m=url.hash.match(/^#day-(\d+)$/);render(url.searchParams.get('route'),false);if(m)showChapter(Number(m[1]),null,false);}
  fromURL();document.documentElement.classList.add('js');
  window.addEventListener('load',()=>{if(dialog.open)requestAnimationFrame(()=>$('close-dialog').focus({preventScroll:true}));},{once:true});
  window.addEventListener('popstate',fromURL);
})();
