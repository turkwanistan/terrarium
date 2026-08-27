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
    const routes={sleeping_nook:[[202,189],[174,191],[148,196]],window:[[202,189],[150,162],[84,158]],collection_shelf:[[202,189],[244,166],[277,156]],activity_corner:[[202,189],[245,185],[277,186]]};
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
    // Deep inset casing: top/side planes make the window feel built into the wall.
    rect(20,21,125,94,p.shadow); rect(22,22,121,91,p.walnutDark); rect(25,25,115,86,p.walnut);
    rect(29,28,107,79,p.walnutLight); rect(32,30,101,75,p.sky);
    rect(80,30,5,75,p.skyDark); rect(31,64,103,5,p.skyDark);
    rect(83,31,1,72,p.creamShade); rect(32,67,100,1,p.creamShade);
    // Exterior focal cluster.
    if(f.lighting==='night'){
      rect(108,41,10,8,p.cream); rect(105,44,13,5,p.cream); rect(111,39,4,2,p.cream);
      rect(48,42,2,2,p.creamShade); rect(64,52,1,1,p.cream); rect(121,57,2,1,p.creamShade);
    } else {
      rect(105,39,14,10,p.amber); rect(102,42,20,5,p.amber); rect(109,36,6,3,p.cream);
    }
    // Curtains use broad stepped cloth masses plus a few fold/shadow clusters.
    rect(21,27,10,78,p.creamShade); rect(18,31,9,67,p.cream); rect(15,39,7,47,p.creamShade);
    rect(132,27,10,78,p.creamShade); rect(139,32,9,65,p.cream); rect(146,40,6,46,p.creamShade);
    for(const [x,y,w] of [[19,35,8],[18,50,7],[17,68,6],[22,89,7],[137,38,8],[141,54,7],[143,72,6],[137,91,8]]) rect(x,y,w,2,p.wallShade);
    rect(17,28,14,4,p.walnut); rect(132,28,17,4,p.walnut); rect(18,27,12,2,p.walnutLight); rect(134,27,13,2,p.walnutLight);
    // Sill: bright top lip, darker front face and support brackets.
    rect(26,104,113,3,p.creamShade); rect(23,107,120,6,p.walnutLight); rect(26,113,114,4,p.walnutDark);
    rect(35,116,7,6,p.walnutDark); rect(122,116,7,6,p.walnutDark); rect(37,116,3,3,p.walnutLight); rect(124,116,3,3,p.walnutLight);
    // Low floor-side perch visually connects Moss's valid viewing stance to the sill.
    rect(45,146,80,3,p.walnutLight); rect(42,149,86,6,p.walnut); rect(45,155,80,3,p.walnutDark);
    rect(50,158,6,7,p.walnutDark); rect(116,158,6,7,p.walnutDark);

    if(f.weather==='rain'){
      const phase=Math.floor(now/150)%19;
      for(const d of rain){
        const x=34+d.x%96,y=31+((d.y+phase+d.phase)%67);
        rect(x,y,1,3,p.rain); if((d.phase&1)===0) rect(x-1,y+3,1,2,p.rain);
      }
      // Water gathering on the lower panes, kept sparse and clustered.
      for(const [x,y,w] of [[38,92,9],[58,88,5],[91,94,11],[115,90,7]]){ rect(x,y,w,1,p.rain); rect(x+2,y+1,Math.max(2,w-4),1,p.skyDark); }
    } else if(f.weather==='mist'){
      for(let y=45;y<91;y+=12) for(let x=35+(y%3);x<129;x+=19) rect(x,y,9,2,p.rain);
    }

    const watches=historyValue(f,'window_watches',now),wet=historyValue(f,'wet_window_watches',now);
    for(let i=0;i<6;i++){
      const strength=emergence(watches,1+i*2.5,6); if(strength<=0) continue;
      const x=47+i*13+(stableUnit('smudge',i)>.5?1:0),y=91-(i%2)*3;
      rect(x,y,5,1,p.creamShade); if(strength>.55) rect(x+1,y+1,4,1,p.skyDark);
    }
    for(let i=0;i<5;i++){
      const strength=emergence(wet,.4+i*1.3,4.5); if(strength<=0) continue;
      const x=45+i*16; rect(x,75,1,7,p.rain); rect(x+1,82,1,4,p.rain);
    }
    if(causalActivityState(f,now).window>0){ const cx=clamp(px(f.creature.x),44,121); rect(cx-8,103,16,2,p.creamShade); rect(cx-4,105,8,1,p.walnutLight); }
  }
  function drawBed(f,now,p){
    // Headboard and frame with exposed posts and a recessed mattress.
    rect(21,175,114,44,p.shadow); rect(22,172,9,44,p.walnutDark); rect(126,173,9,44,p.walnutDark);
    rect(24,170,5,5,p.walnutLight); rect(128,171,5,5,p.walnutLight);
    rect(29,177,99,35,p.walnut); rect(32,180,93,29,p.creamShade);
    rect(33,182,42,14,p.cream); rect(36,184,36,10,p.creamShade); rect(38,184,28,2,p.cream);
    // Blanket is an authored stepped mass, not one rectangle.
    rect(77,181,45,4,p.dustyBlue); rect(73,185,51,6,p.dustyBlue); rect(70,191,55,8,p.dustyBlue); rect(73,199,51,7,p.dustyBlue);
    rect(80,183,18,2,p.creamShade); rect(75,189,24,2,p.skyDark); rect(103,194,18,2,p.skyDark); rect(79,201,30,2,p.skyDark);
    rect(91,186,2,8,p.creamShade); rect(112,198,8,1,p.creamShade);
    const sleepTicks=historyValue(f,'sleep_nook_ticks',now),sleepBouts=historyValue(f,'sleep_nook_bouts',now);
    const nest=emergence(sleepTicks,0,18);
    if(nest>0){
      rect(77,196,43+Math.floor(8*emergence(sleepBouts,0,5)),5,p.walnutDark); rect(84,194,24,2,p.floorShade);
      if(nest>.45){ rect(88,192,13,1,p.creamShade); rect(105,198,10,1,p.skyDark); }
    }
    for(let i=0;i<4;i++){
      const s=emergence(sleepTicks,1+i*3.5,8); if(s>.2){ rect(65+i*12,187+i*2,8,1,p.walnutLight); rect(70+i*10,193+i,6,1,p.skyDark); }
    }
    // Footboard front plane and feet.
    rect(22,210,113,5,p.walnutLight); rect(22,215,113,4,p.walnutDark); rect(27,219,8,5,p.walnutDark); rect(122,219,8,5,p.walnutDark);
    rect(29,219,4,3,p.walnutLight); rect(124,219,4,3,p.walnutLight);
  }
  function drawRug(p){
    const rows=[[154,172,92],[149,176,102],[146,180,108],[144,184,112],[144,188,112],[146,192,108],[150,196,100],[156,200,88],[164,204,72]];
    for(const [x,y,w] of rows) rect(x,y,w,4,p.rug);
    // A deliberate woven border and a few broad fibers.
    rect(158,174,84,2,p.rugLight); rect(151,178,98,1,p.mossDark); rect(149,198,98,2,p.mossDark); rect(160,203,80,1,p.rugLight);
    for(const [x,y,w] of [[165,181,11],[188,184,9],[214,179,12],[173,193,13],[204,196,10],[228,190,8]]) rect(x,y,w,1,p.rugLight);
    for(const [x,y,w] of [[177,187,8],[198,191,12],[221,184,7],[187,200,9]]) rect(x,y,w,1,p.mossDark);
    for(const x of [156,171,187,205,222,238]) rect(x,201+(x%2),1,4,p.rugLight);
  }
  function drawShelf(f,p){
    // Cabinet silhouette with top cap, recessed back and shelf lips.
    rect(293,29,88,94,p.shadow); rect(296,27,83,11,p.walnutDark); rect(299,28,77,7,p.walnutLight);
    rect(299,38,7,81,p.walnutDark); rect(369,38,7,81,p.walnutDark); rect(306,39,63,78,p.walnut);
    rect(309,41,57,16,p.walnutDark); rect(309,66,57,16,p.walnutDark); rect(309,91,57,16,p.walnutDark);
    for(const y of [58,83,108]){ rect(304,y,68,6,p.walnutLight); rect(306,y+6,65,3,p.walnutDark); rect(311,y,54,1,p.creamShade); }
    const books=[[310,44,4,13,p.dustyBlue],[315,47,3,10,p.amber],[319,43,5,14,p.moss],[325,48,4,9,p.creamShade],[338,69,4,12,p.cream],[343,66,5,15,p.dustyBlue],[349,70,3,11,p.amber]];
    for(const b of books){ rect(...b); rect(b[0],b[1],1,b[3],p.shadow); }
    // Small fixed trinkets make shelf bays recognizable without competing with movable props.
    rect(337,48,12,7,p.walnutLight); rect(339,46,8,2,p.creamShade); rect(342,44,3,2,p.amber);
    rect(312,94,15,9,p.walnutDark); rect(314,92,11,2,p.amber); rect(318,90,3,2,p.cream);
    rect(347,96,8,6,p.creamShade); rect(349,94,4,2,p.dustyBlue);
    rect(301,119,74,5,p.walnutDark); rect(306,119,8,6,p.walnutLight); rect(361,119,8,6,p.walnutLight);
    // Accessible low collection tray: canonical shelf objects now stage here instead of inside wall bays.
    rect(304,143,65,3,p.walnutLight); rect(302,146,69,8,p.walnut); rect(305,146,63,3,p.walnutDark);
    rect(306,154,6,5,p.walnutDark); rect(361,154,6,5,p.walnutDark);
  }
  function drawActivityCorner(f,now,p){
    // Desk top: narrow light top plane over a darker apron and planted legs.
    rect(291,178,81,33,p.shadow); rect(294,173,76,4,p.walnutLight); rect(291,177,82,6,p.walnut); rect(296,183,72,5,p.walnutDark);
    rect(300,188,7,23,p.walnutDark); rect(356,188,7,23,p.walnutDark); rect(302,188,3,18,p.walnutLight); rect(358,188,3,18,p.walnutLight);
    rect(311,188,35,10,p.walnut); rect(314,190,29,6,p.walnutDark); rect(339,192,3,2,p.amber);
    const uses=historyValue(f,'activity_corner_uses',now);
    // Notebook and increasingly lived-in canonical activity aftermath.
    rect(319,167,24,10,p.walnutDark); rect(321,165,21,3,p.paper); rect(323,168,16,6,p.paper); rect(325,169,11,1,p.walnutLight);
    for(let i=0;i<5;i++){
      const s=emergence(uses,1+i*4.2,8); if(s<=0) continue;
      const x=300+i*12+(stableUnit('paper',i)>.5?2:0),y=168-(i%2)*3;
      rect(x,y,11,5,p.paper); rect(x+2,y+2,6,1,p.walnutLight); if(s>.6) rect(x+8,y+1,2,1,p.amber);
    }
    for(let i=0;i<7;i++){ const s=emergence(uses,2+i*3.2,7); if(s>.1) rect(304+i*8,172-(i%3),5,1,p.walnutDark); }
    // Pot + layered leaf clumps.
    rect(373,171,13,13,p.amber); rect(371,168,17,4,p.creamShade); rect(375,181,9,3,p.walnutDark);
    rect(378,154,3,15,p.foliage); rect(371,157,8,5,p.foliage); rect(381,155,8,5,p.moss); rect(368,162,8,4,p.mossDark); rect(382,162,9,4,p.foliage); rect(375,151,7,5,p.moss);
    if(causalActivityState(f,now).activity_corner>0){ const hx=clamp(px(f.creature.x)-4,305,356); rect(hx-6,174,12,1,p.cream); }
  }
  function drawBowls(p){
    // Two squat stepped bowls with rims/interiors and their own contact shadows.
    rect(256,214,22,3,p.shadow); rect(258,208,18,6,p.dustyBlue); rect(260,206,14,3,p.cream); rect(262,207,10,2,p.skyDark); rect(260,213,14,2,p.skyDark);
    rect(285,215,21,3,p.shadow); rect(287,209,17,6,p.amber); rect(289,207,13,3,p.creamShade); rect(291,208,9,2,p.walnutDark); rect(289,214,13,2,p.walnutDark);
  }
  function drawBackground(f,now){
    const p=visualLighting(f,now).palette;
    rect(0,0,ART_W,158,p.wall); rect(0,158,ART_W,82,p.floor);
    // Plaster/board irregularity: broad authored runs, not confetti texture.
    for(let y=17;y<153;y+=27) rect(0,y,ART_W,1,p.wallShade);
    for(const [x,y,w] of [[12,20,18],[61,45,13],[104,74,21],[164,32,15],[214,93,24],[268,55,18],[331,132,22],[362,18,14]]){
      rect(x,y,w,1,p.wallLight); rect(x+3,y+2,Math.max(4,w-8),1,p.wallShade);
    }
    rect(0,152,ART_W,8,p.walnutDark); rect(0,152,ART_W,2,p.walnutLight); rect(0,159,ART_W,2,p.floorShade);
    // Floor boards receive seams, knots and short grain clusters with open breathing room.
    for(const y of [178,202,226]) rect(0,y,ART_W,1,p.floorShade);
    for(const x of [48,99,154,207,262,317,369]){ const y=160+((x/3)%24); rect(x,y,1,17,p.floorShade); }
    for(const [x,y,w] of [[16,164,15],[73,186,12],[125,215,17],[184,166,13],[239,221,18],[300,191,15],[348,229,19]]){
      rect(x,y,w,1,p.floorLight); rect(x+4,y+2,Math.max(3,w-8),1,p.floorShade);
    }

    drawWindow(f,now,p);
    drawBed(f,now,p);
    drawRug(p);
    drawShelf(f,p);
    drawActivityCorner(f,now,p);
    drawBowls(p);
    drawPersistentHistory(f,p);

    // A few composition-balancing accents near otherwise empty edges.
    rect(276,149,4,2,p.amber); rect(280,147,2,4,p.foliage); rect(273,148,2,2,p.cream);
    rect(17,218,7,1,p.floorShade); rect(33,229,5,1,p.floorLight); rect(244,222,9,1,p.floorShade);
    rect(268,151,14,2,p.walnutDark); rect(271,147,8,4,p.walnut); rect(274,144,3,3,p.foliage);

    const phase=Math.floor(now/850);
    for(const m of motes){ if((phase+Math.floor(m.phase))%5!==0) continue; rect(m.x,m.y,1,1,p.cream); }
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
    const cx=Number(f.last_event?.contact_x),cy=Number(f.last_event?.contact_y);
    if(Number.isFinite(cx)&&Number.isFinite(cy)) return {x:cx,y:cy,id:f.last_event?.object_id||f.creature?.target_object_id,contact:true};
    const lx=Number(f.last_event?.target_x),ly=Number(f.last_event?.target_y);
    if(Number.isFinite(lx)&&Number.isFinite(ly)) return {x:lx,y:ly,id:f.last_event?.object_id||f.creature?.target_object_id,contact:false};
    const obj=actionTargetObject(f); return obj?{x:Number(obj.x),y:Number(obj.y),id:obj.id,contact:false}:null;
  }
  function authoredRoute(f,sourceX,sourceY){
    const points=[{x:Number(sourceX),y:Number(sourceY)}], authored=Array.isArray(f.last_event?.route)?f.last_event.route:[];
    for(const item of authored){
      const x=Number(item?.x),y=Number(item?.y); if(!Number.isFinite(x)||!Number.isFinite(y)) continue;
      const prior=points[points.length-1]; if(Math.abs(prior.x-x)>1e-9||Math.abs(prior.y-y)>1e-9) points.push({x,y});
    }
    const end={x:Number(f.creature.x),y:Number(f.creature.y)},last=points[points.length-1];
    if(Math.abs(last.x-end.x)>1e-9||Math.abs(last.y-end.y)>1e-9) points.push(end);
    return points;
  }
  function routeSample(points,progress){
    if(points.length<2) return {x:points[0].x,y:points[0].y,total:0,segment_index:0,segment_progress:1,segment_dx:0,segment_dy:0};
    const lengths=[];let total=0;for(let i=1;i<points.length;i++){const len=Math.hypot(points[i].x-points[i-1].x,points[i].y-points[i-1].y);lengths.push(len);total+=len;}
    if(total<=1e-9) return {x:points.at(-1).x,y:points.at(-1).y,total:0,segment_index:0,segment_progress:1,segment_dx:0,segment_dy:0};
    let remaining=clamp01(progress)*total;
    for(let i=0;i<lengths.length;i++){const len=lengths[i];if(remaining<=len||i===lengths.length-1){const t=len<=1e-9?1:clamp01(remaining/len),a=points[i],b=points[i+1];return{x:mix(a.x,b.x,t),y:mix(a.y,b.y,t),total,segment_index:i,segment_progress:t,segment_dx:b.x-a.x,segment_dy:b.y-a.y};}remaining-=len;}
    const last=points.at(-1);return{x:last.x,y:last.y,total,segment_index:lengths.length-1,segment_progress:1,segment_dx:0,segment_dy:0};
  }

  function phaseName(moving,raw,activityProgress){
    if(moving){ if(raw<.08)return'anticipation'; if(raw<.82)return'movement'; if(raw<.94)return'settle'; return'recovery'; }
    if(activityProgress<.18)return'anticipation'; if(activityProgress<.62)return'contact'; if(activityProgress<.88)return'settle'; return'hold';
  }
  function authoredStage(progress,cuts){
    for(let i=0;i<cuts.length;i++) if(progress<cuts[i]) return i;
    return cuts.length;
  }

  function creatureRenderState(f, now) {
    const c=f.creature,old=previous?.creature||c,sourceX=Number(transitionSource?.x??old.x),sourceY=Number(transitionSource?.y??old.y);
    const semanticDistance=Math.hypot(Number(c.x)-sourceX,Number(c.y)-sourceY),route=authoredRoute(f,sourceX,sourceY),routeTotal=routeSample(route,1).total,duration=locomotionDuration(routeTotal),raw=clamp01((now-fetchedAt)/duration);
    const travel=routeTotal>2?stagedTravel(raw):1,routeState=routeSample(route,travel),continuousX=routeState.x,continuousBaseY=routeState.y,moving=routeTotal>2&&travel<1;
    const activityProgress=actionEnvelope(now,c.activity),target=actionTargetPoint(f);
    let renderedFacing=c.facing;
    if(moving&&Math.abs(routeState.segment_dx)>3) renderedFacing=routeState.segment_dx>0?'right':'left';
    else if(!moving&&target&&['inspect','carry','place'].includes(c.activity)&&Math.abs(Number(target.x)-continuousX)>3) renderedFacing=Number(target.x)>=continuousX?'right':'left';
    const direction=renderedFacing==='left'?-1:1,strideCount=Math.max(2,Math.round(routeTotal/58)),walkPhase=travel*Math.PI*2*strideCount;
    let carryDirection=direction,turningCarry=false;
    if(moving&&c.carrying&&routeState.segment_index>0){
      const priorA=route[routeState.segment_index-1],priorB=route[routeState.segment_index],priorDx=priorB.x-priorA.x;
      const priorDirection=Math.abs(priorDx)>3?(priorDx>0?1:-1):direction;
      if(priorDirection!==direction&&routeState.segment_progress<.20){ const blend=smoother01(routeState.segment_progress/.20);carryDirection=mix(priorDirection,direction,blend);turningCarry=true; }
    }
    const walkFrame=moving?(Math.floor(walkPhase/(Math.PI/2))&3):0;
    const walkBob=moving?([0,1,0,1][walkFrame]):0;
    const breathStep=c.pose==='sleep'?((Math.floor(now/500)%2)?1:0):(!moving&&Math.floor(now/900)%2?1:0);
    const renderedX=snapDisplay(continuousX),renderedBaseY=snapDisplay(continuousBaseY),renderedY=renderedBaseY-(walkBob+breathStep)*SCALE;
    const pickupSource=c.carrying?previous?.objects?.find(o=>o.id===c.carrying&&o.state==='placed'):null;
    const attachmentProgress=pickupSource?smoother01((activityProgress-.24)/.46):(c.carrying?1:0),holdX=carryDirection*22,holdY=-4,attached=Boolean(c.carrying)&&attachmentProgress>=.96;
    let carriedWorldX=null,carriedWorldY=null;
    if(c.carrying){ const tx=renderedX+holdX,ty=renderedBaseY+holdY; carriedWorldX=pickupSource?mix(Number(pickupSource.x),tx,attachmentProgress):tx; carriedWorldY=pickupSource?mix(Number(pickupSource.y),ty,attachmentProgress):ty; carriedWorldX=snapDisplay(carriedWorldX); carriedWorldY=snapDisplay(carriedWorldY); }
    const causal=causalActivityState(f,now);
    return {
      requested_timestamp_ms:now,source_tick:previous?.tick??f.tick,target_tick:f.tick,semantic_x:c.x,semantic_y:c.y,source_x:sourceX,source_y:sourceY,
      rendered_x:renderedX,rendered_y:renderedY,rendered_base_y:renderedBaseY,continuous_x:Number(continuousX.toFixed(6)),continuous_base_y:Number(continuousBaseY.toFixed(6)),
      interpolation_progress:Number(raw.toFixed(6)),interpolation_ease:Number(travel.toFixed(9)),motion_duration_ms:Number(duration.toFixed(3)),activity_progress:Number(activityProgress.toFixed(6)),motion_phase:phaseName(moving,raw,activityProgress),semantic_distance:Number(semanticDistance.toFixed(6)),route_distance:Number(routeTotal.toFixed(6)),route_segment_index:routeState.segment_index,route_segment_progress:Number(routeState.segment_progress.toFixed(6)),route_points:route.map(point=>({x:Number(point.x.toFixed(6)),y:Number(point.y.toFixed(6))})),moving,facing:renderedFacing,pose:c.pose,activity:c.activity,
      carrying:attached?c.carrying:null,carrying_semantic:c.carrying,attachment_progress:Number(attachmentProgress.toFixed(6)),carried_rendered_x:carriedWorldX,carried_rendered_y:carriedWorldY,carried_relative_x:attached?Number(holdX.toFixed(6)):null,carried_relative_y:attached?holdY:null,carry_turning:turningCarry,walk_phase:Number(walkPhase.toFixed(6)),walk_keyframe:walkFrame,
      causal_activity:{sleep_nook:Number(causal.sleep_nook.toFixed(6)),window:Number(causal.window.toFixed(6)),activity_corner:Number(causal.activity_corner.toFixed(6))},
      interaction_target:target?{object_id:target.id||null,x:Number(target.x.toFixed(6)),y:Number(target.y.toFixed(6)),contact:Boolean(target.contact)}:null,semantic_target:(Number.isFinite(Number(f.last_event?.target_x))&&Number.isFinite(Number(f.last_event?.target_y)))?{x:Number(f.last_event.target_x),y:Number(f.last_event.target_y),object_id:f.last_event?.object_id||null}:null,object_placement:activePlacementState(f,now),
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

    const walkFrame=rs.walk_keyframe||0;
    const target=actionTargetPoint(f);
    const localTargetX=target?clamp((px(target.x)-x)*flip,10,19):16;
    const localTargetY=target?clamp(px(target.y)-baseY,-14,10):4;
    const idleFrame=Math.floor(now/900)&1;
    const inspectStage=authoredStage(ap,[.20,.46,.76]);
    const pickupStage=authoredStage(ap,[.16,.34,.58,.80]);
    const placeStage=authoredStage(ap,[.16,.34,.58,.78,.92]);
    const windowStage=authoredStage(ap,[.18,.46,.78]);
    const restStage=authoredStage(ap,[.22,.58,.84]);
    const sleepStage=prior==='sleep'?4:authoredStage(ap,[.14,.34,.58,.82]);
    const wakeStage=authoredStage(ap,[.16,.38,.68,.88]);

    ctx.save(); ctx.translate(x,baseY-bob); ctx.scale(flip,1);

    function groundShadow(width=27,offset=0){ rect(-Math.floor(width/2),11+offset,width,3,p.shadow); rect(-Math.floor(width/2)+4,14+offset,width-8,1,p.shadow); }
    function tail(kind='neutral',y=0){
      if(kind==='rest'){ rect(-18,2+y,7,3,p.dogDark); rect(-22,4+y,6,3,p.dog); rect(-23,5+y,3,2,p.dogLight); return; }
      const shift=kind==='up'?-2:kind==='down'?2:0;
      rect(-18,-3+y,7,3,p.dogDark); rect(-22,-6+y+shift,6,3,p.dog); rect(-24,-8+y+shift,4,3,p.dogLight);
    }
    function body(crouch=0,lean=0,carryChest=false){
      rect(-14,-4+crouch,25,11,p.dogDark);
      rect(-12,-8+crouch,23,13,p.dog);
      rect(-8,-9+crouch,16,4,p.dogLight);
      rect(-9,-4+crouch,17,7,p.dogLight);
      rect(-6,2+crouch,12,3,p.dogDark);
      rect(5,-4+crouch,5,7,p.dogCream);
      if(carryChest){ rect(7,-2+crouch,4,5,p.dogCream); rect(8,2+crouch,4,2,p.dogDark); }
      if(lean>0){ rect(10,-4+crouch,2+lean,7,p.dog); }
    }
    function plantedLegs(crouch=0){
      rect(-10,5+crouch,5,7,p.dogDark); rect(-11,11+crouch,7,2,p.dogDark);
      rect(4,5+crouch,5,7,p.dogDark); rect(4,11+crouch,7,2,p.dogDark);
      rect(-9,5+crouch,3,4,p.dog); rect(5,5+crouch,3,4,p.dog);
    }
    function walkLegs(frame){
      if(frame===0){
        rect(-11,4,5,8,p.dogDark); rect(-13,11,8,2,p.dogDark); rect(4,5,5,7,p.dogDark); rect(4,11,7,2,p.dogDark);
      } else if(frame===1){
        rect(-9,5,5,7,p.dogDark); rect(-10,11,7,2,p.dogDark); rect(2,5,5,6,p.dogDark); rect(5,10,6,2,p.dogDark);
      } else if(frame===2){
        rect(-9,5,5,7,p.dogDark); rect(-10,11,7,2,p.dogDark); rect(5,4,5,8,p.dogDark); rect(4,11,8,2,p.dogDark);
      } else {
        rect(-8,5,5,6,p.dogDark); rect(-11,10,6,2,p.dogDark); rect(4,5,5,7,p.dogDark); rect(4,11,7,2,p.dogDark);
      }
    }
    function head(headX=6,headY=-15,earMode='neutral',gaze='forward'){
      rect(headX-8,headY-4,14,11,p.dogDark);
      rect(headX-6,headY-7,13,13,p.dog);
      rect(headX-2,headY-6,9,7,p.dogLight);
      rect(headX-1,headY-7,4,2,p.dogCream);
      const nearEarY=earMode==='lift'?-2:earMode==='bounce'?1:0;
      const farEarY=earMode==='lift'?-1:earMode==='bounce'?2:1;
      rect(headX-9,headY-6+nearEarY,5,9,p.dogDark); rect(headX-11,headY-2+nearEarY,5,7,p.dogDark);
      rect(headX+5,headY-5+farEarY,4,8,p.dogDark); rect(headX+7,headY-1+farEarY,4,6,p.dogDark);
      rect(headX+2,headY,8,5,p.dogCream); rect(headX+7,headY+1,3,2,p.eye);
      const eyeY=gaze==='down'?headY-1:gaze==='up'?headY-4:headY-3;
      rect(headX+1,eyeY,2,gaze==='soft'?1:2,p.eye);
      rect(headX+5,headY+4,3,1,p.dogDark);
    }
    function contactPaw(ex,ey,lower=false){
      const shoulderY=lower?1:-1;
      rect(7,shoulderY,4,4,p.dogDark);
      const midX=Math.max(10,Math.round((10+ex)/2)),midY=Math.round((shoulderY+ey)/2);
      drawPixelLine(9,shoulderY+2,midX,midY,p.dogDark,3);
      drawPixelLine(midX,midY,ex,ey,p.dog,3);
      rect(ex-1,ey,4,2,p.dogCream);
    }
    function chestPaws(crouch=0){
      rect(7,-1+crouch,4,5,p.dogDark); rect(9,2+crouch,5,3,p.dog); rect(10,3+crouch,4,2,p.dogCream);
      rect(4,0+crouch,3,5,p.dogDark); rect(6,3+crouch,4,2,p.dogLight);
    }

    if(pose==='sleep'){
      const settle=Math.min(4,sleepStage);
      groundShadow(settle>=2?31:27,1);
      if(settle===0){
        tail('rest',2); body(3,0,false); plantedLegs(3); head(6,-11,'bounce','soft');
      } else if(settle===1){
        rect(-17,5,31,3,p.shadow); tail('rest',3); rect(-14,-2,25,10,p.dogDark); rect(-11,-5,22,11,p.dog); rect(-6,-6,15,5,p.dogLight); head(7,-10,'bounce','soft'); rect(-9,5,9,3,p.dogDark);
      } else if(settle===2){
        rect(-17,5,32,3,p.shadow); rect(-14,-3,27,10,p.dogDark); rect(-11,-7,23,13,p.dog); rect(-5,-8,15,6,p.dogLight); rect(-17,-5,8,7,p.dogDark); rect(-19,-2,7,5,p.dog); head(5,-10,'neutral','soft'); rect(-10,3,10,3,p.dogDark);
      } else {
        rect(-17,5,33,4,p.shadow); rect(-14,-3,27,10,p.dogDark); rect(-11,-7,23,13,p.dog); rect(-6,-8,16,6,p.dogLight);
        rect(-18,-5,8,8,p.dogDark); rect(-20,-1,7,5,p.dog); rect(1,-10,13,10,p.dogDark); rect(3,-12,12,11,p.dog); rect(7,-9,9,7,p.dogCream);
        rect(6,-14,5,6,p.dogDark); rect(11,-13,5,7,p.dogDark); rect(12,-7,2,1,p.eye); rect(-7,2,10,2,p.dogLight); rect(-11,3,8,2,p.dogDark);
        if((Math.floor(now/650)&1)===1) rect(-2,-8,7,1,p.dogLight);
      }
      ctx.restore(); return;
    }

    if(pose==='wake'){
      groundShadow(wakeStage<2?31:27,1);
      if(wakeStage===0){
        rect(-14,-3,27,10,p.dogDark); rect(-11,-7,23,13,p.dog); rect(-5,-8,15,6,p.dogLight); tail('rest',2); head(5,-10,'bounce','soft');
      } else if(wakeStage===1){
        tail('rest',1); body(3,0,false); rect(-10,7,9,5,p.dogDark); rect(3,6,8,5,p.dogDark); head(7,-12,'bounce','soft');
      } else if(wakeStage===2){
        tail('down',1); body(2,0,false); plantedLegs(2); head(7,-14,'neutral','forward');
      } else {
        tail('neutral'); body(); plantedLegs(); head(7,-15,'lift','forward');
      }
      ctx.restore(); return;
    }

    let crouch=0,lean=0,earMode='neutral',gaze='forward',tailMode='neutral',carryChest=false;
    if(pose==='walk'){
      earMode=walkFrame===1?'bounce':walkFrame===3?'lift':'neutral'; tailMode=walkFrame===1?'up':walkFrame===3?'down':'neutral';
    } else if(pose==='inspect'){
      lean=inspectStage>=1&&inspectStage<=2?2:0; earMode=inspectStage>=1?'lift':'neutral'; gaze=inspectStage>=1?'down':'forward';
    } else if(pose==='carry'){
      crouch=pickupStage<=2?1:0; lean=pickupStage===1||pickupStage===2?2:0; earMode=pickupStage===2?'lift':'neutral'; gaze=pickupStage<=2?'down':'forward'; carryChest=pickupStage>=3;
    } else if(pose==='place'){
      crouch=placeStage>=1&&placeStage<=3?2:0; lean=placeStage>=1&&placeStage<=3?2:0; earMode=placeStage===2?'lift':'neutral'; gaze=placeStage>=1&&placeStage<=3?'down':'forward'; carryChest=placeStage===0||placeStage===1;
    } else if(pose==='window'){
      crouch=windowStage===0?1:0; lean=windowStage>=1?1:0; earMode=windowStage>=1?'lift':'neutral'; gaze='up'; tailMode='rest';
    } else if(pose==='rest'){
      crouch=restStage>=1?3:2; earMode='bounce'; gaze='soft'; tailMode='rest';
    } else if(idleFrame){ earMode='lift'; tailMode='down'; }

    groundShadow(pose==='rest'?29:27,pose==='rest'?2:0);
    tail(tailMode,crouch);
    body(crouch,lean,carryChest);
    if(pose==='walk') walkLegs(walkFrame); else plantedLegs(crouch);

    let headX=6+lean,headY=-15+crouch;
    if(pose==='inspect'&&inspectStage>=1){ headX+=2; headY+=1; }
    if(pose==='window'&&windowStage>=1){ headX+=1; headY-=1; }
    if(pose==='rest'){ headX=5; headY=-12+crouch; }
    head(headX,headY,earMode,gaze);

    if(pose==='inspect'&&(inspectStage===1||inspectStage===2)) contactPaw(localTargetX,localTargetY,localTargetY>4);
    if(pose==='carry'){
      if(pickupStage===1) contactPaw(Math.max(12,localTargetX-2),Math.max(-5,localTargetY-1),localTargetY>4);
      else if(pickupStage===2) contactPaw(localTargetX,localTargetY,localTargetY>4);
      else if(pickupStage>=3) chestPaws(crouch);
    }
    if(pose==='place'){
      if(placeStage===0) chestPaws(crouch);
      else if(placeStage===1) contactPaw(Math.max(11,localTargetX-2),Math.min(8,localTargetY-2),true);
      else if(placeStage===2||placeStage===3) contactPaw(localTargetX,localTargetY,true);
      else if(placeStage===4) contactPaw(11,2,false);
    }
    if(pose==='window'&&windowStage>=1){ rect(8,-7,4,6,p.dogDark); rect(10,-3,5,2,p.dogCream); rect(4,-6,3,5,p.dogDark); }

    ctx.restore();
  }
  function drawCreature(f,now,p){
    const rs=creatureRenderState(f,now); drawMossSprite(f,now,rs,p);
    if(f.creature.carrying){ const obj=f.objects.find(o=>o.id===f.creature.carrying)||previous?.objects?.find(o=>o.id===f.creature.carrying); if(obj&&rs.carried_rendered_x!==null) drawObject({...obj,state:'placed',x:rs.carried_rendered_x,y:rs.carried_rendered_y},p); }
    return rs;
  }

  function drawForegroundFurniture(f,now,p){
    for(const y of [62,87,112]) rect(303,y,70,2,p.walnutDark);
    rect(303,151,68,4,p.walnutDark); rect(305,151,64,1,p.walnutLight);
    if(f.creature.zone==='window'&&f.creature.activity==='look_outside'){ rect(44,155,82,3,p.walnutDark); rect(47,155,76,1,p.walnutLight); }
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
