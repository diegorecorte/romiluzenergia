import * as THREE from './vendor/three.module.js';
import { OrbitControls } from './vendor/OrbitControls.js';
import { energyState } from './energy-state.mjs';

const root = document.querySelector('#energy-experience');
if (root) initEnergy(root);
function initEnergy(root) {
  const stage = root.querySelector('#energy-stage');
  const loading = root.querySelector('#energy-loading');
  const fallback = root.querySelector('#energy-fallback');
  const modes = [...root.querySelectorAll('[data-energy-mode]')];
  const backup = root.querySelector('#energy-backup');
  const flowToggle = root.querySelector('#energy-flows');
  const pauseButton = root.querySelector('#energy-pause');
  let mode = 'day';
  let paused = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let state = energyState(mode, backup.checked);
  let syncScene = () => {};
  function update() {
    state = energyState(mode, backup.checked);
    for (const part of ['solar','home','battery','car','grid']) root.querySelector('#energy-'+part+'-status').textContent = state[part];
    root.querySelector('#energy-title').textContent = state.title;
    root.querySelector('#energy-description').textContent = state.description;
    modes.forEach(button => button.setAttribute('aria-pressed',String(button.dataset.energyMode === mode)));
    pauseButton.setAttribute('aria-pressed',String(paused));
    pauseButton.textContent = paused ? 'Reanudar movimiento' : 'Pausar movimiento';
    syncScene();
  }
  modes.forEach(button => button.addEventListener('click', () => {mode = button.dataset.energyMode;update();}));
  backup.addEventListener('change',update);
  flowToggle.addEventListener('change',update);
  pauseButton.addEventListener('click',() => {paused = !paused;update();});
  update();
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'low-power'});
  } catch(error) {
    loading.textContent = 'La vista 3D no está disponible en este navegador. Puedes seguir explorando las explicaciones de cada situación.';
    root.querySelector('#energy-reset').disabled = true;
    pauseButton.disabled = true;
    return;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1,1.7));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.25;
  renderer.domElement.setAttribute('aria-label','Vivienda tridimensional con paneles solares, batería mural y coche conectado. Arrastra para girar la escena.');
  renderer.domElement.setAttribute('role','img');
  stage.prepend(renderer.domElement);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#e6edf2');
  scene.fog = new THREE.Fog('#e6edf2',45,100);
  const camera = new THREE.PerspectiveCamera(38,1,.1,180);
  const defaultPosition = new THREE.Vector3(21,16,23);
  camera.position.copy(defaultPosition);
  const controls = new OrbitControls(camera,renderer.domElement);
  controls.target.set(0,1,0);
  controls.enableDamping = true;
  controls.enablePan = false;
  controls.minDistance = 14;
  controls.maxDistance = 40;
  controls.maxPolarAngle = Math.PI/2.12;
  controls.minPolarAngle = .3;
  controls.autoRotate = false;
  root.querySelector('#energy-reset').addEventListener('click',() => {camera.position.copy(defaultPosition);controls.target.set(0,1,0);controls.update();});
  const hemi = new THREE.HemisphereLight('#f0f7ff','#586448',2.5);scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff1da',4);sun.position.set(-6,16,9);sun.castShadow = true;
  const shadowSize=stage.clientWidth<640?1024:2048;sun.shadow.mapSize.set(shadowSize,shadowSize);Object.assign(sun.shadow.camera,{left:-18,right:18,top:16,bottom:-16,near:.5,far:50});sun.shadow.bias=-.0005;sun.shadow.normalBias=.025;scene.add(sun);
  const fill = new THREE.DirectionalLight('#adc7e2',.7);fill.position.set(8,5,-10);scene.add(fill);
  const standard = (color,roughness=.7,metalness=0) => new THREE.MeshStandardMaterial({color,roughness,metalness});
  const white = standard('#e8e6dd',.93), concrete=standard('#b6b4ad'),darkMetal=standard('#333e44',.3,.65), silver=standard('#9eaab2',.25,.8), roofMat=standard('#6d706d',.8),wood=standard('#9a7250',.8);
  const glass = new THREE.MeshPhysicalMaterial({color:'#638596',roughness:.13,metalness:.28,clearcoat:1,transparent:true,opacity:.83});
  const windowLight = new THREE.MeshStandardMaterial({color:'#829dab',roughness:.2,metalness:.35,emissive:'#f3c675',emissiveIntensity:0});
  const meshes=[];
  function box(w,h,d,material,x=0,y=0,z=0,parent=scene){
    const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);meshes.push(m);return m;
  }
  function cylinder(top,bottom,height,material,x,y,z,parent=scene){const m=new THREE.Mesh(new THREE.CylinderGeometry(top,bottom,height,20),material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
  function cable(points,material,radius=.035,parent=scene){const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));const m=new THREE.Mesh(new THREE.TubeGeometry(curve,40,radius,8,false),material);parent.add(m);return curve;}
  function labelTexture(text,bg='#f1f1e9',ink='#064e83'){
    const c=document.createElement('canvas');c.width=512;c.height=256;const ctx=c.getContext('2d');ctx.fillStyle=bg;ctx.fillRect(0,0,512,256);ctx.fillStyle=ink;ctx.textAlign='center';ctx.font='bold 56px Arial';ctx.fillText(text,256,145);const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;return new THREE.MeshStandardMaterial({map:tex,roughness:.7});
  }
  // Parcela, acceso y vivienda a escala aproximada, sin marcas de equipos inventadas.
  box(24,.3,18,standard('#b8c4aa'),0,-.25,0);
  box(8,.09,10,standard('#b0b5b6'),6,.02,3.8);
  for(let x=2.5;x<10;x+=1)for(let z=0;z<8;z+=1)box(.97,.015,.97,standard((Math.round(x+z)%2)?'#b8bcba':'#b1b6b5'),x,.075,z);
  box(9,.14,7,concrete,-2,.02,-2);
  box(8,3.2,6,white,-2,1.67,-2);
  const roofAngle=Math.atan(1.6/3);
  const south=box(8.8,.14,3.6,roofMat,-2,4.15,-.5);south.rotation.x=roofAngle;
  const north=box(8.8,.14,3.6,roofMat,-2,4.15,-3.5);north.rotation.x=-roofAngle;
  const gableGeometry=new THREE.BufferGeometry();
  gableGeometry.setAttribute('position',new THREE.Float32BufferAttribute([-3,0,0,3,0,0,0,1.6,0],3));gableGeometry.computeVertexNormals();
  const gableMaterial=new THREE.MeshStandardMaterial({color:'#e8e6dd',roughness:.9,side:THREE.DoubleSide});
  for(const x of [-6.01,2.01]){const triangle=new THREE.Mesh(gableGeometry,gableMaterial);triangle.rotation.y=Math.PI/2;triangle.position.set(x,3.25,-2);scene.add(triangle);}
  // Juntas del tejado, canalones y bajantes.
  for(let x=-6.2;x<2.4;x+=.45){const rib=box(.016,.035,3.5,standard('#7b7d78'),x,4.24,-.5);rib.rotation.x=roofAngle;}
  box(8.8,.12,.12,darkMetal,-2,3.28,1.1);
  cylinder(.05,.05,3.15,darkMetal,-6.05,1.6,1.08);
  // Ventanales, puerta y porche.
  for(const x of [-4.7,-2.8]){
    box(1.5,1.65,.12,darkMetal,x,1.8,1.03);box(1.35,1.48,.035,windowLight,x,1.8,1.105);box(.035,1.5,.04,silver,x,1.8,1.13);
  }
  box(.95,2.25,.11,wood,-.95,1.18,1.08);box(.07,.34,.05,silver,-.64,1.35,1.16);
  box(4,.14,1.7,concrete,-2.6,.04,1.95);
  for(let i=0;i<4;i++)box(1.2,.06,.65,concrete,-2.8,.03,3.1+i*.92);
  for(const z of [-3.3,-.6]){box(.08,1.7,1.55,darkMetal,2.035,1.8,z);box(.03,1.55,1.39,windowLight,2.085,1.8,z);}
  // Ocho módulos fotovoltaicos con marcos y células individuales instanciadas.
  const cellMat=standard('#102d48',.25,.5);
  const cellGeo=new THREE.BoxGeometry(.235,.012,.16);
  for(let col=0;col<4;col++)for(let row=0;row<2;row++){
    const z=-1.35+row*1.45,x=-4.85+col*1.9,y=3.4+(1-z)*(1.6/3)+.11;
    const panel=new THREE.Group();panel.position.set(x,y,z);panel.rotation.x=roofAngle;scene.add(panel);
    box(1.75,.065,1.28,silver,0,0,0,panel);box(1.68,.025,1.21,darkMetal,0,.04,0,panel);
    const cells=new THREE.InstancedMesh(cellGeo,cellMat,36);const matrix=new THREE.Matrix4();let k=0;
    for(let a=0;a<6;a++)for(let b=0;b<6;b++){matrix.makeTranslation(-.665+a*.265,.06,-.49+b*.19);cells.setMatrixAt(k++,matrix);}panel.add(cells);
  }
  // Inversor híbrido y batería mural: representaciones genéricas, no equipos comerciales.
  const inverter=box(.62,.86,.25,standard('#ebecea'),.1,2.05,1.22);
  box(.5,.28,.015,darkMetal,.1,2.22,1.355);box(.25,.065,.02,standard('#8cc69b',.3),.1,2.2,1.37);
  for(let i=0;i<5;i++)box(.42,.018,.02,standard('#969d9d'),.1,1.85+i*.045,1.36);
  box(.82,1.55,.32,standard('#edf0ee'),1.3,1.08,1.29);box(.65,.035,.02,standard('#459654'),1.3,1.55,1.46);
  const badge=box(.62,.24,.01,labelTexture('BATERÍA'),1.3,1.23,1.46);
  cable([[.1,1.65,1.24],[.1,.65,1.24],[1.3,.65,1.24]],darkMetal,.025);
  cable([[.1,2.5,1.22],[.1,3.35,1.2],[-1,4.2,-.25]],darkMetal,.025);
  // Vehículo eléctrico: carrocería, habitáculo, cristales, ruedas y puerto de carga.
  const car=new THREE.Group();car.position.set(6.3,.03,3.15);scene.add(car);
  function roundedBox(w,h,d,r,mat,x,y,z,parent){
    const sh=new THREE.Shape();const a=-w/2,b=-h/2;
    sh.moveTo(a+r,b);sh.lineTo(a+w-r,b);sh.quadraticCurveTo(a+w,b,a+w,b+r);sh.lineTo(a+w,b+h-r);sh.quadraticCurveTo(a+w,b+h,a+w-r,b+h);sh.lineTo(a+r,b+h);sh.quadraticCurveTo(a,b+h,a,b+h-r);sh.lineTo(a,b+r);sh.quadraticCurveTo(a,b,a+r,b);
    const geo=new THREE.ExtrudeGeometry(sh,{depth:d,bevelEnabled:true,bevelSegments:3,steps:1,bevelSize:.08,bevelThickness:.08,curveSegments:8});geo.translate(0,0,-d/2);
    const m=new THREE.Mesh(geo,mat);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;
  }
  const paint=new THREE.MeshPhysicalMaterial({color:'#ccdbdf',metalness:.65,roughness:.24,clearcoat:1,clearcoatRoughness:.15});
  roundedBox(2.04,.55,4.15,.2,paint,0,.73,0,car);
  roundedBox(1.6,.67,2.2,.22,glass,0,1.29,-.12,car);
  roundedBox(1.56,.08,1.5,.1,paint,0,1.66,-.28,car);
  box(1.3,.09,.04,darkMetal,0,.8,2.17,car);
  for(const x of [-.74,.74]){box(.48,.1,.06,standard('#e9f2ee',.25),x,.89,2.19,car);box(.45,.08,.05,standard('#ab2525',.35),x,.86,-2.18,car);}
  for(const x of [-1.03,1.03])for(const z of [-1.32,1.32]){
    const wheel=cylinder(.39,.39,.22,standard('#202323',.9),x,.46,z,car);wheel.rotation.z=Math.PI/2;
    const hub=cylinder(.24,.24,.24,silver,x,.46,z,car);hub.rotation.z=Math.PI/2;
    for(let i=0;i<5;i++){const spoke=box(.25,.045,.38,darkMetal,x,.46,z,car);spoke.rotation.x=i*Math.PI/5;}
  }
  for(const x of [-1.1,1.1]){box(.18,.11,.28,paint,x,1.19,.55,car);box(.02,.08,.2,glass,x*1.04,1.2,.55,car);}
  // Cargador y cable físico hasta el coche.
  box(.22,1.1,.22,darkMetal,4.45,.55,4.25);roundedBox(.48,.65,.22,.08,standard('#f1f3f1'),4.45,1.4,4.25,scene);
  box(.27,.23,.02,darkMetal,4.45,1.47,4.38);
  cable([[4.64,1.26,4.35],[4.95,.32,4.5],[5.23,.24,4.25],[5.26,.91,3.9]],standard('#161c20'),.035);
  // Vegetación y cerramiento de parcela.
  const leaf=standard('#5d7750',.95);
  function tree(x,z,height){
    cylinder(.11,.17,height*.62,wood,x,height*.3,z);
    const crown=new THREE.Mesh(new THREE.IcosahedronGeometry(height*.43,2),leaf);crown.scale.set(.8,1.15,.8);crown.position.set(x,height*.82,z);crown.castShadow=true;scene.add(crown);
  }
  tree(-8,-5.5,4);tree(-8.5,2,3.3);tree(8,-5.5,3.5);
  for(let x=-10;x<11;x+=1.2)box(1.1,.38,.7,leaf,x,.25,-7.7);
  for(let z=-7;z<6;z+=1.2)box(.7,.38,1.1,leaf,-10.8,.25,z);
  // Acometida simplificada y punto de conexión a red.
  cylinder(.09,.12,3.7,wood,-8.1,1.85,6.5);box(.7,.08,.1,darkMetal,-8.1,3.65,6.5);
  box(.36,.48,.16,white,-8.1,1.5,6.65);
  const flowColors={solar:0xe0a02b,home:0x2d9a64,battery:0x2d9a64,car:0x2d9a64,grid:0x367fbd};
  const flowDefinitions={
    solar:[[-1,4.35,-.25],[.15,3.65,1.48],[.15,2.52,1.48]],
    home:[[-.2,2.1,1.53],[-1.3,2.1,1.53],[-2.6,1.8,1.53]],
    battery:[[.4,1.9,1.56],[1.1,1.9,1.56],[1.3,1.7,1.56]],
    car:[[.1,1.6,1.6],[2.8,.2,2.4],[4.45,.2,4.25],[4.45,1.32,4.44]],
    grid:[[.1,1.6,1.6],[-.1,.18,3.8],[-5,.18,5.7],[-8.1,.18,6.5],[-8.1,1.1,6.7]]
  };
  const flows={};
  for(const [key,points] of Object.entries(flowDefinitions)){
    const group=new THREE.Group();scene.add(group);const mat=new THREE.MeshBasicMaterial({color:flowColors[key],transparent:true,opacity:.8,depthTest:false});
    const curve=cable(points,mat,.022,group);const dots=[];
    for(let i=0;i<5;i++){const dot=new THREE.Mesh(new THREE.SphereGeometry(.065,8,8),new THREE.MeshBasicMaterial({color:flowColors[key],depthTest:false}));dot.renderOrder=6;group.add(dot);dots.push(dot);}
    group.renderOrder=5;flows[key]={group,curve,dots};
  }
  const interior=new THREE.PointLight('#ffd193',0,8,2);interior.position.set(-2,2,2);scene.add(interior);
  syncScene=()=>{
    const night=state.night;
    scene.background.set(night?'#182a3d':'#e6edf2');scene.fog.color.copy(scene.background);
    hemi.intensity=night?.42:2.5;sun.intensity=night?.35:4;fill.intensity=night?.22:.7;
    renderer.toneMappingExposure=night?1.05:1.25;
    windowLight.emissiveIntensity=state.houseOn&&night?1.7:0;
    interior.intensity=state.houseOn&&night?8:0;
    for(const [key,flow] of Object.entries(flows))flow.group.visible=flowToggle.checked&&state.active.includes(key);
  };
  syncScene();
  function resize(){const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}
  const observer=new ResizeObserver(resize);observer.observe(stage);resize();
  fallback.hidden=true;loading.hidden=true;
  let visible=true;new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;},{rootMargin:'150px'}).observe(stage);
  let phase=0,last=0;
  renderer.setAnimationLoop(time=>{
    if(document.hidden||!visible){last=time;return;}
    const delta=last?Math.min((time-last)/1000,.05):0;last=time;
    if(!paused)phase+=delta*.32;
    for(const [key,flow] of Object.entries(flows)){
      if(!flow.group.visible)continue;
      flow.dots.forEach((dot,i)=>{let t=(phase+i/flow.dots.length)%1;if(state.reverse.includes(key))t=1-t;dot.position.copy(flow.curve.getPointAt(t));});
    }
    controls.update();renderer.render(scene,camera);
  });
  renderer.domElement.addEventListener('webglcontextlost',event=>{event.preventDefault();loading.hidden=false;loading.textContent='Se ha pausado la vista 3D. Recarga la página para volver a abrirla.';renderer.setAnimationLoop(null);});
}
