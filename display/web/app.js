(() => {
  'use strict';
  const canvas = document.getElementById('terrarium');
  const ctx = canvas.getContext('2d', { alpha: false });
  const debug = document.getElementById('debug');
  const params = new URLSearchParams(window.location.search);
  const snapshotPath = params.get('snapshot');
  const temporalScenario = params.get('temporal');
  const temporalSequence = params.get('sequence') === '1';
  const temporalRafProbe = params.get('rafProbe') === '1';
  const temporalTimestamp = Number(params.get('t') || 0);
  const temporalDuration = Math.max(250, Math.min(5000, Number(params.get('duration') || 1800)));
  const temporalEasing = params.get('easing') === 'legacy' ? 'legacy' : 'current';
  const temporalContinuity = params.get('continuity') === 'legacy' ? 'legacy' : 'current';
  const temporalContinuityProbe = params.get('continuityProbe') === '1';
  const telemetryNode = document.createElement('pre');
  telemetryNode.id = 'temporal-telemetry';
  telemetryNode.setAttribute('aria-label', 'Terrarium temporal telemetry');
  telemetryNode.style.cssText = 'position:fixed;left:-10000px;top:0;width:1px;height:1px;overflow:hidden;white-space:pre-wrap';
  document.body.appendChild(telemetryNode);
  if (canvas.width !== 800 || canvas.height !== 480) throw new Error('Terrarium logical viewport must be exactly 800x480');
  ctx.imageSmoothingEnabled = false;

  let frame = null;
  let previous = null;
  let transitionSource = null;
  let fetchedAt = performance.now();
  let connected = false;
  let debugVisible = false;
  let lastPollError = null;
  const MOTION = Object.freeze({
    locomotion_min_ms: 1500, locomotion_max_ms: 2300, locomotion_base_ms: 1400, locomotion_px_ms: 1.4,
    activity_ms: 1250, contact_ms: 1000, placement_ms: 1450, history_ms: 1800, engagement_ms: 900,
  });
  const rain = Array.from({length: 28}, (_, i) => ({x: (i * 67) % 800, y: (i * 41) % 250, speed: 0.40 + (i % 4) * 0.10}));
  const dust = Array.from({length: 8}, (_, i) => ({x: 92 + (i * 59) % 286, y: 88 + (i * 47) % 214, phase: i * 1.7}));

  function mix(a, b, t) { return a + (b - a) * t; }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function clamp01(v) { return clamp(v, 0, 1); }
  function smooth01(v) { const t=clamp01(v); return t*t*(3-2*t); }
  function smoother01(v) { const t=clamp01(v); return t*t*t*(t*(t*6-15)+10); }
  function transitionEase(v) { return temporalEasing === 'legacy' ? smooth01(v) : smoother01(v); }
  function locomotionDuration(distance) { return clamp(MOTION.locomotion_base_ms + distance * MOTION.locomotion_px_ms, MOTION.locomotion_min_ms, MOTION.locomotion_max_ms); }
  function stagedTravel(raw) { return transitionEase((raw - .08) / .80); }
  function actionEnvelope(now, duration=MOTION.activity_ms) { if (!previous) return 1; return transitionEase((now-fetchedAt)/duration); }
  function emergence(value, start, span) { return smooth01((value-start)/Math.max(.001,span)); }
  function historyValue(f, key, now) {
    const target=Number(f.habitat.activity_aftermath?.[key] || 0);
    if (!previous || snapshotPath) return target;
    const source=Number(previous.habitat?.activity_aftermath?.[key] || 0);
    return mix(source,target,smooth01((now-fetchedAt)/MOTION.history_ms));
  }
  function activityEngagement(f, now, zone, activities) {
    const current = f.creature.zone === zone && activities.includes(f.creature.activity);
    if (!previous || snapshotPath) return current ? 1 : 0;
    const prior = previous.creature?.zone === zone && activities.includes(previous.creature?.activity);
    if (current === prior) return current ? 1 : 0;
    const t=smoother01((now-fetchedAt)/MOTION.engagement_ms);
    return current ? t : 1-t;
  }
  function causalActivityState(f, now) {
    return {
      sleep_nook: activityEngagement(f,now,'sleeping_nook',['sleep']),
      window: activityEngagement(f,now,'window',['look_outside']),
      activity_corner: activityEngagement(f,now,'activity_corner',['inspect','carry','place']),
    };
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
    const common = {
      wood:'#4a342a', woodTop:'#6b4c39', woodDark:'#34251f', cloth:'#a99170', clothLight:'#c8b38b',
      paper:'#d3c291', foliage:'#5c7053', objectShadow:'rgba(30,22,18,.24)', moss:'#60745b', mossLight:'#74896c',
    };
    if (lighting === 'night') return {...common, wall:'#2c3540', floor:'#3d342e', trim:'#59483a', glow:'#d7a45d', sky:'#17243a', rug:'#536052', ambient:'#c7a96e'};
    if (lighting === 'dawn') return {...common, wall:'#766961', floor:'#5a493c', trim:'#765b46', glow:'#efbc77', sky:'#c48073', rug:'#63705b', ambient:'#efcf98'};
    if (lighting === 'dusk') return {...common, wall:'#665a58', floor:'#574438', trim:'#705541', glow:'#e8a662', sky:'#8a6075', rug:'#626b59', ambient:'#dfb47e'};
    return {...common, wall:'#867c6b', floor:'#665240', trim:'#745845', glow:'#edc77e', sky:'#81a39e', rug:'#6c7964', ambient:'#ead6a8'};
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
    const causal = causalActivityState(f, now);
    ctx.fillStyle = p.wall; ctx.fillRect(0, 0, 800, 315);
    ctx.fillStyle = p.floor; ctx.fillRect(0, 315, 800, 165);
    // A real baseboard and quiet floor seams make the room read as one physical
    // box instead of two flat color fields. Keep them lower-contrast than Moss.
    ctx.fillStyle = p.woodDark; ctx.fillRect(0, 306, 800, 14);
    ctx.fillStyle = p.trim; ctx.fillRect(0, 306, 800, 5);
    ctx.strokeStyle='rgba(42,31,25,.10)'; ctx.lineWidth=2;
    for (const y of [357,405,453]) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(800,y); ctx.stroke(); }
    if (f.lighting !== 'night') {
      ctx.fillStyle = f.lighting === 'dusk' ? 'rgba(231,165,101,.035)' : 'rgba(239,210,156,.055)';
      ctx.beginPath(); ctx.moveTo(92,210); ctx.lineTo(245,210); ctx.lineTo(410,480); ctx.lineTo(176,480); ctx.closePath(); ctx.fill();
    }

    // Window / weather: environmental time instead of a dashboard clock.
    ctx.fillStyle='rgba(31,23,20,.16)'; ctx.fillRect(49,53,235,176);
    rounded(54, 48, 225, 172, 5, p.woodDark);
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

    // Current window watching activates the same pane and sill where persistent
    // traces accumulate. This response is grounded in canonical activity and
    // position; it is not an independent decorative animation.
    if (causal.window > 0) {
      const contactX=Math.max(88,Math.min(242,Number(f.creature.x)));
      const pulse=.86+.14*Math.sin(now*.0016);
      const wet=f.weather==='rain' || f.weather==='mist';
      ctx.fillStyle=`rgba(232,228,211,${(.075*causal.window*pulse*(wet?1.25:1)).toFixed(4)})`;
      ctx.beginPath(); ctx.ellipse(contactX,198,20+5*causal.window,6+2*causal.window,-.08,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle=`rgba(224,215,194,${(.14*causal.window).toFixed(4)})`; ctx.lineWidth=1.2;
      ctx.beginPath(); ctx.moveTo(contactX-13,216); ctx.quadraticCurveTo(contactX,213,contactX+13,216); ctx.stroke();
    }

    // Sleeping nook compression, pillow drift and creases all grow as
    // continuous functions of actual accumulated sleep rather than popping at
    // integer renderer thresholds. A sub-pixel cloth drift keeps old wear
    // visually integrated with the ambient room without changing world state.
    const sleepTicks = historyValue(f,'sleep_nook_ticks',now);
    const sleepBouts = historyValue(f,'sleep_nook_bouts',now);
    rounded(49, 356, 216, 75, 9, p.woodDark);
    rounded(54, 351, 210, 74, 9, p.wood);
    rounded(62, 362, 188, 53, 9, p.cloth);
    const nestStrength=emergence(sleepTicks,0,18);
    if (nestStrength > 0) {
      ctx.fillStyle=`rgba(76,58,48,${(.235*nestStrength).toFixed(4)})`;
      ctx.beginPath(); ctx.ellipse(164,389,44+17*emergence(sleepBouts,0,5),15+8*nestStrength,-.08,0,Math.PI*2); ctx.fill();
    }
    // Existing sleep wear physically responds while Moss is asleep in the
    // nook. The local pressure follows canonical x and breathing, while the
    // accumulated nest strength remains history-owned.
    if (causal.sleep_nook > 0) {
      const breath=.5+.5*Math.sin(now*.002);
      const pressX=Math.max(92,Math.min(214,Number(f.creature.x)+12));
      ctx.fillStyle=`rgba(62,47,40,${(.17*causal.sleep_nook*(.82+.18*breath)).toFixed(4)})`;
      ctx.beginPath(); ctx.ellipse(pressX,397+breath,31+5*breath,8+4*causal.sleep_nook,-.06,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle=`rgba(218,194,151,${(.12*causal.sleep_nook).toFixed(4)})`; ctx.lineWidth=1.1;
      ctx.beginPath(); ctx.moveTo(pressX-33,390); ctx.quadraticCurveTo(pressX-18,397+2*breath,pressX-7,401); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(pressX+10,401); ctx.quadraticCurveTo(pressX+24,396+2*breath,pressX+36,391); ctx.stroke();
    }
    const pillowShift=13*emergence(sleepBouts,0,6);
    rounded(70+pillowShift,367+4*emergence(sleepBouts,0,5),72,29,9,p.clothLight);
    for (let i=0;i<4;i++) {
      const strength=emergence(sleepTicks,1+i*3.5,8);
      if (strength <= 0) continue;
      const clothDrift=Math.sin(now*.0007+i*1.9)*.55*strength;
      ctx.strokeStyle=`rgba(93,72,57,${(.28*strength).toFixed(4)})`; ctx.lineWidth=1.2+strength*.8;
      ctx.beginPath(); ctx.moveTo(128+i*22,374+i*4+clothDrift); ctx.quadraticCurveTo(145+i*18,385+clothDrift,132+i*22,402); ctx.stroke();
    }
    ctx.fillStyle = p.woodTop; ctx.fillRect(45, 426, 224, 8);

    // Rug / open living space.
    rounded(296, 333, 224, 91, 30, p.rug);
    ctx.strokeStyle = 'rgba(225,211,176,.13)'; ctx.lineWidth = 2;
    for (let y=351; y<413; y+=16) { ctx.beginPath(); ctx.moveTo(319,y); ctx.lineTo(497,y); ctx.stroke(); }

    // Collection shelf; items themselves are canonical world objects.
    ctx.fillStyle = 'rgba(28,20,17,.16)'; ctx.fillRect(590,66,167,177);
    ctx.fillStyle = p.wood; ctx.fillRect(595, 61, 157, 17); ctx.fillRect(603, 78, 8, 158); ctx.fillRect(736, 78, 8, 158);
    ctx.fillStyle = p.woodTop; for (const y of [118,169,220]) ctx.fillRect(603,y,141,10);
    ctx.fillStyle = 'rgba(15,10,8,.14)'; ctx.fillRect(611,87,125,31); ctx.fillRect(611,128,125,41); ctx.fillRect(611,179,125,41);

    // Activity-corner history is layered rather than counted: every paper and
    // work mark fades into the same authored composition over a different
    // history range. Stable hash offsets add organic variation with no random
    // renderer state and no authority outside the canonical counters.
    const cornerUses=historyValue(f,'activity_corner_uses',now);
    ctx.fillStyle='rgba(30,22,18,.16)'; ctx.fillRect(585,358,155,59);
    ctx.fillStyle=p.woodTop; ctx.fillRect(590,351,145,12); ctx.fillStyle=p.wood; ctx.fillRect(604,363,9,48); ctx.fillRect(712,363,9,48);
    ctx.save(); ctx.translate(648,379); ctx.rotate(.16*emergence(cornerUses,0,28));
    ctx.fillStyle=p.woodTop; ctx.fillRect(-23,-13,46,27); ctx.fillStyle=p.paper; ctx.fillRect(-17,-9,35,18); ctx.restore();
    for(let i=0;i<5;i++) {
      const strength=emergence(cornerUses,1+i*4.2,8);
      if(strength<=0) continue;
      const x=607+i*25+(stableUnit('paper-x',i)-.5)*7;
      const y=337-(i%2)*5+(stableUnit('paper-y',i)-.5)*5;
      const drift=Math.sin(now*.00055+i*1.4)*.35*strength;
      const side=x < Number(f.creature.x) ? -1 : 1;
      const contactShift=causal.activity_corner*side*(.7+stableUnit('paper-contact',i)*2.2);
      const contactLift=causal.activity_corner*(i%2 ? -1.2 : -.35);
      ctx.save();ctx.translate(x+contactShift,y+drift+contactLift);ctx.rotate((stableUnit('paper-r',i)-.5)*.18 + side*.025*causal.activity_corner);
      ctx.fillStyle=`rgba(211,194,145,${(.68*strength).toFixed(4)})`;ctx.fillRect(-10,-5,22,11);
      ctx.strokeStyle=`rgba(108,82,58,${(.16*strength).toFixed(4)})`;ctx.lineWidth=.8;ctx.strokeRect(-10,-5,22,11);ctx.restore();
    }
    for(let i=0;i<7;i++) {
      const strength=emergence(cornerUses,2+i*3.2,7);
      if(strength<=0) continue;
      ctx.strokeStyle=`rgba(75,54,43,${(.46*strength).toFixed(4)})`;ctx.lineWidth=1.1;
      const x=612+i*16; ctx.beginPath();ctx.moveTo(x,344);ctx.lineTo(x+8,340+(stableUnit('work-mark-y',i)-.5)*5);ctx.stroke();
    }
    if (causal.activity_corner > 0) {
      const handX=Math.max(610,Math.min(712,Number(f.creature.x)-8));
      ctx.strokeStyle=`rgba(225,205,164,${(.18*causal.activity_corner).toFixed(4)})`; ctx.lineWidth=1.2;
      ctx.beginPath(); ctx.moveTo(handX-12,350); ctx.quadraticCurveTo(handX,346,handX+12,349); ctx.stroke();
    }
    ctx.fillStyle = p.woodTop; ctx.fillRect(748, 339, 28, 36); ctx.fillStyle = p.foliage;
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
      const alpha = .025 + .018 * Math.sin(now*.00035 + d.phase);
      ctx.fillStyle = `rgba(239,216,169,${alpha})`; ctx.fillRect(d.x, d.y, 2, 2);
    }
  }

  function placedObjectRenderState(o, f, now) {
    const source=previous?.objects?.find(item=>item.id===o.id);
    if (!snapshotPath && source?.state === 'carried' && o.state === 'placed') {
      const raw=clamp01((now-fetchedAt)/MOTION.placement_ms);
      const t=smoother01((raw-.14)/.68);
      const facing=previous?.creature?.facing === 'left' ? -1 : 1;
      const originX=(transitionSource?.x ?? Number(previous.creature.x)) + facing*22;
      const originY=(transitionSource?.y ?? Number(previous.creature.y)) - 4;
      return {
        x:mix(originX,Number(o.x),t),
        y:mix(originY,Number(o.y),t),
        progress:t,
        phase:raw < .14 ? 'prepare' : t < 1 ? 'lower-contact' : 'settled',
        transitioning:t < 1,
      };
    }
    return {x:Number(o.x),y:Number(o.y),progress:1,phase:'settled',transitioning:false};
  }

  function activePlacementState(f, now) {
    if (!previous || snapshotPath) return null;
    for (const o of f.objects || []) {
      const source=previous.objects?.find(item=>item.id===o.id);
      if (source?.state === 'carried' && o.state === 'placed') {
        const rs=placedObjectRenderState(o,f,now);
        return {object_id:o.id,rendered_x:Number(rs.x.toFixed(6)),rendered_y:Number(rs.y.toFixed(6)),target_x:Number(o.x),target_y:Number(o.y),progress:Number(rs.progress.toFixed(6)),phase:rs.phase};
      }
    }
    return null;
  }

  function drawWorldObject(o, f, now) {
    if (o.state === 'carried') return;
    const rs=placedObjectRenderState(o,f,now);
    ctx.save();
    ctx.fillStyle='rgba(30,22,18,.18)';
    ctx.beginPath(); ctx.ellipse(rs.x,rs.y+6,10,3.5,0,0,Math.PI*2); ctx.fill();
    ctx.restore();
    drawObject({...o,x:rs.x,y:rs.y});
  }

  function drawObject(o) {
    if (o.state === 'carried') return;
    const x=o.x, y=o.y;
    ctx.save(); ctx.translate(x,y);
    if (o.kind === 'stone') { ctx.fillStyle='#557487'; ctx.beginPath(); ctx.ellipse(0,0,11,8,-.2,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#8ba2ad'; ctx.fillRect(-3,-4,4,2); }
    else if (o.kind === 'leaf') { ctx.fillStyle='#b8773f'; ctx.beginPath(); ctx.ellipse(0,0,11,5,-.55,0,Math.PI*2); ctx.fill(); ctx.strokeStyle='#6d5135'; ctx.lineWidth=1.3; ctx.beginPath(); ctx.moveTo(-9,6); ctx.lineTo(9,-6); ctx.stroke(); }
    else if (o.kind === 'seed') { ctx.fillStyle='#87633d'; ctx.beginPath(); ctx.arc(0,0,7,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#5d472e'; ctx.fillRect(-5,-7,10,3); }
    else if (o.kind === 'shell') { ctx.fillStyle='#d0b6a0'; ctx.beginPath(); ctx.arc(0,0,8,0,Math.PI*2); ctx.fill(); ctx.strokeStyle='#977f70'; ctx.lineWidth=1.2; ctx.beginPath(); ctx.arc(0,0,4,0,Math.PI*1.7); ctx.stroke(); }
    else if (o.kind === 'thread') { ctx.strokeStyle='#9f564b'; ctx.lineWidth=3; ctx.beginPath(); ctx.arc(0,0,9,0,Math.PI*1.6); ctx.arc(4,1,6,0,Math.PI*1.7); ctx.stroke(); }
    else { ctx.fillStyle='#d8c3a8'; ctx.beginPath(); for(let i=0;i<10;i++){const r=i%2?4:9,a=-Math.PI/2+i*Math.PI/5; const px=Math.cos(a)*r,py=Math.sin(a)*r; i?ctx.lineTo(px,py):ctx.moveTo(px,py);} ctx.closePath();ctx.fill(); ctx.strokeStyle='rgba(86,70,59,.45)';ctx.lineWidth=1;ctx.stroke(); }
    ctx.restore();
  }

  function actionTargetObject(f) {
    const id=f.last_event?.object_id;
    if (!id) return null;
    return f.objects?.find(o=>o.id===id) || previous?.objects?.find(o=>o.id===id) || null;
  }

  function phaseName(moving, raw, activityProgress) {
    if (moving) {
      if (raw < .08) return 'anticipation';
      if (raw < .82) return 'movement';
      if (raw < .94) return 'settle';
      return 'recovery';
    }
    if (activityProgress < .18) return 'anticipation';
    if (activityProgress < .62) return 'contact';
    if (activityProgress < .88) return 'settle';
    return 'hold';
  }

  function creatureRenderState(f, now) {
    const c = f.creature;
    const old = previous?.creature || c;
    const sourceX = Number(transitionSource?.x ?? old.x);
    const sourceY = Number(transitionSource?.y ?? old.y);
    const semanticDistance = Math.hypot(Number(c.x)-sourceX, Number(c.y)-sourceY);
    const duration = locomotionDuration(semanticDistance);
    const raw = clamp01((now-fetchedAt)/duration);
    const travel = semanticDistance > 2 ? stagedTravel(raw) : 1;
    const x = mix(sourceX, Number(c.x), travel), baseY = mix(sourceY, Number(c.y), travel);
    const moving = semanticDistance > 2 && travel < 1;
    const activityProgress=actionEnvelope(now);
    const target=actionTargetObject(f);
    let renderedFacing=c.facing;
    if (!moving && target && ['inspect','carry','place'].includes(c.activity) && Math.abs(Number(target.x)-x)>3) renderedFacing=Number(target.x)>=x?'right':'left';
    const direction=renderedFacing==='left'?-1:1;
    const strideCount=Math.max(2,Math.round(semanticDistance/58));
    const walkPhase=travel*Math.PI*2*strideCount;
    const walkBob=moving ? Math.abs(Math.sin(walkPhase))*2.15 : 0;
    const sleepBreath=c.pose==='sleep' ? Math.sin(now*.0017)*.55 : 0;
    const idleBreath=!moving && c.pose!=='sleep' ? Math.sin(now*.00115)*.55 : 0;
    const bob=walkBob+sleepBreath+idleBreath;
    const y=baseY-bob;
    const pickupSource=c.carrying ? previous?.objects?.find(o=>o.id===c.carrying && o.state==='placed') : null;
    const attachmentProgress=pickupSource ? smoother01((activityProgress-.24)/.46) : (c.carrying ? 1 : 0);
    const holdX=direction*22, holdY=-4;
    const attached=Boolean(c.carrying) && attachmentProgress>=.96;
    let carriedWorldX=null, carriedWorldY=null;
    if (c.carrying) {
      const targetHoldX=x+holdX, targetHoldY=baseY+holdY;
      carriedWorldX=pickupSource ? mix(Number(pickupSource.x),targetHoldX,attachmentProgress) : targetHoldX;
      carriedWorldY=pickupSource ? mix(Number(pickupSource.y),targetHoldY,attachmentProgress) : targetHoldY;
    }
    const causal=causalActivityState(f,now);
    return {
      requested_timestamp_ms: now,
      source_tick: previous?.tick ?? f.tick,
      target_tick: f.tick,
      semantic_x: c.x, semantic_y: c.y,
      source_x: sourceX, source_y: sourceY,
      rendered_x: Number(x.toFixed(6)), rendered_y: Number(y.toFixed(6)),
      rendered_base_y: Number(baseY.toFixed(6)),
      interpolation_progress: Number(raw.toFixed(6)),
      interpolation_ease: Number(travel.toFixed(9)),
      motion_duration_ms: Number(duration.toFixed(3)),
      activity_progress: Number(activityProgress.toFixed(6)),
      motion_phase: phaseName(moving,raw,activityProgress),
      semantic_distance: Number(semanticDistance.toFixed(6)),
      moving, facing: renderedFacing, pose: c.pose, activity: c.activity,
      carrying: attached ? c.carrying : null,
      carrying_semantic: c.carrying,
      attachment_progress: Number(attachmentProgress.toFixed(6)),
      carried_rendered_x: carriedWorldX===null ? null : Number(carriedWorldX.toFixed(6)),
      carried_rendered_y: carriedWorldY===null ? null : Number(carriedWorldY.toFixed(6)),
      carried_relative_x: attached ? holdX : null,
      carried_relative_y: attached ? holdY : null,
      walk_phase: Number(walkPhase.toFixed(6)),
      causal_activity: {
        sleep_nook: Number(causal.sleep_nook.toFixed(6)),
        window: Number(causal.window.toFixed(6)),
        activity_corner: Number(causal.activity_corner.toFixed(6)),
      },
      object_placement: activePlacementState(f,now),
      ambient_classes: [f.weather === 'rain' ? 'rain' : f.weather === 'mist' ? 'mist' : null, 'window-motes', c.pose === 'sleep' ? 'breathing' : moving ? 'walk-cycle' : 'quiet-breathing', causal.sleep_nook>0?'bedding-contact':null, causal.window>0?'window-contact':null, causal.activity_corner>0?'work-surface-contact':null].filter(Boolean),
    };
  }

  function drawCreature(f, now) {
    const c=f.creature;
    const rs=creatureRenderState(f,now);
    const p=palette(f.lighting);
    const x=rs.rendered_x, y=rs.rendered_y, moving=rs.moving;
    const flip=rs.facing==='left'?-1:1;
    const ap=rs.activity_progress;
    const prior=previous?.creature?.activity;
    let sleepBlend=0;
    if (c.activity==='sleep') sleepBlend=prior==='sleep' ? 1 : smoother01((ap-.12)/.58);
    else if (prior==='sleep') sleepBlend=1-smoother01((ap-.10)/.68);
    const inspectBlend=c.activity==='inspect' ? smoother01((ap-.10)/.42) : prior==='inspect' ? 1-smoother01(ap/.34) : 0;
    const windowBlend=c.activity==='look_outside' ? smoother01((ap-.12)/.48) : prior==='look_outside' ? 1-smoother01(ap/.38) : 0;
    const carryReach=c.activity==='carry' ? smoother01((ap-.08)/.50) : 0;
    const placeReach=c.activity==='place' ? smoother01((ap-.08)/.42) * (1-smoother01((ap-.78)/.22)) : 0;
    const restBlend=['idle','rest'].includes(c.activity) && !moving ? .55 : 0;
    const lean=inspectBlend*.08 + windowBlend*.06 + carryReach*.035;
    const bodyDrop=restBlend*2 + sleepBlend*8;
    const headX=9 + inspectBlend*4 + windowBlend*3 + sleepBlend*6;
    const headY=-16 + bodyDrop + sleepBlend*8;

    ctx.save(); ctx.translate(x,y); ctx.scale(flip,1);
    ctx.fillStyle='rgba(28,21,18,.25)';
    ctx.beginPath(); ctx.ellipse(-3,21+sleepBlend*3,24+sleepBlend*10,6.5-sleepBlend*1.2,0,0,Math.PI*2); ctx.fill();

    // Tail is the strongest silhouette cue. It curls lower and forward during sleep.
    ctx.strokeStyle='#465642'; ctx.lineWidth=12; ctx.lineCap='round';
    ctx.beginPath(); ctx.moveTo(-18,4+bodyDrop*.25);
    ctx.quadraticCurveTo(-38,-4+sleepBlend*16,-30,-24+sleepBlend*29);
    ctx.stroke();
    ctx.strokeStyle='#64765e'; ctx.lineWidth=4;
    ctx.beginPath(); ctx.moveTo(-23,1+bodyDrop*.25); ctx.quadraticCurveTo(-35,-4+sleepBlend*15,-30,-19+sleepBlend*26); ctx.stroke();

    ctx.save(); ctx.translate(0,bodyDrop); ctx.rotate(lean-.075*sleepBlend);
    ctx.fillStyle=p.moss;
    ctx.beginPath(); ctx.ellipse(-2,2,25+sleepBlend*7,20-sleepBlend*4,0,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='#7f8e70';
    ctx.beginPath(); ctx.ellipse(7,7,12+sleepBlend*5,8,0,0,Math.PI*2); ctx.fill();
    ctx.restore();

    ctx.save(); ctx.translate(headX,headY); ctx.rotate(lean*.45-.05*sleepBlend);
    ctx.fillStyle=p.mossLight;
    ctx.beginPath(); ctx.ellipse(0,0,20+sleepBlend*1.5,18-sleepBlend*1.5,-.06,0,Math.PI*2); ctx.fill();
    ctx.fillStyle=p.mossLight;
    ctx.beginPath(); ctx.moveTo(-13,-11+sleepBlend*4); ctx.lineTo(-8,-30+sleepBlend*10); ctx.lineTo(-1,-13+sleepBlend*3); ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.moveTo(7,-13+sleepBlend*4); ctx.lineTo(18,-29+sleepBlend*10); ctx.lineTo(18,-9+sleepBlend*3); ctx.closePath(); ctx.fill();
    ctx.fillStyle='#d6c59d';
    ctx.beginPath(); ctx.ellipse(10,6,9,7,0,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='#252923';
    if (sleepBlend>.45 || c.expression==='sleepy') {
      ctx.fillRect(-6,-3,7,2); ctx.fillRect(7,-4,7,2);
    } else {
      const gaze=actionTargetObject(f) ? 1.0 : 0;
      ctx.beginPath(); ctx.arc(-2+gaze,-4,2.6,0,Math.PI*2); ctx.arc(11+gaze,-5,2.6,0,Math.PI*2); ctx.fill();
    }
    ctx.fillStyle='#3c332d'; ctx.fillRect(17,6,4,3);
    ctx.restore();

    if (sleepBlend<.72) {
      ctx.strokeStyle='#475642'; ctx.lineWidth=5.5; ctx.lineCap='round';
      ctx.beginPath();
      if (moving) {
        const stride=Math.sin(rs.walk_phase)*5.5;
        ctx.moveTo(-10,15+bodyDrop*.35); ctx.lineTo(-12-stride,26);
        ctx.moveTo(8,15+bodyDrop*.35); ctx.lineTo(11+stride,26);
      } else {
        ctx.moveTo(-10,15+bodyDrop*.35); ctx.lineTo(-11,26-bodyDrop*.15);
        ctx.moveTo(8,15+bodyDrop*.35); ctx.lineTo(10,26-bodyDrop*.15);
      }
      ctx.stroke();
      const reach=Math.max(inspectBlend*.75,carryReach,placeReach);
      if (reach>.02) {
        ctx.strokeStyle='#566650'; ctx.lineWidth=5; ctx.beginPath();
        ctx.moveTo(10,5+bodyDrop*.35); ctx.lineTo(18+reach*7,8+placeReach*11); ctx.stroke();
      }
    }
    ctx.restore();

    if (c.carrying) {
      const obj=f.objects.find(o=>o.id===c.carrying) || previous?.objects?.find(o=>o.id===c.carrying);
      if (obj && rs.carried_rendered_x!==null) drawObject({...obj,state:'placed',x:rs.carried_rendered_x,y:rs.carried_rendered_y});
    }
    return rs;
  }

  function drawForegroundCausality(f, now, rs) {
    const causal=causalActivityState(f,now);
    // A shallow blanket lip crosses Moss's lower body only while sleeping in
    // the nook, providing a foreground contact/depth cue without new state.
    if (causal.sleep_nook > 0) {
      const x=rs.rendered_x, y=rs.rendered_base_y;
      ctx.save();
      ctx.fillStyle=`rgba(180,153,116,${(.72*causal.sleep_nook).toFixed(4)})`;
      ctx.beginPath(); ctx.moveTo(x-31,y+9); ctx.quadraticCurveTo(x-3,y+18,x+35,y+12); ctx.lineTo(x+35,y+24); ctx.quadraticCurveTo(x,y+29,x-31,y+21); ctx.closePath(); ctx.fill();
      ctx.strokeStyle=`rgba(94,72,57,${(.28*causal.sleep_nook).toFixed(4)})`; ctx.lineWidth=1.2;
      ctx.beginPath(); ctx.moveTo(x-27,y+14); ctx.quadraticCurveTo(x+1,y+20,x+31,y+15); ctx.stroke();
      ctx.restore();
    }
  }

  function render(now, scheduleNext = true) {
    if (!frame) {
      ctx.fillStyle='#25242b';ctx.fillRect(0,0,800,480);
      if (scheduleNext) requestAnimationFrame(render); return null;
    }
    drawBackground(frame, now);
    for (const o of frame.objects) drawWorldObject(o,frame,now);
    const renderState = drawCreature(frame, now);
    drawForegroundCausality(frame, now, renderState);
    if (debugVisible) {
      debug.hidden=false;
      debug.textContent = JSON.stringify({mode:snapshotPath?'snapshot':'live', connected, tick:frame.tick, lighting:frame.lighting, weather:frame.weather, creature:frame.creature, shelf_count:frame.habitat.shelf_count, marks:frame.habitat.marks, last_event:frame.last_event, poll_error:lastPollError}, null, 2);
    } else debug.hidden=true;
    if (scheduleNext) requestAnimationFrame(render);
    return renderState;
  }

  async function rasterTelemetry() {
    const image = ctx.getImageData(0,0,800,480);
    let h=2166136261;
    for (let i=0;i<image.data.length;i+=4) {
      h^=image.data[i]; h=Math.imul(h,16777619);
      h^=image.data[i+1]; h=Math.imul(h,16777619);
      h^=image.data[i+2]; h=Math.imul(h,16777619);
      h^=image.data[i+3]; h=Math.imul(h,16777619);
    }
    const pixelHash=`fnv1a32:${(h>>>0).toString(16).padStart(8,'0')}`;
    const gridW=20, gridH=12, cellW=40, cellH=40, grid=[];
    for(let gy=0;gy<gridH;gy++) {
      for(let gx=0;gx<gridW;gx++) {
        let total=0,count=0;
        for(let y=gy*cellH;y<(gy+1)*cellH;y+=4) for(let x=gx*cellW;x<(gx+1)*cellW;x+=4) {
          const i=(y*800+x)*4; total += image.data[i]*.2126 + image.data[i+1]*.7152 + image.data[i+2]*.0722; count++;
        }
        grid.push(Number((total/count).toFixed(3)));
      }
    }
    return {width:800,height:480,pixel_hash:pixelHash,luma_grid_width:gridW,luma_grid_height:gridH,luma_grid:grid};
  }

  function publishTemporal(payload) {
    window.__terrariumTemporalResult = payload;
    telemetryNode.textContent = JSON.stringify(payload);
    document.title = `Terrarium Temporal ${payload.status || 'ready'}`;
    fetch('/api/dev/temporal-evidence', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).catch(()=>{});
  }

  async function captureTemporalSample(timestamp) {
    const state = render(timestamp, false);
    const raster = await rasterTelemetry();
    return {...state, raster};
  }

  function acceptFrame(next, now) {
    if (!frame) { frame=next; previous=null; transitionSource=null; fetchedAt=now; return; }
    if (next.tick === frame.tick) return;
    const current=creatureRenderState(frame,now);
    const source=temporalContinuity==='legacy' ? null : {x:current.rendered_x,y:current.rendered_base_y};
    previous=frame; frame=next; transitionSource=source; fetchedAt=now;
  }

  async function poll() {
    try {
      const response = await fetch('/api/frame', {cache:'no-store'});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const next = await response.json();
      if (next.logical_width !== 800 || next.logical_height !== 480) throw new Error('authoritative frame contract mismatch');
      acceptFrame(next,performance.now());
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
      frame=next; previous=null; transitionSource=null; fetchedAt=performance.now(); connected=true; lastPollError=null;
    } catch (err) { connected=false; lastPollError=String(err); }
  }

  async function loadTemporalScenario() {
    try {
      const response = await fetch('/api/dev/temporal-fixtures', {cache:'no-store'});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const pack = await response.json();
      if (temporalContinuityProbe) {
        const probe=pack.continuity_probe;
        if (!probe) throw new Error('continuity probe fixture is missing');
        previous=probe.source; frame=probe.middle; transitionSource=null; fetchedAt=0; connected=true; lastPollError=null;
        const interrupt=Number(probe.interrupt_ms || 1000);
        const before=await captureTemporalSample(interrupt);
        acceptFrame(probe.followup,interrupt);
        const after=await captureTemporalSample(interrupt);
        const jump=Math.hypot(after.rendered_x-before.rendered_x,after.rendered_base_y-before.rendered_base_y);
        publishTemporal({
          schema:'terrarium.continuity-probe.v1',status:'ready',scenario:'continuity_probe',easing:temporalContinuity,continuity:temporalContinuity,
          interrupt_ms:interrupt,source_tick:probe.source.tick,middle_tick:probe.middle.tick,followup_tick:probe.followup.tick,
          first_event:probe.first_event,second_event:probe.second_event,jump_px:Number(jump.toFixed(6)),before,after
        });
        return;
      }
      const scenario = pack.scenarios?.[temporalScenario];
      if (!scenario) throw new Error(`unknown temporal scenario: ${temporalScenario}`);
      previous=scenario.source; frame=scenario.target; transitionSource=null; fetchedAt=0; connected=true; lastPollError=null;
      if (frame.logical_width !== 800 || frame.logical_height !== 480 || previous.logical_width !== 800 || previous.logical_height !== 480) throw new Error('temporal fixture frame contract mismatch');
      if (temporalRafProbe) {
        const intervals=[]; let last=null; let start=null; let frames=0;
        await new Promise(resolve => {
          function probe(ts) {
            if (start === null) start=ts;
            if (last !== null) intervals.push(ts-last);
            last=ts; frames++;
            render(ts-start,false);
            if (ts-start >= temporalDuration) resolve(); else requestAnimationFrame(probe);
          }
          requestAnimationFrame(probe);
        });
        const sorted=[...intervals].sort((a,b)=>a-b);
        const pct=p=>sorted.length ? sorted[Math.min(sorted.length-1,Math.floor((sorted.length-1)*p))] : 0;
        publishTemporal({
          schema:'terrarium.raf-probe.v1',status:'ready',scenario:temporalScenario,frames,
          duration_ms:Number((last-start).toFixed(3)),interval_count:intervals.length,
          interval_ms:{min:Number((sorted[0]||0).toFixed(3)),p50:Number(pct(.5).toFixed(3)),p95:Number(pct(.95).toFixed(3)),max:Number((sorted.at(-1)||0).toFixed(3)),over_34ms:intervals.filter(v=>v>34).length,over_50ms:intervals.filter(v=>v>50).length},
          intervals_ms:intervals.map(v=>Number(v.toFixed(3)))
        });
        return;
      }
      if (temporalSequence) {
        const timestamps=pack.recommended_timestamps_ms || [0,250,500,750,1000,1250,1500];
        const samples=[];
        for (const t of timestamps) samples.push(await captureTemporalSample(Number(t)));
        publishTemporal({schema:'terrarium.temporal-capture.v1',status:'ready',scenario:temporalScenario,easing:temporalEasing,source_tick:scenario.source_tick,target_tick:scenario.target_tick,semantic_event:scenario.semantic_event,samples});
        return;
      }
      const sample=await captureTemporalSample(temporalTimestamp);
      publishTemporal({schema:'terrarium.temporal-keyframe.v1',status:'ready',scenario:temporalScenario,easing:temporalEasing,source_tick:scenario.source_tick,target_tick:scenario.target_tick,semantic_event:scenario.semantic_event,sample});
    } catch (err) {
      connected=false; lastPollError=String(err); publishTemporal({schema:'terrarium.temporal-error.v1',status:'error',error:String(err)});
    }
  }

  document.addEventListener('keydown', ev => { if (ev.key.toLowerCase()==='d') debugVisible=!debugVisible; });
  if (temporalScenario) loadTemporalScenario();
  else if (snapshotPath) { loadSnapshot(); requestAnimationFrame(render); }
  else { poll(); setInterval(poll, 700); requestAnimationFrame(render); }
})();
