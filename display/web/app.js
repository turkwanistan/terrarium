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
    idle: 950, rest: 1450, loaf: 2300, groom: 2300, stretch: 2100, react: 1800,
    inspect: 1800, nudge: 2100, carry: 1900, place: 2200,
    look_outside: 1700, sleep: 2200, wake: 2000, walk: 1300,
  });

  const SCENE_LAYERS = Object.freeze({BACK:0,STRUCTURE:1,SURFACE:2,WORLD:3,ACTORS:4,FRONT:5,ALWAYS_FRONT:6});
  let PALETTES = null;
  let ART_MANIFEST = null;
  const ART_ASSETS = new Map();
  const ART_CACHE = new Map();

  async function fetchJson(path){
    const response=await fetch(path,{cache:'no-store'});
    if(!response.ok) throw new Error(`unable to load authored art ${path}: HTTP ${response.status}`);
    return response.json();
  }
  function validateAsset(asset,entry,roles){
    if(asset?.schema!=='terrarium.pixel-asset.v1'||asset.id!==entry.id) throw new Error(`invalid authored asset identity: ${entry.id}`);
    if(!Number.isInteger(asset.width)||!Number.isInteger(asset.height)||asset.width<1||asset.height<1) throw new Error(`invalid authored asset dimensions: ${entry.id}`);
    if(!Array.isArray(asset.anchor)||asset.anchor.length!==2||!asset.anchor.every(Number.isInteger)) throw new Error(`invalid authored asset anchor: ${entry.id}`);
    if(!Array.isArray(asset.runs)||asset.runs.length<1) throw new Error(`authored asset has no pixel runs: ${entry.id}`);
    for(const run of asset.runs){
      if(!Array.isArray(run)||run.length!==5) throw new Error(`invalid pixel run in ${entry.id}`);
      const [x,y,w,h,role]=run;
      if(![x,y,w,h].every(Number.isInteger)||x<0||y<0||w<1||h<1||x+w>asset.width||y+h>asset.height) throw new Error(`out-of-bounds pixel run in ${entry.id}`);
      if(typeof role!=='string'||!roles.has(role)) throw new Error(`unknown palette role ${role} in ${entry.id}`);
    }
  }
  async function loadArtBundle(){
    const manifest=await fetchJson('/art/manifest.json');
    if(manifest?.schema!=='terrarium.art-manifest.v1') throw new Error('invalid authored art manifest schema');
    if(JSON.stringify(manifest.art_surface)!=='[400,240]'||manifest.tile_size!==16||JSON.stringify(manifest.grid)!=='[25,15]') throw new Error('authored art grid must be 400x240, 16px tiles, 25x15 cells');
    if(manifest.grid[0]*manifest.tile_size!==ART_W||manifest.grid[1]*manifest.tile_size!==ART_H) throw new Error('authored art grid does not exactly cover the art surface');
    const paletteBank=await fetchJson(`/art/${manifest.palette_source}`);
    if(paletteBank?.schema!=='terrarium.palette-bank.v1'||!paletteBank.palettes) throw new Error('invalid authored palette bank');
    const roles=new Set(paletteBank.required_roles||[]);
    for(const [name,palette] of Object.entries(paletteBank.palettes)) for(const role of roles) if(typeof palette[role]!=='string') throw new Error(`palette ${name} is missing role ${role}`);
    PALETTES=Object.freeze(paletteBank.palettes);
    ART_MANIFEST=manifest;
    for(const entry of manifest.assets||[]){
      if(!(entry.layer in SCENE_LAYERS)) throw new Error(`unknown scene layer ${entry.layer} for ${entry.id}`);
      const asset=await fetchJson(`/art/${entry.path}`);
      validateAsset(asset,entry,roles);
      ART_ASSETS.set(entry.id,Object.freeze({...asset,kind:entry.kind,layer:entry.layer}));
    }
    window.__terrariumAuthoredArt=Object.freeze({schema:manifest.schema,tile_size:manifest.tile_size,grid:manifest.grid,asset_count:ART_ASSETS.size,assets:[...ART_ASSETS.keys()],palette_names:Object.keys(PALETTES),material_families:paletteBank.material_families});
  }
  function compiledAsset(id,paletteName){
    const asset=ART_ASSETS.get(id); if(!asset) throw new Error(`unknown authored asset: ${id}`);
    const palette=PALETTES[paletteName]; if(!palette) throw new Error(`unknown authored palette: ${paletteName}`);
    const key=`${id}@${paletteName}`; if(ART_CACHE.has(key)) return ART_CACHE.get(key);
    const surface=document.createElement('canvas'); surface.width=asset.width; surface.height=asset.height;
    const assetCtx=surface.getContext('2d',{alpha:true}); assetCtx.imageSmoothingEnabled=false; assetCtx.clearRect(0,0,asset.width,asset.height);
    for(const [x,y,w,h,role] of asset.runs){ assetCtx.fillStyle=palette[role]; assetCtx.fillRect(x,y,w,h); }
    const compiled=Object.freeze({surface,anchor:asset.anchor,width:asset.width,height:asset.height}); ART_CACHE.set(key,compiled); return compiled;
  }
  function drawAuthoredAsset(id,x,y,paletteName,{flipX=false}={}){
    const compiled=compiledAsset(id,paletteName),[anchorX,anchorY]=compiled.anchor;
    ctx.save(); ctx.translate(Math.round(x),Math.round(y)); if(flipX) ctx.scale(-1,1); ctx.imageSmoothingEnabled=false; ctx.drawImage(compiled.surface,-anchorX,-anchorY); ctx.restore();
  }
  function createSceneQueue(){
    let serial=0; const entries=[];
    return {
      add(layer,y,id,draw){ if(!(layer in SCENE_LAYERS)) throw new Error(`unknown scene layer: ${layer}`); entries.push({layer,y:Number(y)||0,id,draw,serial:serial++}); },
      flush(){ entries.sort((a,b)=>SCENE_LAYERS[a.layer]-SCENE_LAYERS[b.layer]||a.y-b.y||a.serial-b.serial); for(const entry of entries) entry.draw(); },
      metadata(){ return entries.map(({layer,y,id})=>({layer,y,id})); },
    };
  }

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
      activity_corner:activityEngagement(f,now,'activity_corner',['inspect','nudge','carry','place','loaf','groom','stretch']),
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
    const transitions=[[360,'night','dawn'],[480,'dawn','day'],[1050,'day','dusk'],[1170,'dusk','night']];
    let paletteName=f.lighting in PALETTES?f.lighting:'day';
    for(const [center,from,to] of transitions){
      if(minute>=center-30&&minute<center+30){ const q=Math.floor(clamp01((minute-(center-30))/60)*4); paletteName=q<2?from:to; break; }
    }
    return {palette:PALETTES[paletteName],palette_name:paletteName,night:paletteName==='night'?1:0,minute};
  }

  function drawPixelLine(x0,y0,x1,y1,color,thickness=1){
    x0=Math.round(x0); y0=Math.round(y0); x1=Math.round(x1); y1=Math.round(y1);
    const dx=Math.abs(x1-x0), sx=x0<x1?1:-1, dy=-Math.abs(y1-y0), sy=y0<y1?1:-1;
    let err=dx+dy;
    while(true){ rect(x0-Math.floor(thickness/2),y0-Math.floor(thickness/2),thickness,thickness,color); if(x0===x1&&y0===y1) break; const e2=2*err; if(e2>=dy){err+=dy;x0+=sx;} if(e2<=dx){err+=dx;y0+=sy;} }
  }

  function worldEventRenderState(f,now){
    const e=f.world_event; if(!e) return null;
    let x=Number(e.x),y=Number(e.y);
    const prior=previous?.world_event;
    if(!snapshotPath&&prior?.id===e.id){
      const t=smoother01((now-fetchedAt)/MOTION.environment_ms);
      x=mix(Number(prior.x),x,t); y=mix(Number(prior.y),y,t);
    }
    const minute=worldMinuteAt(f,now),start=Number(e.start_world_minute),end=Math.max(start+1,Number(e.end_world_minute));
    return {...e,x,y,progress:clamp01((minute-start)/(end-start))};
  }

  function drawFloorWorldEvent(f,now,p){
    const e=worldEventRenderState(f,now); if(!e||e.type!=='sunlight') return;
    const x=px(e.x),y=px(e.y);
    // Hard-edged finite-palette sunlight: an authored rug patch, not an alpha spotlight.
    rect(x-22,y-6,44,3,p.amber); rect(x-26,y-3,52,6,p.amber); rect(x-22,y+3,44,3,p.amber);
    rect(x-15,y-4,20,1,p.creamShade); rect(x+7,y+1,12,1,p.rugLight);
    rect(x-19,y+5,9,1,p.rugLight);
  }

  function drawInteriorWorldEvent(f,now,p){
    const e=worldEventRenderState(f,now); if(!e||e.type!=='moth') return;
    const x=px(e.x),y=px(e.y),wing=(Math.floor(now/420)&1);
    rect(x-1,y,2,2,p.creamShade);
    rect(x-4,y-2-wing,3,2,p.cream); rect(x+1,y-2+wing,3,2,p.cream);
    rect(x-2,y+2,1,1,p.amber);
  }

  function drawWindowWorldEvent(f,now,p){
    const e=worldEventRenderState(f,now); if(!e||e.source_zone!=='window') return;
    const x=px(e.x),y=px(e.y);
    if(e.type==='bird'){
      const wing=(Math.floor(now/520)&1);
      rect(x-4,y,8,2,p.walnutDark); rect(x+3,y-2,3,2,p.walnutDark);
      rect(x-2,y-2-wing,3,2,p.shadow); rect(x-1,y+2+wing,3,1,p.shadow);
      rect(x+6,y-1,1,1,p.amber);
    } else if(e.type==='rain_intensify'){
      for(let i=0;i<7;i++){ const dx=((i*11)%35)-17,dy=((i*17+Math.floor(now/170))%31)-15; rect(x+dx,y+dy,1,4,p.rain); }
      rect(x-16,96,31,1,p.rain);
    } else if(e.type==='thunder'){
      if((Math.floor(now/360)&3)!==3){
        drawPixelLine(x+3,y-13,x-2,y-3,p.cream,2); drawPixelLine(x-2,y-3,x+2,y+3,p.creamShade,2); drawPixelLine(x+2,y+3,x-4,y+12,p.cream,2);
      }
    } else if(e.type==='leaf_tap'){
      const sway=(Math.floor(now/460)&1);
      rect(x-4,y-2+sway,7,3,p.amber); rect(x-2,y-4+sway,5,2,p.amber);
      drawPixelLine(x-4,y+2,x+3,y-4,p.walnutDark,1);
    }
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

  function drawWindowBack(f,now,p,paletteName){
    drawAuthoredAsset('environment.window-view',32,30,paletteName);
    if(f.lighting==='night'){
      rect(108,41,10,8,p.cream); rect(105,44,13,5,p.cream); rect(111,39,4,2,p.cream);
      rect(48,42,2,2,p.creamShade); rect(64,52,1,1,p.cream); rect(121,57,2,1,p.creamShade);
    } else {
      rect(105,39,14,10,p.amber); rect(102,42,20,5,p.amber); rect(109,36,6,3,p.cream);
    }
    if(f.weather==='rain'){
      const phase=Math.floor(now/150)%19;
      for(const d of rain){
        const x=34+d.x%96,y=31+((d.y+phase+d.phase)%67);
        rect(x,y,1,3,p.rain); if((d.phase&1)===0) rect(x-1,y+3,1,2,p.rain);
      }
      for(const [x,y,w] of [[38,92,9],[58,88,5],[91,94,11],[115,90,7]]){ rect(x,y,w,1,p.rain); rect(x+2,y+1,Math.max(2,w-4),1,p.skyDark); }
    } else if(f.weather==='mist'){
      for(let y=45;y<91;y+=12) for(let x=35+(y%3);x<129;x+=19) rect(x,y,9,2,p.rain);
    }
    drawWindowWorldEvent(f,now,p);
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
  }
  function drawWindowStructure(f,now,p,paletteName){
    drawAuthoredAsset('structure.window-alcove',14,18,paletteName);
    if(causalActivityState(f,now).window>0){ const cx=clamp(px(f.creature.x),44,121); rect(cx-8,103,16,2,p.creamShade); rect(cx-4,105,8,1,p.walnutLight); }
  }
  function drawBed(f,now,p,paletteName){
    drawAuthoredAsset('structure.sleeping-nook',18,170,paletteName);
    const sleepTicks=historyValue(f,'sleep_nook_ticks',now),sleepBouts=historyValue(f,'sleep_nook_bouts',now);
    const nest=emergence(sleepTicks,0,18);
    if(nest>0){
      rect(77,196,43+Math.floor(8*emergence(sleepBouts,0,5)),5,p.walnutDark); rect(84,194,24,2,p.floorShade);
      if(nest>.45){ rect(88,192,13,1,p.creamShade); rect(105,198,10,1,p.skyDark); }
    }
    for(let i=0;i<4;i++){
      const strength=emergence(sleepTicks,1+i*3.5,8); if(strength>.2){ rect(65+i*12,187+i*2,8,1,p.walnutLight); rect(70+i*10,193+i,6,1,p.skyDark); }
    }
  }
  function drawRug(p,paletteName){
    drawAuthoredAsset('surface.living-rug',140,170,paletteName);
  }
  function drawShelf(f,p,paletteName){ drawAuthoredAsset('structure.collection-shelf',293,27,paletteName); }
  function drawActivityCorner(f,now,p,paletteName){
    drawAuthoredAsset('structure.activity-desk',286,145,paletteName);
    const uses=historyValue(f,'activity_corner_uses',now);
    for(let i=0;i<5;i++){
      const strength=emergence(uses,1+i*4.2,8); if(strength<=0) continue;
      const x=300+i*12+(stableUnit('paper',i)>.5?2:0),y=168-(i%2)*3;
      rect(x,y,11,5,p.paper); rect(x+2,y+2,6,1,p.walnutLight); if(strength>.6) rect(x+8,y+1,2,1,p.amber);
    }
    for(let i=0;i<7;i++){ const strength=emergence(uses,2+i*3.2,7); if(strength>.1) rect(304+i*8,172-(i%3),5,1,p.walnutDark); }
    drawAuthoredAsset('environment.desk-plant',368,151,paletteName);
    if(causalActivityState(f,now).activity_corner>0){ const hx=clamp(px(f.creature.x)-4,305,356); rect(hx-6,174,12,1,p.cream); }
  }
  function drawBowls(p,paletteName){
    drawAuthoredAsset('prop.water-bowl',256,206,paletteName);
    drawAuthoredAsset('prop.food-bowl',284,205,paletteName);
  }
  function drawBackground(f,now,p,paletteName){
    drawAuthoredAsset('structure.room-shell',0,0,paletteName);
    drawWindowBack(f,now,p,paletteName);
    const phase=Math.floor(now/850);
    for(const mote of motes){ if((phase+Math.floor(mote.phase))%5!==0) continue; rect(mote.x,mote.y,1,1,p.cream); }
    return p;
  }
  function drawStructureLayer(f,now,p,paletteName){
    drawWindowStructure(f,now,p,paletteName);
    drawBed(f,now,p,paletteName);
    drawShelf(f,p,paletteName);
    drawActivityCorner(f,now,p,paletteName);
  }
  function drawSurfaceLayer(f,now,p,paletteName){
    drawAuthoredAsset('tile.floor-detail',16,164,paletteName);
    drawRug(p,paletteName);
    drawFloorWorldEvent(f,now,p);
    drawPersistentHistory(f,p);
    rect(276,149,4,2,p.amber); rect(280,147,2,4,p.foliage); rect(273,148,2,2,p.cream);
    rect(268,151,14,2,p.walnutDark); rect(271,147,8,4,p.walnut); rect(274,144,3,3,p.leafBright);
  }
  function drawWorldAtmosphere(f,now,p){
    drawInteriorWorldEvent(f,now,p);
  }
  function placedObjectRenderState(o, f, now) {
    const source=previous?.objects?.find(item=>item.id===o.id);
    if(!snapshotPath&&source?.state==='carried'&&o.state==='placed'){
      const raw=clamp01((now-fetchedAt)/MOTION.placement_ms),t=smoother01((raw-.34)/.58),facing=previous?.creature?.facing==='left'?-1:1;
      const originX=(transitionSource?.x??Number(previous.creature.x))+facing*22, originY=(transitionSource?.y??Number(previous.creature.y))-4;
      return {x:mix(originX,Number(o.x),t),y:mix(originY,Number(o.y),t),progress:t,phase:raw<.34?'prepare':t<1?'lower-contact':'settled',transitioning:t<1};
    }
    const displaced=!snapshotPath&&source?.state==='placed'&&o.state==='placed'&&(Number(source.x)!==Number(o.x)||Number(source.y)!==Number(o.y));
    if(displaced&&f.creature?.activity==='nudge'&&f.last_event?.object_id===o.id){
      const raw=clamp01((now-fetchedAt)/(ACTION_DURATION.nudge||MOTION.activity_ms)),t=smoother01((raw-.30)/.48);
      return {x:mix(Number(source.x),Number(o.x),t),y:mix(Number(source.y),Number(o.y),t),progress:t,phase:raw<.30?'paw-contact':t<1?'nudge-slide':'settled',transitioning:t<1};
    }
    return {x:Number(o.x),y:Number(o.y),progress:1,phase:'settled',transitioning:false};
  }
  function activePlacementState(f,now){
    if(!previous||snapshotPath) return null;
    for(const o of f.objects||[]){
      const source=previous.objects?.find(item=>item.id===o.id);
      const changed=source?.state==='carried'&&o.state==='placed'||(source?.state==='placed'&&o.state==='placed'&&(Number(source.x)!==Number(o.x)||Number(source.y)!==Number(o.y)));
      if(changed){ const rs=placedObjectRenderState(o,f,now); return {object_id:o.id,rendered_x:Number(rs.x.toFixed(6)),rendered_y:Number(rs.y.toFixed(6)),target_x:Number(o.x),target_y:Number(o.y),progress:Number(rs.progress.toFixed(6)),phase:rs.phase}; }
    }
    return null;
  }

  const OBJECT_ART = Object.freeze({
    blue_stone:{default:'settled',settled:'object.blue-stone.settled',rolled:'object.blue-stone.rolled'},
    acorn:{default:'settled',settled:'object.acorn.settled',rolled:'object.acorn.rolled'},
    red_thread:{default:'loose',loose:'object.red-thread.loose',rumpled:'object.red-thread.rumpled',nested:'object.red-thread.nested'},
    amber_leaf:{default:'fresh',fresh:'object.amber-leaf.fresh',handled:'object.amber-leaf.handled'},
    shell:{default:'handled',handled:'object.shell.handled',displayed:'object.shell.displayed'},
    glass_star:{default:'handled',handled:'object.glass-star.handled',displayed:'object.glass-star.displayed'},
  });
  function objectAssetId(o){
    const variants=OBJECT_ART[o.id]; if(!variants) throw new Error(`unknown authored object: ${o.id}`);
    const state=String(o.interaction_state||variants.default); return variants[state]||variants[variants.default];
  }
  function drawObject(o,paletteName){
    if(o.state==='carried') return;
    drawAuthoredAsset(objectAssetId(o),px(o.x),px(o.y),paletteName);
  }
  function drawWorldObject(o,f,now,paletteName){ if(o.state==='carried') return; const rs=placedObjectRenderState(o,f,now); drawObject({...o,x:rs.x,y:rs.y},paletteName); }

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
    else if(!moving&&target&&['inspect','nudge','carry','place'].includes(c.activity)&&Math.abs(Number(target.x)-continuousX)>3) renderedFacing=Number(target.x)>=continuousX?'right':'left';
    const direction=renderedFacing==='left'?-1:1,strideCount=Math.max(2,Math.round(routeTotal/58)),walkPhase=travel*Math.PI*2*strideCount;
    let carryDirection=direction,turningCarry=false;
    if(moving&&c.carrying&&routeState.segment_index>0){
      const priorA=route[routeState.segment_index-1],priorB=route[routeState.segment_index],priorDx=priorB.x-priorA.x;
      const priorDirection=Math.abs(priorDx)>3?(priorDx>0?1:-1):direction;
      if(priorDirection!==direction&&routeState.segment_progress<.20){ const blend=smoother01(routeState.segment_progress/.20);carryDirection=mix(priorDirection,direction,blend);turningCarry=true; }
    }
    const walkFrame=moving?(Math.floor(walkPhase/(Math.PI/2))&3):0;
    const walkBob=0; // body shift is authored into the four locomotion sprites; keep the semantic base planted.
    const renderedX=snapDisplay(continuousX),renderedBaseY=snapDisplay(continuousBaseY),renderedY=renderedBaseY-walkBob*SCALE;
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
      ambient_classes:[f.weather==='rain'?'rain':f.weather==='mist'?'mist':null,f.world_event?`world-event-${f.world_event.type}`:null,'pixel-motes',moving?'walk-cycle':null,causal.sleep_nook>0?'bedding-contact':null,causal.window>0?'window-contact':null,causal.activity_corner>0?'work-surface-contact':null].filter(Boolean),
      world_event:f.world_event?{id:f.world_event.id,type:f.world_event.type,x:Number(f.world_event.x),y:Number(f.world_event.y),attention_status:f.world_event.attention_status,temporary_affordance:f.world_event.temporary_affordance||null}:null,
      art_grid:{width:ART_W,height:ART_H,scale:SCALE,x:px(renderedX),y:px(renderedBaseY)},
    };
  }

  function mossFrameAsset(pose, stage, walkFrame) {
    if(pose==='walk') return `moss.walk.${walkFrame&3}`;
    if(pose==='inspect') return ['moss.inspect.anticipate','moss.inspect.contact','moss.inspect.hold','moss.inspect.recover'][Math.min(3,stage)];
    if(pose==='nudge') return ['moss.nudge.anticipate','moss.nudge.contact','moss.nudge.press','moss.nudge.hold','moss.nudge.recover'][Math.min(4,stage)];
    if(pose==='carry') return ['moss.pickup.anticipate','moss.pickup.contact','moss.pickup.lift','moss.pickup.hold','moss.carry'][Math.min(4,stage)];
    if(pose==='place') return ['moss.place.hold','moss.place.lower','moss.place.contact','moss.place.release','moss.place.recover','moss.place.recover'][Math.min(5,stage)];
    if(pose==='window') return stage===0?'moss.window.ready':'moss.window.watch';
    if(pose==='rest') return 'moss.rest';
    if(pose==='loaf') return 'moss.loaf';
    if(pose==='groom') return ['moss.groom.start','moss.groom.contact','moss.groom.hold','moss.groom.recover','moss.groom.recover'][Math.min(4,stage)];
    if(pose==='stretch') return ['moss.stretch.ready','moss.stretch.extend','moss.stretch.hold','moss.stretch.recover','moss.stretch.recover'][Math.min(4,stage)];
    if(pose==='react') return 'moss.react';
    if(pose==='sleep') return ['moss.sleep.settle0','moss.sleep.settle1','moss.sleep.settle2','moss.sleep.settle3','moss.sleep.curled'][Math.min(4,stage)];
    if(pose==='wake') return ['moss.wake.0','moss.wake.1','moss.wake.2','moss.wake.3','moss.idle'][Math.min(4,stage)];
    return 'moss.idle';
  }

  function drawMossContactReach(x,baseY,flip,target,p,{lower=false}){
    if(!target) return;
    const localTargetX=clamp((px(target.x)-x)*flip,10,19),localTargetY=clamp(px(target.y)-baseY,-14,10),shoulderY=lower?1:-1;
    ctx.save(); ctx.translate(x,baseY); ctx.scale(flip,1);
    rect(7,shoulderY,4,4,p.dogDark);
    const midX=Math.max(10,Math.round((10+localTargetX)/2)),midY=Math.round((shoulderY+localTargetY)/2);
    drawPixelLine(9,shoulderY+2,midX,midY,p.dogDark,3);
    drawPixelLine(midX,midY,localTargetX,localTargetY,p.dog,3);
    rect(localTargetX-1,localTargetY,4,2,p.dogCream);
    ctx.restore();
  }

  function drawMossSprite(f,now,rs,p,paletteName){
    const c=f.creature,flip=rs.facing==='left'?-1:1,ap=rs.activity_progress,prior=previous?.creature?.activity;
    const x=px(rs.rendered_x),baseY=px(rs.rendered_base_y),target=actionTargetPoint(f);
    let pose='idle';
    if(c.activity==='sleep'||c.pose==='sleep') pose='sleep';
    else if(c.activity==='wake') pose='wake';
    else if(rs.moving) pose='walk';
    else if(c.activity==='inspect') pose='inspect';
    else if(c.activity==='nudge') pose='nudge';
    else if(c.activity==='carry') pose='carry';
    else if(c.activity==='place') pose='place';
    else if(c.activity==='look_outside') pose='window';
    else if(c.activity==='rest') pose='rest';
    else if(c.activity==='loaf') pose='loaf';
    else if(c.activity==='groom') pose='groom';
    else if(c.activity==='stretch') pose='stretch';
    else if(c.activity==='react') pose='react';

    const walkFrame=rs.walk_keyframe||0;
    const inspectStage=authoredStage(ap,[.20,.46,.76]);
    const nudgeStage=authoredStage(ap,[.18,.36,.58,.78]);
    const groomStage=authoredStage(ap,[.18,.42,.72,.88]);
    const stretchStage=authoredStage(ap,[.18,.38,.68,.88]);
    const pickupStage=authoredStage(ap,[.16,.34,.58,.80]);
    const placeStage=authoredStage(ap,[.16,.34,.58,.78,.92]);
    const windowStage=authoredStage(ap,[.18,.46,.78]);
    const sleepStage=prior==='sleep'?4:authoredStage(ap,[.14,.34,.58,.82]);
    const wakeStage=authoredStage(ap,[.16,.38,.68,.88]);
    let stage=0;
    if(pose==='inspect')stage=inspectStage; else if(pose==='nudge')stage=nudgeStage; else if(pose==='carry')stage=pickupStage;
    else if(pose==='place')stage=placeStage; else if(pose==='window')stage=windowStage; else if(pose==='groom')stage=groomStage;
    else if(pose==='stretch')stage=stretchStage; else if(pose==='sleep')stage=sleepStage; else if(pose==='wake')stage=wakeStage;

    const assetId=mossFrameAsset(pose,stage,walkFrame);
    drawAuthoredAsset(assetId,x,baseY,paletteName,{flipX:flip===-1});

    // Exact target reach stays presentation-dependent; the finished body/head/legs/tail silhouette is authored.
    if(pose==='inspect'&&(inspectStage===1||inspectStage===2)) drawMossContactReach(x,baseY,flip,target,p,{lower:false});
    else if(pose==='nudge'&&nudgeStage>=1&&nudgeStage<=3) drawMossContactReach(x,baseY,flip,target,p,{lower:true});
    else if(pose==='carry'&&(pickupStage===1||pickupStage===2)) drawMossContactReach(x,baseY,flip,target,p,{lower:pickupStage===2});
    else if(pose==='place'&&placeStage>=1&&placeStage<=3) drawMossContactReach(x,baseY,flip,target,p,{lower:true});
  }
  function drawCreature(f,now,p,rs,paletteName){
    rs=rs||creatureRenderState(f,now); drawMossSprite(f,now,rs,p,paletteName);
    if(f.creature.carrying){ const obj=f.objects.find(o=>o.id===f.creature.carrying)||previous?.objects?.find(o=>o.id===f.creature.carrying); if(obj&&rs.carried_rendered_x!==null) drawObject({...obj,state:'placed',x:rs.carried_rendered_x,y:rs.carried_rendered_y},paletteName); }
    return rs;
  }

  function drawForegroundFurniture(f,now,p,paletteName){
    drawAuthoredAsset('front.collection-shelf-lips',293,27,paletteName);
    drawAuthoredAsset('front.activity-desk-lip',286,145,paletteName);
    if(f.creature.zone==='window'&&f.creature.activity==='look_outside') drawAuthoredAsset('front.window-perch',42,149,paletteName);
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
    const lighting=visualLighting(frame,now),p=lighting.palette,paletteName=lighting.palette_name;
    const scene=createSceneQueue();
    const renderState=creatureRenderState(frame,now);
    scene.add('BACK',0,'room-shell-and-window-view',()=>drawBackground(frame,now,p,paletteName));
    scene.add('STRUCTURE',158,'room-zones',()=>drawStructureLayer(frame,now,p,paletteName));
    scene.add('SURFACE',160,'room-surface-and-history',()=>drawSurfaceLayer(frame,now,p,paletteName));
    scene.add('WORLD',0,'world-atmosphere',()=>drawWorldAtmosphere(frame,now,p));
    scene.add('WORLD',210,'room-bowls',()=>drawBowls(p,paletteName));
    for(const o of frame.objects) scene.add('WORLD',px(o.y),`object:${o.id}`,()=>drawWorldObject(o,frame,now,paletteName));
    scene.add('ACTORS',px(renderState.rendered_base_y),'actor:moss',()=>drawCreature(frame,now,p,renderState,paletteName));
    scene.add('FRONT',px(renderState.rendered_base_y)+1,'room-foreground',()=>{ drawForegroundFurniture(frame,now,p,paletteName); drawForegroundCausality(frame,now,renderState,p); });
    scene.flush();
    window.__terrariumSceneLayers=scene.metadata();
    presentArtSurface();
    if(debugVisible){ debug.hidden=false; debug.textContent=JSON.stringify({mode:snapshotPath?'snapshot':'live',connected,tick:frame.tick,lighting:frame.lighting,weather:frame.weather,world_event:frame.world_event,art_surface:[ART_W,ART_H],art_grid:[25,15],tile_size:16,palette:paletteName,scene_layers:window.__terrariumSceneLayers,display:[DISPLAY_W,DISPLAY_H],scale:SCALE,creature:frame.creature,last_event:frame.last_event,poll_error:lastPollError},null,2); } else debug.hidden=true;
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

  window.__terrariumPixelRenderer = Object.freeze({art_width:ART_W,art_height:ART_H,display_width:DISPLAY_W,display_height:DISPLAY_H,integer_scale:SCALE,smoothing:false,tile_size:16,art_grid:[25,15],scene_layers:Object.keys(SCENE_LAYERS),asset_schema:'terrarium.pixel-asset.v1'});
  document.addEventListener('keydown',ev=>{if(ev.key.toLowerCase()==='d')debugVisible=!debugVisible;});
  async function start(){
    try{ await loadArtBundle(); }
    catch(err){ connected=false; lastPollError=String(err); console.error(err); rect(0,0,ART_W,ART_H,'#25242b'); presentArtSurface(); document.title='Terrarium Art Error'; if(temporalScenario)publishTemporal({schema:'terrarium.art-error.v1',status:'error',scenario:temporalScenario,error:String(err)}); return; }
    if(temporalScenario)loadTemporalScenario();else if(snapshotPath){await loadSnapshot();requestAnimationFrame(render);}else{await poll();setInterval(poll,700);requestAnimationFrame(render);}
  }
  start();
})();
