(() => {
  'use strict';

  const DISPLAY_W = 800;
  const DISPLAY_H = 480;
  const ART_W = 400;
  const ART_H = 240;
  const SCALE = 2;

  const canvas = document.getElementById('terrarium');
  const displayCtx = canvas.getContext('2d', { alpha: false });
  const artCanvas = document.createElement('canvas');
  artCanvas.width = ART_W;
  artCanvas.height = ART_H;
  const ctx = artCanvas.getContext('2d', { alpha: false });
  const debug = document.getElementById('debug');

  if (canvas.width !== DISPLAY_W || canvas.height !== DISPLAY_H) throw new Error('Terrarium logical viewport must be exactly 800x480');
  if (artCanvas.width !== ART_W || artCanvas.height !== ART_H) throw new Error('Terrarium art surface must be exactly 400x240');
  ctx.imageSmoothingEnabled = false;
  displayCtx.imageSmoothingEnabled = false;

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

  let frame = null;
  let previous = null;
  let transitionSource = null;
  let fetchedAt = performance.now();
  let activityStartedAt = fetchedAt;
  let connected = false;
  let debugVisible = false;
  let lastPollError = null;

  const MOTION = Object.freeze({
    locomotion_min_ms: 1500, locomotion_max_ms: 2300, locomotion_base_ms: 1400, locomotion_px_ms: 1.4,
    activity_ms: 1300, contact_ms: 1200, placement_ms: 2200, history_ms: 1800, engagement_ms: 1200, environment_ms: 3000,
  });
  const ACTION_DURATION = Object.freeze({
    idle: 950, rest: 1450, inspect: 1800, carry: 1900, place: 2200,
    look_outside: 1700, sleep: 2200, wake: 2000, walk: 1300,
  });

  // Deliberately finite, reusable palette families. Environmental changes swap
  // and step these colors; they never introduce gradients or bloom.
  const PALETTES = Object.freeze({
    day: {
      wall:'#a48b6a', wallShade:'#8a7155', wallLight:'#c0a27a', floor:'#785638', floorShade:'#60422f', floorLight:'#916947',
      walnut:'#533824', walnutDark:'#352519', walnutLight:'#765236', cream:'#e5cf9f', creamShade:'#c3aa7d', moss:'#66774b', mossDark:'#435437',
      amber:'#d39a4a', sky:'#7eaaa6', skyDark:'#557c7e', dustyBlue:'#668399', rain:'#b0c7c0', shadow:'#2e241d', paper:'#d7c493',
      dog:'#8b5d3b', dogDark:'#5f3c29', dogLight:'#b47c50', dogCream:'#d9bd8d', eye:'#2d241e', rug:'#66754e', rugLight:'#819064', foliage:'#536b42',
    },
    dawn: {
      wall:'#967b69', wallShade:'#765d52', wallLight:'#b49378', floor:'#684b37', floorShade:'#51392e', floorLight:'#805c44',
      walnut:'#513523', walnutDark:'#332319', walnutLight:'#714c34', cream:'#ddc494', creamShade:'#b99c73', moss:'#61704b', mossDark:'#414f38',
      amber:'#d59655', sky:'#b77b70', skyDark:'#765c68', dustyBlue:'#6d758c', rain:'#a9b9b4', shadow:'#2c2220', paper:'#ceb786',
      dog:'#84583c', dogDark:'#5b3a2a', dogLight:'#aa744f', dogCream:'#d0b382', eye:'#2b2421', rug:'#626f51', rugLight:'#788263', foliage:'#536643',
    },
    dusk: {
      wall:'#78645f', wallShade:'#604d4b', wallLight:'#92766e', floor:'#604331', floorShade:'#493128', floorLight:'#79533c',
      walnut:'#4b3022', walnutDark:'#302019', walnutLight:'#684631', cream:'#cfae82', creamShade:'#aa8969', moss:'#59664a', mossDark:'#3c4738',
      amber:'#ce864b', sky:'#865d78', skyDark:'#54465f', dustyBlue:'#606b83', rain:'#9caeac', shadow:'#282022', paper:'#c2a97f',
      dog:'#79503a', dogDark:'#52362a', dogLight:'#9e6a4d', dogCream:'#c3a57e', eye:'#292326', rug:'#59624d', rugLight:'#6f785d', foliage:'#4d5d42',
    },
    night: {
      wall:'#3e4650', wallShade:'#303640', wallLight:'#535b62', floor:'#49382f', floorShade:'#342925', floorLight:'#5a4538',
      walnut:'#422c21', walnutDark:'#2b201b', walnutLight:'#5c4030', cream:'#b69c79', creamShade:'#927a62', moss:'#4d5b46', mossDark:'#354039',
      amber:'#c78647', sky:'#1d2a43', skyDark:'#131c30', dustyBlue:'#4f637c', rain:'#8299a0', shadow:'#211d22', paper:'#ad9473',
      dog:'#6c4937', dogDark:'#4a3329', dogLight:'#8d624a', dogCream:'#ae9374', eye:'#201f24', rug:'#4d5948', rugLight:'#63705a', foliage:'#414f3d',
    },
  });

  const rain = Array.from({length: 22}, (_, i) => ({x:(i*37)%194, y:(i*29)%72, phase:(i*7)%17}));
  const motes = Array.from({length: 9}, (_, i) => ({x:45+(i*47)%310, y:35+(i*31)%125, phase:i*1.7}));

  function mix(a,b,t){ return a+(b-a)*t; }
  function clamp(v,lo,hi){ return Math.max(lo,Math.min(hi,v)); }
  function clamp01(v){ return clamp(v,0,1); }
  function smooth01(v){ const t=clamp01(v); return t*t*(3-2*t); }
  function smoother01(v){ const t=clamp01(v); return t*t*t*(t*(t*6-15)+10); }
  function settled01(v){ const t=clamp01(v); return t*t*t*t*(35-84*t+70*t*t-20*t*t*t); }
  function transitionEase(v){ return temporalEasing==='legacy' ? smooth01(v) : settled01(v); }
  function locomotionDuration(distance){ return clamp(MOTION.locomotion_base_ms+distance*MOTION.locomotion_px_ms,MOTION.locomotion_min_ms,MOTION.locomotion_max_ms); }
  function stagedTravel(raw){ return transitionEase((raw-.08)/.80); }
  function actionEnvelope(now,activity){ if(!previous) return 1; const duration=ACTION_DURATION[activity]||MOTION.activity_ms; return transitionEase((now-activityStartedAt)/duration); }
  function emergence(value,start,span){ return smooth01((value-start)/Math.max(.001,span)); }
  function px(v){ return Math.round(Number(v)/SCALE); }
  function snapDisplay(v){ return px(v)*SCALE; }
  function rect(x,y,w,h,color){ ctx.fillStyle=color; ctx.fillRect(Math.round(x),Math.round(y),Math.max(1,Math.round(w)),Math.max(1,Math.round(h))); }
  function stableUnit(label,index){
    let h=2166136261; const text=`${label}:${index}`;
    for(let i=0;i<text.length;i++){ h^=text.charCodeAt(i); h=Math.imul(h,16777619); }
    return (h>>>0)/4294967295;
  }

  function historyValue(f,key,now){
    const target=Number(f.habitat.activity_aftermath?.[key]||0);
    if(!previous||snapshotPath) return target;
    const source=Number(previous.habitat?.activity_aftermath?.[key]||0);
    return mix(source,target,smooth01((now-fetchedAt)/MOTION.history_ms));
  }
  function activityEngagement(f,now,zone,activities){
    const current=f.creature.zone===zone&&activities.includes(f.creature.activity);
    if(!previous||snapshotPath) return current?1:0;
    const prior=previous.creature?.zone===zone&&activities.includes(previous.creature?.activity);
    if(current===prior) return current?1:0;
    const t=smoother01((now-fetchedAt)/MOTION.engagement_ms);
    return current?t:1-t;
  }
  function causalActivityState(f, now) {
    return {
      sleep_nook:activityEngagement(f,now,'sleeping_nook',['sleep']),
      window:activityEngagement(f,now,'window',['look_outside']),
      activity_corner:activityEngagement(f,now,'activity_corner',['inspect','carry','place']),
    };
  }

  function worldMinuteAt(f,now){
    const target=Number(f.world_minutes||0);
    if(!previous||snapshotPath) return target;
    const source=Number(previous.world_minutes??target);
    let delta=target-source; if(delta<-720) delta+=1440; if(delta>720) delta-=1440;
    return source+delta*smoother01((now-fetchedAt)/MOTION.environment_ms);
  }
  function visualLighting(f,now){
    const minute=((worldMinuteAt(f,now)%1440)+1440)%1440;
    // Four deliberate palette steps through each one-hour boundary. This keeps
    // environmental change calm while retaining a finite pixel-art palette.
    const transitions=[[360,'night','dawn'],[480,'dawn','day'],[1050,'day','dusk'],[1170,'dusk','night']];
    for(const [center,from,to] of transitions){
      if(minute>=center-30&&minute<center+30){
        const q=Math.floor(clamp01((minute-(center-30))/60)*4);
        return {palette: q<2 ? PALETTES[from] : PALETTES[to], night: to==='night'&&q>=2 ? 1 : from==='night'&&q<2 ? 1 : 0, minute};
      }
    }
    return {palette:PALETTES[f.lighting]||PALETTES.day,night:f.lighting==='night'?1:0,minute};
  }

  function drawPixelLine(x0,y0,x1,y1,color,thickness=1){
    x0=Math.round(x0); y0=Math.round(y0); x1=Math.round(x1); y1=Math.round(y1);
    const dx=Math.abs(x1-x0), sx=x0<x1?1:-1, dy=-Math.abs(y1-y0), sy=y0<y1?1:-1;
    let err=dx+dy;
    while(true){ rect(x0-Math.floor(thickness/2),y0-Math.floor(thickness/2),thickness,thickness,color); if(x0===x1&&y0===y1) break; const e2=2*err; if(e2>=dy){err+=dy;x0+=sx;} if(e2<=dx){err+=dx;y0+=sy;} }
  }

  function drawPersistentHistory(f,p){
    const wear=f.habitat.path_wear||{};
    const routes={sleeping_nook:[[201,210],[137,206],[77,214]],window:[[201,210],[143,170],[91,153]],collection_shelf:[[201,210],[273,171],[325,152]],activity_corner:[[201,210],[267,205],[325,214]]};
    for(const [zone,points] of Object.entries(routes)){
      const visits=Number(wear[zone]||0); if(visits<5) continue;
      const count=Math.min(9,2+Math.floor(visits/4));
      for(let i=0;i<count;i++){
        const t=(i+1)/(count+1); const u=1-t;
        const x=u*u*points[0][0]+2*u*t*points[1][0]+t*t*points[2][0];
        const y=u*u*points[0][1]+2*u*t*points[1][1]+t*t*points[2][1];
        rect(x-2,y+(i%2),4+(visits>18?2:0),1,p.floorShade);
        if(i%3===0) rect(x,y-1,2,1,p.floorLight);
      }
    }
    for(const o of f.objects||[]){
      const moved=Number(o.times_moved||0); if(o.state!=='placed'||moved<2) continue;
      const x=px(o.x),y=px(o.y); rect(x-5,y+3,10,2,p.shadow); if(moved>5) rect(x-3,y+2,6,1,p.floorShade);
    }
  }

  function drawWindow(f,now,p){
    rect(22,23,121,91,p.walnutDark); rect(25,26,115,85,p.walnut); rect(31,30,103,75,p.sky);
    rect(81,30,4,75,p.skyDark); rect(31,65,103,4,p.skyDark);
    // Tiny stepped sun/moon clusters instead of circles.
    if(f.lighting==='night'){ rect(108,41,10,8,p.cream); rect(105,44,13,5,p.cream); rect(111,39,4,2,p.cream); }
    else { rect(105,39,14,10,p.amber); rect(102,42,20,5,p.amber); rect(109,36,6,3,p.cream); }
    // Curtains: irregular stair-steps, not smooth drapery.
    rect(24,27,8,79,p.creamShade); rect(20,31,7,68,p.cream); rect(17,38,5,48,p.creamShade); rect(132,27,8,79,p.creamShade); rect(139,32,7,66,p.cream); rect(146,39,4,47,p.creamShade);
    for(let y=34;y<98;y+=13){ rect(21,y,9,2,p.wallShade); rect(136,y+3,9,2,p.wallShade); }
    rect(27,105,112,6,p.walnutLight); rect(24,111,118,4,p.walnutDark);

    if(f.weather==='rain'){
      const phase=Math.floor(now/120)%17;
      for(const d of rain){ const x=34+d.x%96; const y=31+((d.y+phase+d.phase)%68); rect(x,y,1,4,p.rain); rect(x-1,y+4,1,2,p.rain); }
    } else if(f.weather==='mist'){
      for(let y=45;y<91;y+=11) for(let x=35+(y%3);x<129;x+=17) rect(x,y,10,2,p.rain);
    }

    const watches=historyValue(f,'window_watches',now), wet=historyValue(f,'wet_window_watches',now);
    for(let i=0;i<6;i++){
      const strength=emergence(watches,1+i*2.5,6); if(strength<=0) continue;
      const x=47+i*13+(stableUnit('smudge',i)>.5?1:0), y=91-(i%2)*3;
      rect(x,y,5,1,p.creamShade); if(strength>.55) rect(x+1,y+1,4,1,p.skyDark);
    }
    for(let i=0;i<5;i++){
      const strength=emergence(wet,.4+i*1.3,4.5); if(strength<=0) continue;
      const x=45+i*16; rect(x,75,1,8,p.rain); rect(x+1,83,1,4,p.rain);
    }
    if(causalActivityState(f,now).window>0){ const cx=clamp(px(f.creature.x),44,121); rect(cx-8,101,16,2,p.creamShade); rect(cx-4,103,8,1,p.walnutLight); }
  }

  function drawBed(f,now,p){
    rect(23,177,111,40,p.walnutDark); rect(27,174,105,38,p.walnut); rect(31,181,95,28,p.creamShade);
    rect(34,184,39,13,p.cream); rect(37,187,33,8,p.creamShade);
    // Hand-authored blanket clusters.
    rect(76,183,48,22,p.dustyBlue); rect(72,188,53,16,p.dustyBlue); rect(83,181,39,5,p.dustyBlue);
    rect(78,187,20,2,p.creamShade); rect(103,193,18,2,p.skyDark); rect(75,200,33,2,p.skyDark);
    const sleepTicks=historyValue(f,'sleep_nook_ticks',now), sleepBouts=historyValue(f,'sleep_nook_bouts',now);
    const nest=emergence(sleepTicks,0,18); if(nest>0){ rect(77,196,43+Math.floor(8*emergence(sleepBouts,0,5)),5,p.walnutDark); rect(84,194,24,2,p.floorShade); }
    for(let i=0;i<4;i++){ const s=emergence(sleepTicks,1+i*3.5,8); if(s>.2){ rect(65+i*12,187+i*2,8,1,p.walnutLight); rect(70+i*10,193+i,6,1,p.skyDark); } }
    rect(22,213,113,5,p.walnutLight);
  }

  function drawRug(p){
    // Large open moss-green center assembled as stepped rows.
    const rows=[[154,173,92],[149,177,102],[146,181,108],[145,185,110],[145,189,110],[147,193,106],[151,197,98],[157,201,86],[165,205,70]];
    for(const [x,y,w] of rows) rect(x,y,w,4,p.rug);
    for(let x=163;x<238;x+=18){ rect(x,181+(x%3),10,1,p.rugLight); rect(x+5,196-(x%4),8,1,p.mossDark); }
    rect(158,176,84,1,p.rugLight); rect(164,204,70,1,p.mossDark);
  }

  function drawShelf(f,p){
    rect(295,30,84,91,p.shadow); rect(298,29,79,10,p.walnut); rect(301,39,5,79,p.walnutDark); rect(369,39,5,79,p.walnutDark);
    for(const y of [59,84,109]){ rect(304,y,68,6,p.walnutLight); rect(306,y+6,65,3,p.walnutDark); }
    // Books/knickknacks are decorative fixed clusters; canonical movable items are drawn separately.
    const books=[[310,44,4,13,p.dustyBlue],[315,47,3,10,p.amber],[319,43,5,14,p.moss],[326,48,4,9,p.creamShade],[339,68,4,13,p.cream],[344,66,5,15,p.dustyBlue],[350,70,3,11,p.amber]];
    for(const b of books) rect(...b);
    rect(310,93,16,9,p.walnutDark); rect(312,91,12,2,p.amber);
  }

  function drawActivityCorner(f,now,p){
    rect(292,180,80,30,p.shadow); rect(295,175,73,7,p.walnutLight); rect(302,182,5,25,p.walnutDark); rect(356,182,5,25,p.walnutDark); rect(293,179,77,4,p.walnut);
    const uses=historyValue(f,'activity_corner_uses',now);
    rect(320,169,23,10,p.walnut); rect(322,166,20,3,p.paper); rect(324,168,15,5,p.paper);
    for(let i=0;i<5;i++){ const s=emergence(uses,1+i*4.2,8); if(s<=0) continue; const x=302+i*12+(stableUnit('paper',i)>.5?2:0); const y=168-(i%2)*3; rect(x,y,11,5,p.paper); rect(x+2,y+2,6,1,p.walnutLight); }
    for(let i=0;i<7;i++){ const s=emergence(uses,2+i*3.2,7); if(s>.1) rect(305+i*8,171-(i%3),5,1,p.walnutDark); }
    // Pot + plant.
    rect(373,171,13,13,p.amber); rect(371,169,17,4,p.creamShade); rect(378,155,3,15,p.foliage);
    rect(371,158,8,5,p.foliage); rect(381,156,8,5,p.moss); rect(368,163,8,4,p.mossDark); rect(382,163,9,4,p.foliage);
    if(causalActivityState(f,now).activity_corner>0){ const hx=clamp(px(f.creature.x)-4,305,356); rect(hx-6,174,12,1,p.cream); }
  }

  function drawBowls(p){
    rect(257,213,20,3,p.shadow); rect(258,208,18,5,p.dustyBlue); rect(261,206,12,2,p.cream); rect(286,214,19,3,p.shadow); rect(287,209,17,5,p.amber); rect(290,207,11,2,p.creamShade);
  }

  function drawBackground(f,now){
    const p=visualLighting(f,now).palette;
    rect(0,0,ART_W,158,p.wall); rect(0,158,ART_W,82,p.floor);
    // Wall boards/panel rhythm; all clusters align to art pixels.
    for(let y=17;y<153;y+=27) rect(0,y,ART_W,1,p.wallShade);
    for(let x=12;x<395;x+=43){ rect(x,18+(x%4),2,6,p.wallLight); rect(x+5,20+(x%3),6,1,p.wallLight); }
    rect(0,153,ART_W,7,p.walnutDark); rect(0,153,ART_W,2,p.walnutLight);
    for(const y of [178,202,226]) rect(0,y,ART_W,1,p.floorShade);
    for(let x=16;x<390;x+=52){ rect(x,162+(x%5),15,1,p.floorLight); rect(x+7,186+(x%7),11,1,p.floorShade); }

    drawWindow(f,now,p);
    drawBed(f,now,p);
    drawRug(p);
    drawShelf(f,p);
    drawActivityCorner(f,now,p);
    drawBowls(p);
    drawPersistentHistory(f,p);

    // Lived-in small clusters: flowers, scuffs and stitching, kept sparse.
    rect(277,150,4,2,p.amber); rect(281,148,2,4,p.foliage); rect(274,149,2,2,p.cream);
    rect(17,218,7,1,p.floorShade); rect(33,229,5,1,p.floorLight); rect(244,222,9,1,p.floorShade);

    const phase=Math.floor(now/650);
    for(const m of motes){ if((phase+Math.floor(m.phase))%4!==0) continue; rect(m.x,m.y,1,1,p.cream); }
    return p;
  }

  function placedObjectRenderState(o, f, now) {
    const source=previous?.objects?.find(item=>item.id===o.id);
    if(!snapshotPath&&source?.state==='carried'&&o.state==='placed'){
      const raw=clamp01((now-fetchedAt)/MOTION.placement_ms),t=smoother01((raw-.34)/.58),facing=previous?.creature?.facing==='left'?-1:1;
      const originX=(transitionSource?.x??Number(previous.creature.x))+facing*22, originY=(transitionSource?.y??Number(previous.creature.y))-4;
      return {x:mix(originX,Number(o.x),t),y:mix(originY,Number(o.y),t),progress:t,phase:raw<.34?'prepare':t<1?'lower-contact':'settled',transitioning:t<1};
    }
    return {x:Number(o.x),y:Number(o.y),progress:1,phase:'settled',transitioning:false};
  }
  function activePlacementState(f,now){
    if(!previous||snapshotPath) return null;
    for(const o of f.objects||[]){ const source=previous.objects?.find(item=>item.id===o.id); if(source?.state==='carried'&&o.state==='placed'){ const rs=placedObjectRenderState(o,f,now); return {object_id:o.id,rendered_x:Number(rs.x.toFixed(6)),rendered_y:Number(rs.y.toFixed(6)),target_x:Number(o.x),target_y:Number(o.y),progress:Number(rs.progress.toFixed(6)),phase:rs.phase}; } }
    return null;
  }

  function drawObject(o,paletteOverride=null){
    if(o.state==='carried') return;
    const p=paletteOverride||PALETTES.day,x=px(o.x),y=px(o.y);
    rect(x-5,y+3,10,2,p.shadow);
    if(o.kind==='stone'){ rect(x-5,y-2,10,5,p.dustyBlue); rect(x-3,y-4,6,2,p.dustyBlue); rect(x-2,y-3,3,1,p.rain); rect(x+3,y,2,1,p.skyDark); }
    else if(o.kind==='leaf'){ rect(x-5,y-1,9,3,p.amber); rect(x-3,y-3,7,2,p.amber); rect(x-1,y+2,2,2,p.walnutDark); drawPixelLine(x-4,y+3,x+4,y-3,p.walnutDark,1); }
    else if(o.kind==='seed'){ rect(x-4,y-3,8,6,p.walnutLight); rect(x-3,y-4,6,2,p.walnut); rect(x-2,y-1,4,2,p.amber); }
    else if(o.kind==='shell'){ rect(x-4,y-3,8,6,p.cream); rect(x-5,y-1,10,3,p.cream); rect(x-2,y-2,4,1,p.creamShade); rect(x-1,y,3,1,p.walnutLight); }
    else if(o.kind==='thread'){ rect(x-5,y-2,8,2,'#a85c4d'); rect(x-3,y,7,2,'#a85c4d'); rect(x+2,y-1,3,1,p.creamShade); }
    else { rect(x-5,y-1,11,3,p.cream); rect(x-3,y-4,6,9,p.cream); rect(x-1,y-2,2,5,p.amber); }
  }
  function drawWorldObject(o,f,now,p){ if(o.state==='carried') return; const rs=placedObjectRenderState(o,f,now); drawObject({...o,x:rs.x,y:rs.y},p); }

  function actionTargetObject(f){
    const id=f.creature?.target_object_id||f.last_event?.object_id; if(!id) return null;
    const prior=previous?.objects?.find(o=>o.id===id); if(f.creature.activity==='carry'&&prior?.state==='placed') return prior;
    return f.objects?.find(o=>o.id===id)||prior||null;
  }
  function actionTargetPoint(f){
    const lx=Number(f.last_event?.target_x),ly=Number(f.last_event?.target_y);
    if(Number.isFinite(lx)&&Number.isFinite(ly)) return {x:lx,y:ly,id:f.last_event?.object_id||f.creature?.target_object_id};
    const obj=actionTargetObject(f); return obj?{x:Number(obj.x),y:Number(obj.y),id:obj.id}:null;
  }
  function phaseName(moving,raw,activityProgress){
    if(moving){ if(raw<.08)return'anticipation'; if(raw<.82)return'movement'; if(raw<.94)return'settle'; return'recovery'; }
    if(activityProgress<.18)return'anticipation'; if(activityProgress<.62)return'contact'; if(activityProgress<.88)return'settle'; return'hold';
  }

  function creatureRenderState(f, now) {
    const c=f.creature,old=previous?.creature||c,sourceX=Number(transitionSource?.x??old.x),sourceY=Number(transitionSource?.y??old.y);
    const semanticDistance=Math.hypot(Number(c.x)-sourceX,Number(c.y)-sourceY),duration=locomotionDuration(semanticDistance),raw=clamp01((now-fetchedAt)/duration);
    const travel=semanticDistance>2?stagedTravel(raw):1;
    const continuousX=mix(sourceX,Number(c.x),travel),continuousBaseY=mix(sourceY,Number(c.y),travel),moving=semanticDistance>2&&travel<1;
    const activityProgress=actionEnvelope(now,c.activity),target=actionTargetPoint(f);
    let renderedFacing=c.facing; if(!moving&&target&&['inspect','carry','place'].includes(c.activity)&&Math.abs(Number(target.x)-continuousX)>3) renderedFacing=Number(target.x)>=continuousX?'right':'left';
    const direction=renderedFacing==='left'?-1:1,strideCount=Math.max(2,Math.round(semanticDistance/58)),walkPhase=travel*Math.PI*2*strideCount;
    const walkBob=moving?(Math.floor(Math.abs(Math.sin(walkPhase))*2)):0;
    const breathStep=c.pose==='sleep'?((Math.floor(now/500)%2)?1:0):(!moving&&Math.floor(now/900)%2?1:0);
    const renderedX=snapDisplay(continuousX),renderedBaseY=snapDisplay(continuousBaseY),renderedY=renderedBaseY-(walkBob+breathStep)*SCALE;
    const pickupSource=c.carrying?previous?.objects?.find(o=>o.id===c.carrying&&o.state==='placed'):null;
    const attachmentProgress=pickupSource?smoother01((activityProgress-.24)/.46):(c.carrying?1:0),holdX=direction*22,holdY=-4,attached=Boolean(c.carrying)&&attachmentProgress>=.96;
    let carriedWorldX=null,carriedWorldY=null;
    if(c.carrying){ const tx=renderedX+holdX,ty=renderedBaseY+holdY; carriedWorldX=pickupSource?mix(Number(pickupSource.x),tx,attachmentProgress):tx; carriedWorldY=pickupSource?mix(Number(pickupSource.y),ty,attachmentProgress):ty; carriedWorldX=snapDisplay(carriedWorldX); carriedWorldY=snapDisplay(carriedWorldY); }
    const causal=causalActivityState(f,now);
    return {
      requested_timestamp_ms:now,source_tick:previous?.tick??f.tick,target_tick:f.tick,semantic_x:c.x,semantic_y:c.y,source_x:sourceX,source_y:sourceY,
      rendered_x:renderedX,rendered_y:renderedY,rendered_base_y:renderedBaseY,continuous_x:Number(continuousX.toFixed(6)),continuous_base_y:Number(continuousBaseY.toFixed(6)),
      interpolation_progress:Number(raw.toFixed(6)),interpolation_ease:Number(travel.toFixed(9)),motion_duration_ms:Number(duration.toFixed(3)),activity_progress:Number(activityProgress.toFixed(6)),motion_phase:phaseName(moving,raw,activityProgress),semantic_distance:Number(semanticDistance.toFixed(6)),moving,facing:renderedFacing,pose:c.pose,activity:c.activity,
      carrying:attached?c.carrying:null,carrying_semantic:c.carrying,attachment_progress:Number(attachmentProgress.toFixed(6)),carried_rendered_x:carriedWorldX,carried_rendered_y:carriedWorldY,carried_relative_x:attached?holdX:null,carried_relative_y:attached?holdY:null,walk_phase:Number(walkPhase.toFixed(6)),
      causal_activity:{sleep_nook:Number(causal.sleep_nook.toFixed(6)),window:Number(causal.window.toFixed(6)),activity_corner:Number(causal.activity_corner.toFixed(6))},
      interaction_target:target?{object_id:target.id||null,x:Number(target.x.toFixed(6)),y:Number(target.y.toFixed(6))}:null,object_placement:activePlacementState(f,now),
      ambient_classes:[f.weather==='rain'?'rain':f.weather==='mist'?'mist':null,'pixel-motes',c.pose==='sleep'?'breathing':moving?'walk-cycle':'quiet-breathing',causal.sleep_nook>0?'bedding-contact':null,causal.window>0?'window-contact':null,causal.activity_corner>0?'work-surface-contact':null].filter(Boolean),
      art_grid:{width:ART_W,height:ART_H,scale:SCALE,x:px(renderedX),y:px(renderedBaseY)},
    };
  }

  function drawMossSprite(f,now,rs,p){
    const c=f.creature,flip=rs.facing==='left'?-1:1,ap=rs.activity_progress,prior=previous?.creature?.activity;
    const x=px(rs.rendered_x),baseY=px(rs.rendered_base_y),bob=Math.round((rs.rendered_base_y-rs.rendered_y)/SCALE);
    let pose='idle';
    if(c.activity==='sleep'||c.pose==='sleep') pose='sleep';
    else if(c.activity==='wake') pose='wake';
    else if(rs.moving) pose='walk';
    else if(c.activity==='inspect') pose='inspect';
    else if(c.activity==='carry') pose='carry';
    else if(c.activity==='place') pose='place';
    else if(c.activity==='look_outside') pose='window';
    else if(c.activity==='rest') pose='rest';
    const phase=Math.floor(rs.walk_phase/Math.PI)%2;
    const target=actionTargetPoint(f),targetY=target?px(target.y):baseY;

    ctx.save(); ctx.translate(x,baseY-bob); ctx.scale(flip,1);
    if(pose==='sleep'){
      rect(-16,5,31,4,p.shadow); rect(-13,-3,25,9,p.dogDark); rect(-10,-7,22,12,p.dog); rect(2,-9,12,10,p.dogLight); rect(8,-7,7,6,p.dogCream);
      rect(-15,-6,7,7,p.dogDark); rect(-17,-2,5,5,p.dog); rect(6,-13,5,6,p.dogDark); rect(10,-12,5,7,p.dogDark);
      rect(11,-6,2,1,p.eye); rect(-4,1,9,2,p.dogLight); rect(-10,2,7,2,p.dogDark);
      ctx.restore(); return;
    }

    const crouch=pose==='rest'?2:pose==='carry'?1:0;
    const lean=(pose==='inspect'||pose==='place')?2:pose==='window'?1:0;
    // Shadow is sparse and fully hard-edged.
    rect(-13,10,26,3,p.shadow); rect(-9,13,18,1,p.shadow);
    // Tail silhouette.
    if(pose==='rest'){ rect(-18,1,6,3,p.dogDark); rect(-21,3,6,3,p.dog); }
    else { rect(-18,-3+crouch,7,3,p.dogDark); rect(-21,-6+crouch,5,3,p.dog); rect(-22,-9+crouch,3,3,p.dogLight); }
    // Compact body: 2-4 stepped shades.
    rect(-13,-5+crouch,23,12,p.dogDark); rect(-11,-8+crouch,21,13,p.dog); rect(-7,-5+crouch,16,7,p.dogLight); rect(-5,1+crouch,11,3,p.dogDark);
    // Planted short legs / walk keyframes.
    if(pose==='walk'){
      if(phase===0){ rect(-9,4+crouch,5,8,p.dogDark); rect(4,5+crouch,5,6,p.dogDark); rect(-11,11+crouch,7,2,p.dogDark); rect(4,10+crouch,7,2,p.dogDark); }
      else { rect(-8,5+crouch,5,6,p.dogDark); rect(3,4+crouch,5,8,p.dogDark); rect(-9,10+crouch,7,2,p.dogDark); rect(3,11+crouch,7,2,p.dogDark); }
    } else { rect(-9,5+crouch,5,7,p.dogDark); rect(4,5+crouch,5,7,p.dogDark); rect(-10,11+crouch,7,2,p.dogDark); rect(4,11+crouch,7,2,p.dogDark); }

    // Slightly oversized head, side/three-quarter by default.
    const hx=5+lean,hy=-14+crouch+(pose==='rest'?2:0)+(targetY>baseY&&pose==='inspect'?1:0);
    rect(hx-7,hy-5,14,12,p.dogDark); rect(hx-6,hy-7,13,12,p.dog); rect(hx-3,hy-5,10,7,p.dogLight);
    // Floppy ears, intentionally asymmetrical clusters.
    const earDrop=(c.expression==='curious'||pose==='window')?-1:1;
    rect(hx-8,hy-6+earDrop,5,9,p.dogDark); rect(hx-10,hy-2+earDrop,5,7,p.dogDark); rect(hx+5,hy-6+earDrop,4,8,p.dogDark); rect(hx+7,hy-2+earDrop,4,6,p.dogDark);
    // Muzzle / minimal face; no accessory required for the core hero set.
    rect(hx+2,hy,8,5,p.dogCream); rect(hx+7,hy+1,3,2,p.eye); rect(hx+1,hy-3,2,2,p.eye);
    if(c.expression==='sleepy'){ rect(hx,hy-2,3,1,p.eye); }
    else if(pose==='inspect'||pose==='window'){ rect(hx+1,hy-4,2,2,p.eye); }
    rect(hx+5,hy+4,3,1,p.dogDark);
    // Single highlight clusters keep the sprite lively without glossy rendering.
    rect(hx-1,hy-5,3,1,p.dogCream); rect(-3,-6+crouch,5,1,p.dogLight);

    // Interaction forepaw key poses. Contact remains target-owned.
    if(['inspect','carry','place'].includes(pose)){
      const reach=pose==='inspect'?smooth01((ap-.12)/.42):pose==='carry'?smooth01((ap-.12)/.54):smooth01((ap-.16)/.46)*(1-smooth01((ap-.9)/.1));
      if(reach>.05){ const endX=target?clamp((px(target.x)-x)*flip,9,18):14; const endY=target?clamp(px(target.y)-baseY,-8,11):4; const ex=Math.round(mix(8,endX,reach)),ey=Math.round(mix(2,endY,reach)); drawPixelLine(7,0+crouch,ex,ey,p.dogDark,3); rect(ex-1,ey,4,2,p.dogLight); }
    }
    ctx.restore();
  }

  function drawCreature(f,now,p){
    const rs=creatureRenderState(f,now); drawMossSprite(f,now,rs,p);
    if(f.creature.carrying){ const obj=f.objects.find(o=>o.id===f.creature.carrying)||previous?.objects?.find(o=>o.id===f.creature.carrying); if(obj&&rs.carried_rendered_x!==null) drawObject({...obj,state:'placed',x:rs.carried_rendered_x,y:rs.carried_rendered_y},p); }
    return rs;
  }

  function drawForegroundFurniture(f,now,p){
    for(const y of [62,87,112]) rect(303,y,70,2,p.walnutDark);
    rect(294,179,77,3,p.walnutDark); rect(296,179,73,1,p.walnutLight);
  }
  function drawForegroundCausality(f, now, rs, p) {
    const causal=causalActivityState(f,now);
    if(causal.sleep_nook>0){ const x=px(rs.rendered_x),y=px(rs.rendered_base_y); rect(x-15,y+4,31,8,p.dustyBlue); rect(x-11,y+3,23,3,p.dustyBlue); rect(x-8,y+6,17,1,p.skyDark); }
  }

  function presentArtSurface(){
    displayCtx.imageSmoothingEnabled=false;
    displayCtx.clearRect(0,0,DISPLAY_W,DISPLAY_H);
    displayCtx.drawImage(artCanvas,0,0,ART_W,ART_H,0,0,DISPLAY_W,DISPLAY_H);
  }

  function render(now, scheduleNext = true) {
    if(!frame){ rect(0,0,ART_W,ART_H,'#25242b'); presentArtSurface(); if(scheduleNext)requestAnimationFrame(render); return null; }
    const p=drawBackground(frame,now);
    for(const o of frame.objects) drawWorldObject(o,frame,now,p);
    const renderState=drawCreature(frame,now,p);
    drawForegroundFurniture(frame,now,p);
    drawForegroundCausality(frame, now, renderState, p);
    presentArtSurface();
    if(debugVisible){ debug.hidden=false; debug.textContent=JSON.stringify({mode:snapshotPath?'snapshot':'live',connected,tick:frame.tick,lighting:frame.lighting,weather:frame.weather,art_surface:[ART_W,ART_H],display:[DISPLAY_W,DISPLAY_H],scale:SCALE,creature:frame.creature,last_event:frame.last_event,poll_error:lastPollError},null,2); } else debug.hidden=true;
    if(scheduleNext) requestAnimationFrame(render);
    return renderState;
  }

  async function rasterTelemetry(){
    const image=displayCtx.getImageData(0,0,DISPLAY_W,DISPLAY_H); let h=2166136261;
    for(let i=0;i<image.data.length;i+=4){ h^=image.data[i];h=Math.imul(h,16777619);h^=image.data[i+1];h=Math.imul(h,16777619);h^=image.data[i+2];h=Math.imul(h,16777619);h^=image.data[i+3];h=Math.imul(h,16777619); }
    let scaleErrors=0;
    for(let y=0;y<DISPLAY_H;y+=2){ for(let x=0;x<DISPLAY_W;x+=2){ const i=(y*DISPLAY_W+x)*4; for(const [dx,dy] of [[1,0],[0,1],[1,1]]){ const j=((y+dy)*DISPLAY_W+(x+dx))*4; for(let c=0;c<4;c++) if(image.data[i+c]!==image.data[j+c]){scaleErrors++;break;} } } }
    const pixelHash=`fnv1a32:${(h>>>0).toString(16).padStart(8,'0')}`,gridW=20,gridH=12,cellW=40,cellH=40,grid=[];
    for(let gy=0;gy<gridH;gy++) for(let gx=0;gx<gridW;gx++){ let total=0,count=0; for(let y=gy*cellH;y<(gy+1)*cellH;y+=4) for(let x=gx*cellW;x<(gx+1)*cellW;x+=4){ const i=(y*DISPLAY_W+x)*4; total+=image.data[i]*.2126+image.data[i+1]*.7152+image.data[i+2]*.0722;count++; } grid.push(Number((total/count).toFixed(3))); }
    return {width:DISPLAY_W,height:DISPLAY_H,art_width:ART_W,art_height:ART_H,integer_scale:SCALE,image_smoothing:false,scale2x_exact:scaleErrors===0,scale2x_error_blocks:scaleErrors,pixel_hash:pixelHash,luma_grid_width:gridW,luma_grid_height:gridH,luma_grid:grid};
  }

  function publishTemporal(payload){ window.__terrariumTemporalResult=payload; telemetryNode.textContent=JSON.stringify(payload); document.title=`Terrarium Temporal ${payload.status||'ready'}`; fetch('/api/dev/temporal-evidence',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).catch(()=>{}); }
  async function captureTemporalSample(timestamp) { const state=render(timestamp,false); const raster=await rasterTelemetry(); return {...state,raster}; }

  function acceptFrame(next, now) {
    if(!frame){frame=next;previous=null;transitionSource=null;fetchedAt=now;activityStartedAt=now;return;}
    if(next.tick===frame.tick)return;
    const current=creatureRenderState(frame,now),source=temporalContinuity==='legacy'?null:{x:current.continuous_x,y:current.continuous_base_y};
    const continuesIntent=next.last_event?.decision===false&&next.creature?.intent_action&&next.creature.intent_action===frame.creature?.intent_action;
    previous=frame;frame=next;transitionSource=source;fetchedAt=now;if(!continuesIntent)activityStartedAt=now;
  }
  async function poll(){
    try{ const response=await fetch('/api/frame',{cache:'no-store'});if(!response.ok)throw new Error(`HTTP ${response.status}`);const next=await response.json();if(next.logical_width!==DISPLAY_W||next.logical_height!==DISPLAY_H)throw new Error('authoritative frame contract mismatch');acceptFrame(next,performance.now());connected=true;lastPollError=null; }
    catch(err){connected=false;lastPollError=String(err);}
  }
  async function loadSnapshot(){
    try{ if(!snapshotPath||!snapshotPath.startsWith('/snapshots/dev/')||!snapshotPath.endsWith('/frame.json'))throw new Error('invalid snapshot path');const response=await fetch(snapshotPath,{cache:'no-store'});if(!response.ok)throw new Error(`HTTP ${response.status}`);const next=await response.json();if(next.logical_width!==DISPLAY_W||next.logical_height!==DISPLAY_H)throw new Error('snapshot frame contract mismatch');frame=next;previous=null;transitionSource=null;fetchedAt=performance.now();activityStartedAt=fetchedAt;connected=true;lastPollError=null; }
    catch(err){connected=false;lastPollError=String(err);}
  }
  async function loadTemporalScenario(){
    try{
      const response=await fetch('/api/dev/temporal-fixtures',{cache:'no-store'});if(!response.ok)throw new Error(`HTTP ${response.status}`);const pack=await response.json();
      if(temporalContinuityProbe){
        const probe=pack.continuity_probe;if(!probe)throw new Error('continuity probe fixture is missing');previous=probe.source;frame=probe.middle;transitionSource=null;fetchedAt=0;activityStartedAt=0;connected=true;lastPollError=null;
        const interrupt=Number(probe.interrupt_ms||1000),before=await captureTemporalSample(interrupt);acceptFrame(probe.followup,interrupt);const after=await captureTemporalSample(interrupt),jump=Math.hypot(after.continuous_x-before.continuous_x,after.continuous_base_y-before.continuous_base_y);
        publishTemporal({schema:'terrarium.continuity-probe.v1',status:'ready',scenario:'continuity_probe',easing:temporalContinuity,continuity:temporalContinuity,interrupt_ms:interrupt,source_tick:probe.source.tick,middle_tick:probe.middle.tick,followup_tick:probe.followup.tick,first_event:probe.first_event,second_event:probe.second_event,jump_px:Number(jump.toFixed(6)),before,after});return;
      }
      const scenario=pack.scenarios?.[temporalScenario];if(!scenario)throw new Error(`unknown temporal scenario: ${temporalScenario}`);previous=scenario.source;frame=scenario.target;transitionSource=null;fetchedAt=0;activityStartedAt=0;connected=true;lastPollError=null;
      if(frame.logical_width!==DISPLAY_W||frame.logical_height!==DISPLAY_H||previous.logical_width!==DISPLAY_W||previous.logical_height!==DISPLAY_H)throw new Error('temporal fixture frame contract mismatch');
      if(temporalRafProbe){
        const intervals=[];let last=null,start=null,frames=0;await new Promise(resolve=>{function probe(ts){if(start===null)start=ts;if(last!==null)intervals.push(ts-last);last=ts;frames++;render(ts-start,false);if(ts-start>=temporalDuration)resolve();else requestAnimationFrame(probe);}requestAnimationFrame(probe);});
        const sorted=[...intervals].sort((a,b)=>a-b),pct=p=>sorted.length?sorted[Math.min(sorted.length-1,Math.floor((sorted.length-1)*p))]:0;publishTemporal({schema:'terrarium.raf-probe.v1',status:'ready',scenario:temporalScenario,frames,duration_ms:Number((last-start).toFixed(3)),interval_count:intervals.length,interval_ms:{min:Number((sorted[0]||0).toFixed(3)),p50:Number(pct(.5).toFixed(3)),p95:Number(pct(.95).toFixed(3)),max:Number((sorted.at(-1)||0).toFixed(3)),over_34ms:intervals.filter(v=>v>34).length,over_50ms:intervals.filter(v=>v>50).length},intervals_ms:intervals.map(v=>Number(v.toFixed(3)))});return;
      }
      if(temporalSequence){ const timestamps=pack.recommended_timestamps_ms||[0,250,500,750,1000,1250,1500],samples=[];for(const t of timestamps)samples.push(await captureTemporalSample(Number(t)));publishTemporal({schema:'terrarium.temporal-capture.v1',status:'ready',scenario:temporalScenario,easing:temporalEasing,source_tick:scenario.source_tick,target_tick:scenario.target_tick,semantic_event:scenario.semantic_event,samples});return; }
      const sample=await captureTemporalSample(temporalTimestamp);publishTemporal({schema:'terrarium.temporal-keyframe.v1',status:'ready',scenario:temporalScenario,easing:temporalEasing,source_tick:scenario.source_tick,target_tick:scenario.target_tick,semantic_event:scenario.semantic_event,sample});
    }catch(err){connected=false;lastPollError=String(err);publishTemporal({schema:'terrarium.temporal-error.v1',status:'error',error:String(err)});}
  }

  window.__terrariumPixelRenderer = Object.freeze({art_width:ART_W,art_height:ART_H,display_width:DISPLAY_W,display_height:DISPLAY_H,integer_scale:SCALE,smoothing:false});
  document.addEventListener('keydown',ev=>{if(ev.key.toLowerCase()==='d')debugVisible=!debugVisible;});
  if(temporalScenario)loadTemporalScenario();else if(snapshotPath){loadSnapshot();requestAnimationFrame(render);}else{poll();setInterval(poll,700);requestAnimationFrame(render);}
})();
