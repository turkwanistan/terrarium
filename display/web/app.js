(() => {
  'use strict';
  const canvas = document.getElementById('terrarium');
  const ctx = canvas.getContext('2d', { alpha: false });
  const debug = document.getElementById('debug');
  const snapshotPath = new URLSearchParams(window.location.search).get('snapshot');
  if (canvas.width !== 800 || canvas.height !== 480) throw new Error('Terrarium logical viewport must be exactly 800x480');
  ctx.imageSmoothingEnabled = false;

  let frame = null;
  let previous = null;
  let fetchedAt = performance.now();
  let connected = false;
  let debugVisible = false;
  let lastPollError = null;
  const rain = Array.from({length: 42}, (_, i) => ({x: (i * 67) % 800, y: (i * 41) % 250, speed: 0.45 + (i % 4) * 0.13}));
  const dust = Array.from({length: 18}, (_, i) => ({x: 260 + (i * 83) % 420, y: 80 + (i * 53) % 280, phase: i * 1.7}));

  function mix(a, b, t) { return a + (b - a) * t; }
  function clamp01(v) { return Math.max(0, Math.min(1, v)); }
  function smooth01(v) { const t=clamp01(v); return t*t*(3-2*t); }
  function emergence(value, start, span) { return smooth01((value-start)/Math.max(.001,span)); }
  function historyValue(f, key, now) {
    const target=Number(f.habitat.activity_aftermath?.[key] || 0);
    if (!previous || snapshotPath) return target;
    const source=Number(previous.habitat?.activity_aftermath?.[key] || 0);
    return mix(source,target,smooth01((now-fetchedAt)/1800));
  }
  function stableUnit(label, index) {
    let h=2166136261;
    const text=`${label}:${index}`;
    for (let i=0;i<text.length;i++){ h^=text.charCodeAt(i); h=Math.imul(h,16777619); }
    return (h>>>0)/4294967295;
  }
  function rounded(x, y, w, h, r, fill) {
    ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fillStyle = fill; ctx.fill();
  }
  function palette(lighting) {
    if (lighting === 'night') return {wall:'#27313d', floor:'#3b342f', trim:'#55463a', glow:'#d9a95b', sky:'#162238', rug:'#596358'};
    if (lighting === 'dawn') return {wall:'#75665e', floor:'#5b493b', trim:'#735845', glow:'#f0bd72', sky:'#c78373', rug:'#66735e'};
    if (lighting === 'dusk') return {wall:'#665957', floor:'#594438', trim:'#715542', glow:'#efad62', sky:'#8e5e76', rug:'#69715c'};
    return {wall:'#8b806f', floor:'#6e5946', trim:'#7c5d46', glow:'#f4cf82', sky:'#82a6a1', rug:'#73806a'};
  }

  function drawPersistentHistory(f) {
    const wear = f.habitat.path_wear || {};
    const routes = {
      sleeping_nook: {end:[154,427], control:[274,408]},
      window: {end:[182,306], control:[286,337]},
      collection_shelf: {end:[650,303], control:[548,333]},
      activity_corner: {end:[650,427], control:[535,408]},
    };
    ctx.save();
    ctx.lineCap='round';
    for (const [zone, route] of Object.entries(routes)) {
      const visits = Number(wear[zone] || 0);
      if (visits < 5) continue;
      const alpha = Math.min(.18, .018 + (visits - 4) * .0048);
      const width = Math.min(12, 2.6 + visits * .17);
      ctx.strokeStyle = `rgba(47,34,27,${alpha})`;
      ctx.lineWidth = width;
      ctx.beginPath(); ctx.moveTo(405,421);
      ctx.quadraticCurveTo(route.control[0],route.control[1],route.end[0],route.end[1]); ctx.stroke();
      ctx.strokeStyle = `rgba(222,198,154,${Math.min(.10,alpha*.42)})`;
      ctx.lineWidth = Math.max(1.5,width*.18);
      ctx.setLineDash([7,12]);
      ctx.beginPath(); ctx.moveTo(405,421);
      ctx.quadraticCurveTo(route.control[0],route.control[1],route.end[0],route.end[1]); ctx.stroke();
      ctx.setLineDash([]);
    }

    // Frequently moved possessions leave small settled/scuffed patches. They
    // are physical cues, not labels: reopening the diorama reveals use without
    // turning the world into an activity feed.
    for (const o of f.objects || []) {
      const moved = Number(o.times_moved || 0);
      if (o.state !== 'placed' || moved < 2) continue;
      ctx.fillStyle = `rgba(39,29,24,${Math.min(.16,.035+moved*.012)})`;
      ctx.beginPath(); ctx.ellipse(o.x,o.y+7,13+Math.min(7,moved),5,0,0,Math.PI*2); ctx.fill();
    }
    ctx.restore();
  }

  function drawBackground(f, now) {
    const p = palette(f.lighting);
    ctx.fillStyle = p.wall; ctx.fillRect(0, 0, 800, 315);
    ctx.fillStyle = p.floor; ctx.fillRect(0, 315, 800, 165);
    ctx.fillStyle = p.trim; ctx.fillRect(0, 307, 800, 12);

    // Window / weather: environmental time instead of a dashboard clock.
    rounded(54, 48, 225, 172, 5, '#392f31');
    rounded(65, 58, 203, 151, 2, p.sky);
    ctx.fillStyle = f.lighting === 'night' ? '#ddd2a8' : '#f5d293';
    if (f.lighting === 'night') { ctx.beginPath(); ctx.arc(224, 91, 14, 0, Math.PI*2); ctx.fill(); }
    else { ctx.beginPath(); ctx.arc(215, 92, 18, 0, Math.PI*2); ctx.fill(); }
    ctx.fillStyle = 'rgba(35,45,55,.33)'; ctx.fillRect(163,58,7,151); ctx.fillRect(65,130,203,7);
    if (f.weather === 'rain') {
      ctx.strokeStyle = 'rgba(190,214,218,.65)'; ctx.lineWidth = 2;
      for (const d of rain) {
        const y = 62 + ((d.y + now * d.speed * .06) % 143);
        const x = 68 + (d.x % 195);
        ctx.beginPath(); ctx.moveTo(x,y); ctx.lineTo(x-5,y+11); ctx.stroke();
      }
    } else if (f.weather === 'mist') {
      ctx.fillStyle = 'rgba(224,224,210,.18)'; ctx.fillRect(65,118,203,46); ctx.fillRect(65,172,203,20);
    }
    // Persistent window traces emerge continuously. Current weather changes
    // how the same history reads: rain glints on old streaks, mist softens
    // smudges, and clear weather leaves the dried traces understated.
    const windowWatches = historyValue(f,'window_watches',now);
    const wetWatches = historyValue(f,'wet_window_watches',now);
    const smudgeWeather = f.weather === 'rain' ? .72 : f.weather === 'mist' ? .84 : 1;
    for (let i=0;i<5;i++) {
      const strength=emergence(windowWatches,1+i*2.8,6.5);
      if (strength <= 0) continue;
      const x=96+i*31 + (stableUnit('window-smudge-x',i)-.5)*8;
      const y=190-(i%2)*6 + (stableUnit('window-smudge-y',i)-.5)*5;
      ctx.fillStyle=`rgba(226,216,196,${(.115*strength*smudgeWeather).toFixed(4)})`;
      ctx.beginPath(); ctx.ellipse(x,y,7+stableUnit('window-smudge-r',i)*3,3.2+strength*1.4,-.24+(stableUnit('window-smudge-a',i)-.5)*.18,0,Math.PI*2); ctx.fill();
    }
    const sillStrength=emergence(windowWatches,1,22);
    if (sillStrength > 0) {
      ctx.fillStyle=`rgba(59,45,38,${(.16*sillStrength).toFixed(4)})`;
      ctx.fillRect(80,215,155,2+4*sillStrength);
      ctx.fillStyle=`rgba(191,168,133,${(.055*sillStrength).toFixed(4)})`;
      ctx.fillRect(91,216,104,1);
    }
    for (let i=0;i<5;i++) {
      const strength=emergence(wetWatches,.4+i*1.3,4.5);
      if (strength <= 0) continue;
      const x=93+i*32+(stableUnit('wet-streak-x',i)-.5)*7;
      const glint=f.weather==='rain' ? .78+.22*Math.sin(now*.0012+i*1.3) : f.weather==='mist' ? .72 : .46;
      ctx.strokeStyle=`rgba(225,232,224,${(.20*strength*glint).toFixed(4)})`; ctx.lineWidth=1.4+strength*.8;
      ctx.beginPath(); ctx.moveTo(x,149); ctx.quadraticCurveTo(x+3+stableUnit('wet-streak-b',i)*4,165,x-1,182); ctx.stroke();
      if (f.weather==='rain' && strength>.3) {
        const beadY=153+((now*.018+i*27)%25);
        ctx.fillStyle=`rgba(238,242,232,${(.10*strength).toFixed(4)})`;
        ctx.fillRect(x-1,beadY,2,3);
      }
    }

    // Sleeping nook compression, pillow drift and creases all grow as
    // continuous functions of actual accumulated sleep rather than popping at
    // integer renderer thresholds. A sub-pixel cloth drift keeps old wear
    // visually integrated with the ambient room without changing world state.
    const sleepTicks = historyValue(f,'sleep_nook_ticks',now);
    const sleepBouts = historyValue(f,'sleep_nook_bouts',now);
    rounded(52, 353, 210, 74, 8, '#463a34');
    rounded(62, 362, 188, 53, 8, '#a28c70');
    const nestStrength=emergence(sleepTicks,0,18);
    if (nestStrength > 0) {
      ctx.fillStyle=`rgba(76,58,48,${(.235*nestStrength).toFixed(4)})`;
      ctx.beginPath(); ctx.ellipse(164,389,44+17*emergence(sleepBouts,0,5),15+8*nestStrength,-.08,0,Math.PI*2); ctx.fill();
    }
    const pillowShift=13*emergence(sleepBouts,0,6);
    rounded(70+pillowShift,367+4*emergence(sleepBouts,0,5),72,29,9,'#d0b992');
    for (let i=0;i<4;i++) {
      const strength=emergence(sleepTicks,1+i*3.5,8);
      if (strength <= 0) continue;
      const clothDrift=Math.sin(now*.0007+i*1.9)*.55*strength;
      ctx.strokeStyle=`rgba(93,72,57,${(.28*strength).toFixed(4)})`; ctx.lineWidth=1.2+strength*.8;
      ctx.beginPath(); ctx.moveTo(128+i*22,374+i*4+clothDrift); ctx.quadraticCurveTo(145+i*18,385+clothDrift,132+i*22,402); ctx.stroke();
    }
    ctx.fillStyle = '#6e6358'; ctx.fillRect(45, 426, 224, 8);

    // Rug / open living space.
    rounded(296, 333, 224, 91, 30, p.rug);
    ctx.strokeStyle = 'rgba(231,214,171,.20)'; ctx.lineWidth = 3;
    for (let y=351; y<413; y+=16) { ctx.beginPath(); ctx.moveTo(319,y); ctx.lineTo(497,y); ctx.stroke(); }

    // Collection shelf; items themselves are canonical world objects.
    ctx.fillStyle = '#4c372d'; ctx.fillRect(595, 61, 157, 17); ctx.fillRect(603, 78, 8, 158); ctx.fillRect(736, 78, 8, 158);
    for (const y of [118,169,220]) ctx.fillRect(603,y,141,10);
    ctx.fillStyle = 'rgba(15,10,8,.18)'; ctx.fillRect(611,87,125,31); ctx.fillRect(611,128,125,41); ctx.fillRect(611,179,125,41);

    // Activity-corner history is layered rather than counted: every paper and
    // work mark fades into the same authored composition over a different
    // history range. Stable hash offsets add organic variation with no random
    // renderer state and no authority outside the canonical counters.
    const cornerUses=historyValue(f,'activity_corner_uses',now);
    ctx.fillStyle='#4b352c'; ctx.fillRect(590,351,145,12); ctx.fillRect(604,363,9,48); ctx.fillRect(712,363,9,48);
    ctx.save(); ctx.translate(648,379); ctx.rotate(.16*emergence(cornerUses,0,28));
    ctx.fillStyle='#b99263'; ctx.fillRect(-23,-13,46,27); ctx.fillStyle='#d7c797'; ctx.fillRect(-17,-9,35,18); ctx.restore();
    for(let i=0;i<5;i++) {
      const strength=emergence(cornerUses,1+i*4.2,8);
      if(strength<=0) continue;
      const x=607+i*25+(stableUnit('paper-x',i)-.5)*7;
      const y=337-(i%2)*5+(stableUnit('paper-y',i)-.5)*5;
      const drift=Math.sin(now*.00055+i*1.4)*.35*strength;
      ctx.save();ctx.translate(x,y+drift);ctx.rotate((stableUnit('paper-r',i)-.5)*.18);
      ctx.fillStyle=`rgba(218,201,158,${(.82*strength).toFixed(4)})`;ctx.fillRect(-10,-5,22,11);
      ctx.strokeStyle=`rgba(108,82,58,${(.16*strength).toFixed(4)})`;ctx.lineWidth=.8;ctx.strokeRect(-10,-5,22,11);ctx.restore();
    }
    for(let i=0;i<7;i++) {
      const strength=emergence(cornerUses,2+i*3.2,7);
      if(strength<=0) continue;
      ctx.strokeStyle=`rgba(75,54,43,${(.46*strength).toFixed(4)})`;ctx.lineWidth=1.1;
      const x=612+i*16; ctx.beginPath();ctx.moveTo(x,344);ctx.lineTo(x+8,340+(stableUnit('work-mark-y',i)-.5)*5);ctx.stroke();
    }
    ctx.fillStyle = '#70513e'; ctx.fillRect(748, 339, 28, 36); ctx.fillStyle = '#5f7555';
    for (let i=0;i<5;i++){ ctx.beginPath(); ctx.ellipse(762 + (i-2)*7, 331 - Math.abs(i-2)*7, 9, 17, (i-2)*.35, 0, Math.PI*2); ctx.fill(); }

    // Repeated travel becomes a physical route through the room.
    drawPersistentHistory(f);

    // Persistent wear is intentionally subtle but visible.
    for (const [zone, wear] of Object.entries(f.habitat.path_wear || {})) {
      if (wear < 6) continue;
      const pos = {sleeping_nook:[118,427],window:[168,277],open_space:[405,429],collection_shelf:[682,246],activity_corner:[655,427]}[zone];
      if (!pos) continue;
      ctx.fillStyle = `rgba(42,31,25,${Math.min(.22, .035 + wear*.006)})`;
      ctx.beginPath(); ctx.ellipse(pos[0], pos[1], 33 + Math.min(18,wear), 7, 0, 0, Math.PI*2); ctx.fill();
    }

    if (f.lighting === 'night') {
      const glow = ctx.createRadialGradient(425,265,30,425,265,340);
      glow.addColorStop(0,'rgba(244,181,93,.16)'); glow.addColorStop(1,'rgba(10,16,30,.36)');
      ctx.fillStyle = glow; ctx.fillRect(0,0,800,480);
    }
    for (const d of dust) {
      const alpha = .05 + .035 * Math.sin(now*.0005 + d.phase);
      ctx.fillStyle = `rgba(248,224,169,${alpha})`; ctx.fillRect(d.x, d.y, 2, 2);
    }
  }

  function drawObject(o) {
    if (o.state === 'carried') return; // carried prop is drawn with creature
    const x=o.x, y=o.y;
    ctx.save(); ctx.translate(x,y);
    if (o.kind === 'stone') { ctx.fillStyle='#557487'; ctx.beginPath(); ctx.ellipse(0,0,11,8,-.2,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#8ba2ad'; ctx.fillRect(-3,-4,4,2); }
    else if (o.kind === 'leaf') { ctx.fillStyle='#b8773f'; ctx.beginPath(); ctx.ellipse(0,0,11,5,-.55,0,Math.PI*2); ctx.fill(); ctx.strokeStyle='#6d5135'; ctx.beginPath(); ctx.moveTo(-9,6); ctx.lineTo(9,-6); ctx.stroke(); }
    else if (o.kind === 'seed') { ctx.fillStyle='#87633d'; ctx.beginPath(); ctx.arc(0,0,7,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#5d472e'; ctx.fillRect(-5,-7,10,3); }
    else if (o.kind === 'shell') { ctx.fillStyle='#d0b6a0'; ctx.beginPath(); ctx.arc(0,0,8,0,Math.PI*2); ctx.fill(); ctx.strokeStyle='#977f70'; ctx.beginPath(); ctx.arc(0,0,4,0,Math.PI*1.7); ctx.stroke(); }
    else if (o.kind === 'thread') { ctx.strokeStyle='#9f564b'; ctx.lineWidth=3; ctx.beginPath(); ctx.arc(0,0,9,0,Math.PI*1.6); ctx.arc(4,1,6,0,Math.PI*1.7); ctx.stroke(); }
    else { ctx.fillStyle='#d8c3a8'; ctx.beginPath(); for(let i=0;i<10;i++){const r=i%2?4:9,a=-Math.PI/2+i*Math.PI/5; const px=Math.cos(a)*r,py=Math.sin(a)*r; i?ctx.lineTo(px,py):ctx.moveTo(px,py);} ctx.closePath();ctx.fill(); }
    ctx.restore();
  }

  function drawCreature(f, now) {
    const c = f.creature;
    const elapsed = Math.min(1, (now - fetchedAt) / 1500);
    const ease = elapsed * elapsed * (3 - 2 * elapsed);
    const old = previous?.creature || c;
    const x = mix(old.x, c.x, ease), baseY = mix(old.y, c.y, ease);
    const moving = Math.abs(old.x-c.x)+Math.abs(old.y-c.y) > 2 && elapsed < 1;
    const bob = c.pose === 'sleep' ? Math.sin(now*.002)*1.2 : moving ? Math.abs(Math.sin(now*.013))*5 : Math.sin(now*.004)*1.8;
    const y = baseY - bob;
    const flip = c.facing === 'left' ? -1 : 1;
    ctx.save(); ctx.translate(x,y); ctx.scale(flip,1);

    // Shadow anchors the creature to the diorama floor.
    ctx.fillStyle='rgba(30,22,20,.24)'; ctx.beginPath(); ctx.ellipse(0,19,24,7,0,0,Math.PI*2); ctx.fill();
    // Tail, body, head: a small mossy fox-like creature, not a UI avatar.
    ctx.strokeStyle='#485843'; ctx.lineWidth=10; ctx.lineCap='round'; ctx.beginPath(); ctx.moveTo(-18,2); ctx.quadraticCurveTo(-35,-8,-27,-23); ctx.stroke();
    ctx.fillStyle='#60705a'; ctx.beginPath(); ctx.ellipse(-2,2,24,20,0,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='#718267'; ctx.beginPath(); ctx.ellipse(9,-16,20,18,-.08,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='#718267'; ctx.beginPath(); ctx.moveTo(-4,-28); ctx.lineTo(2,-48); ctx.lineTo(10,-30); ctx.fill(); ctx.beginPath(); ctx.moveTo(15,-31); ctx.lineTo(26,-47); ctx.lineTo(29,-25); ctx.fill();
    ctx.fillStyle='#d9c9a3'; ctx.beginPath(); ctx.ellipse(18,-10,9,7,0,0,Math.PI*2); ctx.fill();
    // Expressions are subtle face changes.
    ctx.fillStyle='#252923';
    if (c.expression === 'sleepy' || c.pose === 'sleep') { ctx.fillRect(2,-19,7,2); ctx.fillRect(19,-20,7,2); }
    else { ctx.beginPath(); ctx.arc(6,-20,2.6,0,Math.PI*2); ctx.arc(23,-21,2.6,0,Math.PI*2); ctx.fill(); }
    ctx.fillStyle='#3d342e'; ctx.fillRect(27,-11,4,3);
    if (moving) { ctx.strokeStyle='#4b5845';ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(-8,16);ctx.lineTo(-13,25 + Math.sin(now*.014)*4);ctx.moveTo(8,16);ctx.lineTo(13,25 - Math.sin(now*.014)*4);ctx.stroke(); }
    else { ctx.fillStyle='#4b5845';ctx.fillRect(-12,15,8,13);ctx.fillRect(7,15,8,13); }
    if (c.carrying) { const obj=f.objects.find(o=>o.id===c.carrying); if(obj){ ctx.scale(flip,1); drawObject({...obj,state:'placed',x:0,y:0}); } }
    if (c.pose === 'sleep') { ctx.fillStyle='rgba(238,226,196,.72)';ctx.font='bold 14px monospace';ctx.fillText('z',28,-42);ctx.font='bold 10px monospace';ctx.fillText('z',40,-54); }
    ctx.restore();
  }

  function render(now) {
    if (!frame) {
      ctx.fillStyle='#25242b';ctx.fillRect(0,0,800,480);
      requestAnimationFrame(render); return;
    }
    drawBackground(frame, now);
    for (const o of frame.objects) drawObject(o);
    drawCreature(frame, now);
    if (debugVisible) {
      debug.hidden=false;
      debug.textContent = JSON.stringify({mode:snapshotPath?'snapshot':'live', connected, tick:frame.tick, lighting:frame.lighting, weather:frame.weather, creature:frame.creature, shelf_count:frame.habitat.shelf_count, marks:frame.habitat.marks, last_event:frame.last_event, poll_error:lastPollError}, null, 2);
    } else debug.hidden=true;
    requestAnimationFrame(render);
  }

  async function poll() {
    try {
      const response = await fetch('/api/frame', {cache:'no-store'});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const next = await response.json();
      if (next.logical_width !== 800 || next.logical_height !== 480) throw new Error('authoritative frame contract mismatch');
      if (!frame || next.tick !== frame.tick) { previous = frame; frame = next; fetchedAt = performance.now(); }
      connected=true; lastPollError=null;
    } catch (err) {
      connected=false; lastPollError=String(err);
    }
  }

  async function loadSnapshot() {
    try {
      if (!snapshotPath || !snapshotPath.startsWith('/snapshots/dev/') || !snapshotPath.endsWith('/frame.json')) throw new Error('invalid snapshot path');
      const response = await fetch(snapshotPath, {cache:'no-store'});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const next = await response.json();
      if (next.logical_width !== 800 || next.logical_height !== 480) throw new Error('snapshot frame contract mismatch');
      frame=next; previous=null; fetchedAt=performance.now(); connected=true; lastPollError=null;
    } catch (err) { connected=false; lastPollError=String(err); }
  }

  document.addEventListener('keydown', ev => { if (ev.key.toLowerCase()==='d') debugVisible=!debugVisible; });
  if (snapshotPath) loadSnapshot(); else { poll(); setInterval(poll, 700); }
  requestAnimationFrame(render);
})();
