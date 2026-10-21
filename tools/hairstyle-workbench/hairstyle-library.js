(function(){
"use strict";
const $=id=>document.getElementById(id);
const HAIR_CATEGORIES=["haircut","bangs","sidelocks","tie","ahoge","accessory"];
let library=null,webReferences=null,activeViewerTab="references";
const css=[
".library-btn{border-color:#8a5572!important;background:#392638!important;font-weight:800}",
".combo-note{font-size:10px;line-height:1.5;color:#9eacc3;margin:7px 0}",
".combo-list{display:flex;flex-direction:column;gap:6px}",
".combo-option{display:grid;grid-template-columns:18px minmax(0,1fr);gap:8px;align-items:start;padding:7px;border:1px solid #354156;border-radius:8px;background:#111721;cursor:pointer}",
".combo-option input{width:15px;margin:2px 0;accent-color:#ee5d9d}",
".combo-option b{display:block;font-size:11px}.combo-option small{display:block;color:#9eacc3;font-size:9px;overflow-wrap:anywhere}",
".library-overlay{display:none;position:fixed;inset:0;z-index:40;background:#070910ed;padding:clamp(8px,2vw,24px);align-items:center;justify-content:center}",
".library-overlay.open{display:flex}.library-panel{width:min(1320px,100%);height:min(94vh,1100px);background:#151a25;border:1px solid #48546a;border-radius:16px;box-shadow:0 25px 80px #000b;display:flex;flex-direction:column;min-height:0;overflow:hidden}",
".library-header{display:flex;gap:12px;align-items:flex-start;padding:16px 18px;border-bottom:1px solid #354156;background:#1b202d}.library-heading{min-width:0;flex:1}.library-heading h2{font-size:18px;margin:0 0 5px}.library-heading p{font-size:11px;color:#9eacc3;max-width:820px;margin:0;line-height:1.55}",
".library-controls{display:grid;grid-template-columns:minmax(180px,2fr) repeat(3,minmax(130px,1fr));gap:8px;padding:12px 16px;border-bottom:1px solid #354156;background:#121722}.library-count{font-size:11px;color:#9eacc3;padding:10px 17px}",
".library-scroll{flex:1;overflow:auto;padding:0 16px 18px;min-height:0}.recipe-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}",
".recipe-card{min-width:0;border:1px solid #394358;border-radius:11px;overflow:hidden;background:#10151f;display:flex;flex-direction:column}.recipe-card canvas{width:100%;height:150px;display:block;background:radial-gradient(ellipse at center,#252c3b,#151a25 72%)}",
".recipe-body{padding:9px;display:flex;flex:1;flex-direction:column;gap:6px}.recipe-body b{font-size:12px;line-height:1.35;min-height:31px}.recipe-body p{font-size:10px;color:#9eacc3;line-height:1.45;margin:0;min-height:43px}",
".recipe-tags{display:flex;gap:4px;flex-wrap:wrap}.recipe-tags span{font-size:9px;border:1px solid #47536a;color:#ccd7eb;border-radius:5px;padding:2px 5px}.recipe-meta{font-size:9px;color:#f3c4dc}.recipe-body button{margin-top:auto;width:100%;font-size:11px}",
".library-empty{padding:35px;text-align:center;color:#9eacc3;font-size:13px}",
".viewer-tabs{display:flex;gap:8px;padding:10px 16px 0;background:#121722}",
".viewer-tabs button{font-size:11px;border-radius:8px 8px 0 0}.viewer-tabs button.active{background:#3a2535;border-color:#ee5d9d;color:#fff}",
".reference-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}",
".reference-card{min-width:0;border:1px solid #394358;border-radius:11px;overflow:hidden;background:#10151f;display:flex;flex-direction:column}",
".reference-image{width:100%;height:205px;object-fit:contain;background:#252b36;display:block}",
".reference-placeholder{height:160px;display:flex;align-items:center;justify-content:center;text-align:center;background:#202838;color:#c8d4e8;padding:18px;font-size:12px}",
".reference-body{padding:10px;display:flex;flex:1;flex-direction:column;gap:7px}.reference-body b{font-size:12px;line-height:1.4}.reference-body p{margin:0;color:#aab6c9;font-size:10px;line-height:1.55}",
".reference-meta{font-size:9px;color:#b5c5dc}.license-flag{font-size:9px;line-height:1.45;border:1px solid #7a6541;background:#302719;color:#ffe4a4;border-radius:6px;padding:5px 6px}.license-flag.open{border-color:#376b56;background:#173128;color:#b3f0d0}",
".reference-actions{display:flex;gap:7px;margin-top:auto}.reference-actions a{flex:1;text-align:center;font-size:10px;text-decoration:none;color:#ffb6d4;border:1px solid #48546a;padding:7px;border-radius:7px}.reference-actions a:hover{background:#302433}",
"@media(max-width:980px){.reference-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}",
"@media(max-width:650px){.reference-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.reference-image{height:140px}.reference-body{padding:7px}.reference-actions{flex-direction:column}}",
"@media(max-width:980px){.recipe-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}",
"@media(max-width:650px){.library-controls{grid-template-columns:1fr 1fr}.library-controls .field:first-child{grid-column:1/-1}.recipe-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.library-header{padding:12px}.recipe-card canvas{height:130px}.recipe-body p{min-height:0}}",
"@media(max-width:390px){.recipe-grid{gap:7px}.recipe-card canvas{height:110px}.recipe-body{padding:7px}}",
".style-fit-pill{display:inline-block;font-size:9px;padding:4px 6px;border:1px solid #7a4968;border-radius:5px;color:#ffb6d4;line-height:1.3}",
".style-fit-pill.compatible{border-color:#4a668e;color:#b8d7ff}",
".overlay-fit-pill{display:inline-block;max-width:100%;font-size:9px;padding:4px 6px;border:1px solid #6f6547;border-radius:5px;color:#ffe3a3;line-height:1.35;overflow-wrap:anywhere}",
".overlay-fit-pill.parts{border-color:#376b56;color:#b3f0d0}",
".overlay-fit-pill.realign{border-color:#4a668e;color:#b8d7ff}",
".overlay-explainer{font-size:10px;line-height:1.45;color:#d2dbea;background:#1b2432;border-bottom:1px solid #354156;padding:9px 16px}",
".overlay-explainer b{color:#fff}"
].join("");
const style=document.createElement("style");style.textContent=css;document.head.appendChild(style);
function installSlot(){
 const grid=$("slots"),select=$("pieceType");
 if(grid&&!grid.querySelector('[data-slot="ahoge"]')){
  const b=document.createElement("button");b.className="slot";b.dataset.slot="ahoge";
  b.innerHTML="<strong>↟ Ahoge</strong><small>Mechón levantado</small>";grid.appendChild(b);
  b.addEventListener("click",()=>{if(window.HairWorkbenchAPI)window.HairWorkbenchAPI.setSlot("ahoge");grid.querySelectorAll("[data-slot]").forEach(x=>x.classList.toggle("active",x.dataset.slot==="ahoge"));});
 }
 if(select&&!select.querySelector('option[value="ahoge"]')){const o=document.createElement("option");o.value="ahoge";o.textContent="Ahoge / mechón levantado";select.appendChild(o);}
}
function installUI(){
 const header=document.querySelector("header");
 const demo=$("demoBtn");
 if(header&&demo&&!$("libraryBtn")){
  const b=document.createElement("button");b.id="libraryBtn";b.className="library-btn";b.textContent="Visor de 120 diseños";header.querySelector(".actions").insertBefore(b,demo);b.addEventListener("click",openLibrary);
 }
 const aside=document.querySelector(".layout > aside");
 if(aside&&!$("combinationTray")){
  const sec=document.createElement("section");sec.className="section";sec.innerHTML="<h2>Combinador manual de piezas</h2><p class='combo-note'>Marcá las piezas de cabello que quieras superponer. Las alternativas de corte completo se excluyen entre sí; flequillos, mechones, coletas parciales, ahoges y adornos sí pueden coexistir. Cambios en vivo.</p><div id='combinationStatus' class='count'>Cargando capas…</div><div id='combinationTray' class='combo-list'></div><button id='libraryBtnSide' class='library-btn' style='width:100%;margin-top:9px'>Buscar receta de peinado</button>";
  const sections=Array.from(aside.querySelectorAll(".section"));
  const anchor=sections.find(s=>(s.querySelector("h2")?.textContent||"").toLowerCase().includes("conservación"));
  aside.insertBefore(sec,anchor||null);
  $("libraryBtnSide").addEventListener("click",openLibrary);
 }
 if(!$("libraryOverlay")){
  const modal=document.createElement("div");modal.id="libraryOverlay";modal.className="library-overlay";modal.setAttribute("role","dialog");modal.setAttribute("aria-modal","true");modal.setAttribute("aria-labelledby","libraryTitle");
  modal.innerHTML="<div class='library-panel'><div class='library-header'><div class='library-heading'><h2 id='libraryTitle'>Biblioteca visual de peinados · anime 2D</h2><p>Busca por corte, flequillo, trenza o recogido. El catálogo separa paquetes con PNG por capas de las hojas que solo sirven como referencia; las referencias de arte no se presentan como assets listos para superponer.</p></div><button id='closeLibraryBtn' aria-label='Cerrar visor'>Cerrar ✕</button></div><div class='viewer-tabs'><button id='referencesTab' class='active' type='button'>Hojas y piezas visuales</button><button id='recipesTab' type='button'>120 recetas conceptuales</button></div><div class='overlay-explainer'><b>Para montar sobre una base plana:</b> un PNG separado solo encaja automáticamente con la plantilla para la que se dibujó. Para otra cabeza, alinea una vez la coronilla, los ojos y las orejas, guarda cada pieza en un lienzo común y conserva sus coordenadas. Una hoja con varias cabezas no equivale a una capa de cabello.</div><div class='library-controls'><div class='field' style='margin:0'><label for='recipeSearch'>Buscar corte, rasgo o etiqueta</label><input id='recipeSearch' type='search' placeholder='Ej. bob, mechón largo, side_ponytail'></div><div class='field' style='margin:0'><label for='recipeFamily'>Estilo visual</label><select id='recipeFamily'><option value='matching'>Anime line art compatible</option><option value='target_style'>Anclas Madhouse / Trigger</option><option value='compatible'>Line art compatible</option><option value='all'>Mostrar también otros estilos</option></select></div><div class='field' style='margin:0' id='overlayModeField'><label for='overlayMode'>Uso como capa</label><select id='overlayMode'><option value='all'>Todo: piezas y referencias</option><option value='layerable'>Paquetes de piezas separadas</option><option value='parts_same_base'>Requiere base compatible</option><option value='parts_realignable'>Alinear manualmente</option><option value='reference_only'>Solo referencia</option></select></div><div class='field' style='margin:0' id='lengthField'><label for='recipeLength'>Largo</label><select id='recipeLength'><option value=''>Todos los largos</option><option value='short'>Corto</option><option value='medium'>Medio</option><option value='long'>Largo</option></select></div></div><div id='libraryCount' class='library-count'>Cargando referencias…</div><div class='library-scroll'><div id='recipeGrid' class='recipe-grid' hidden></div><div id='referenceGrid' class='reference-grid'></div></div></div>";
  document.body.appendChild(modal);
  $("closeLibraryBtn").addEventListener("click",closeLibrary);
  modal.addEventListener("click",e=>{if(e.target===modal)closeLibrary();});
  document.addEventListener("keydown",e=>{if(e.key==="Escape")closeLibrary();});
  $("recipeSearch").addEventListener("input",()=>activeViewerTab==="recipes"?renderLibrary():renderWebReferences());
  $("recipeFamily").addEventListener("change",()=>activeViewerTab==="recipes"?renderLibrary():renderWebReferences());
  $("recipeLength").addEventListener("change",()=>activeViewerTab==="recipes"?renderLibrary():renderWebReferences());
  $("overlayMode").addEventListener("change",()=>activeViewerTab==="recipes"?null:renderWebReferences());
  $("recipesTab").addEventListener("click",()=>switchViewerTab("recipes"));
  $("referencesTab").addEventListener("click",()=>switchViewerTab("references"));
 }
}
function api(){return window.HairWorkbenchAPI;}
function allLayers(){return api()?api().getLayers():[];}
function openLibrary(){
 if(library&&webReferences){switchViewerTab("references");$("libraryOverlay").classList.add("open");$("recipeSearch").focus();return;}
 Promise.all([
  fetch("./hairstyle-library.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw new Error("No se pudo cargar hairstyle-library.json");return r.json();}),
  fetch("./hairstyle-web-references.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw new Error("No se pudo cargar hairstyle-web-references.json");return r.json();})
 ]).then(([recipes,refs])=>{
  library=recipes;webReferences=refs;
  if(!Array.isArray(library.recipes))throw new Error("La biblioteca no contiene recetas válidas");
  if(!Array.isArray(webReferences.items))throw new Error("El catálogo web no contiene referencias válidas");
  renderLibrary();switchViewerTab("references");$("libraryOverlay").classList.add("open");$("recipeSearch").focus();
 }).catch(e=>{if(api())api().say("No se pudo abrir el visor: "+e.message,"error");});
}
function switchViewerTab(tab){
 activeViewerTab=tab;
 const recipes=tab==="recipes";
 $("recipesTab").classList.toggle("active",recipes);$("referencesTab").classList.toggle("active",!recipes);
 $("recipeGrid").hidden=!recipes;$("referenceGrid").hidden=recipes;
 $("recipeLength").parentElement.style.display=recipes?"flex":"none";$("overlayModeField").style.display=recipes?"none":"flex";
 $("libraryTitle").textContent=recipes?"120 recetas conceptuales de peinados":"Referencias de cabello · anime 2D de producción";
 $("recipeFamily").innerHTML=recipes?
  "<option value=''>Todas las familias</option><option value='Corto'>Cortes cortos</option><option value='Medio'>Cortes medios</option><option value='Largo'>Cortes largos</option>":
  "<option value='matching'>Solo mi estilo</option><option value='target_style'>Anclas Madhouse / Trigger</option><option value='compatible'>Line art anime compatible</option><option value='all'>Mostrar también otros estilos</option>";
 $("recipeFamily").value=recipes?"":"matching";$("recipeLength").value="";
 $("recipeSearch").placeholder=recipes?"Ej. bob, mechón largo, side_ponytail":"Ej. Kill la Kill, Perfect Blue, mechón, trenza";
 recipes?renderLibrary():renderWebReferences();
}
function escapeHtml(value){return String(value==null?"":value).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");}
function renderWebReferences(){
 if(!webReferences)return;
 const q=$("recipeSearch").value.trim().toLowerCase(),fam=$("recipeFamily").value||"matching",mode=$("overlayMode").value||"all";
 const relevant=webReferences.items.filter(r=>r.style_fit==="target"||r.style_fit==="compatible");
 const base=fam==="all"?webReferences.items:fam==="target_style"?webReferences.items.filter(r=>r.style_fit==="target"):fam==="compatible"?webReferences.items.filter(r=>r.style_fit==="compatible"):relevant;
 const layerMode=r=>r.overlay_mode||(r.usable_asset?"parts_same_base":"reference_only");
 const modeMatches=r=>mode==="all"||(mode==="layerable"&&["parts_same_base","parts_realignable"].includes(layerMode(r)))||layerMode(r)===mode;
 const rows=base.filter(r=>modeMatches(r)&&(!q||[r.title,r.source_name,r.license_status,r.description,r.notes,r.overlay_label||"",r.overlay_notes||"",r.studio_anchor||"",r.style_fit||""].concat(r.tags||[],r.part_types||[]).join(" ").toLowerCase().includes(q)));
 const countLayerable=base.filter(r=>["parts_same_base","parts_realignable"].includes(layerMode(r))).length;
 $("libraryCount").textContent=rows.length+" de "+base.length+" fichas · "+countLayerable+" ofrecen paquetes/piezas separadas; las demás son hojas de referencia. El encaje en otra base requiere revisar y alinear.";
 const root=$("referenceGrid");
 if(!rows.length){root.innerHTML="<div class='library-empty'>No hay resultados. Probá otra búsqueda o limpiá el filtro de categoría.</div>";return;}
 root.innerHTML=rows.map(r=>{
  const safeTitle=escapeHtml(r.title),safeUrl=escapeHtml(r.source_url),safeDownload=escapeHtml(r.asset_download_url||r.source_url),safeImage=escapeHtml(r.image_url||"");
  const media=r.image_url?"<img class='reference-image' loading='lazy' src='"+safeImage+"' alt='Referencia visual: "+safeTitle+"' onerror=\"this.style.display='none';this.nextElementSibling.hidden=false\"><div class='reference-placeholder' hidden>Vista previa externa no disponible.<br>Usá el enlace a la fuente para ver la imagen.</div>":"<div class='reference-placeholder'>Paquete de recursos<br>Consultá la fuente y descarga disponible.</div>";
  const cls=r.usable_asset?"license-flag open":"license-flag";
  const fit=r.visual_review==="pending"?"Pendiente de revisión visual":r.style_fit==="target"?"Ancla de estilo · "+(r.studio_anchor||"anime 2D"):r.style_fit==="compatible"?"Line art anime compatible":"Fuera del estilo seleccionado";
  const fitClass=r.visual_review==="pending"?"style-fit-pill compatible":r.style_fit==="compatible"?"style-fit-pill compatible":"style-fit-pill";
  const modeKey=r.overlay_mode||(r.usable_asset?"parts_same_base":"reference_only");
  const overlayLabels={parts_same_base:"Piezas separadas · requiere base compatible",parts_realignable:"Piezas editables · alinear sobre otra base",reference_only:"Solo referencia · no es una capa PNG"};
  const overlayText=escapeHtml(r.overlay_label||overlayLabels[modeKey]||overlayLabels.reference_only);
  const overlayClass=modeKey==="parts_same_base"?"overlay-fit-pill parts":modeKey==="parts_realignable"?"overlay-fit-pill realign":"overlay-fit-pill";
  const detail=escapeHtml(r.overlay_notes||"Verifica transparencia, alineación, procedencia y licencia antes de usarlo como pieza.");
  const buttons=r.usable_asset?"<a href='"+safeUrl+"' target='_blank' rel='noopener noreferrer'>Fuente / licencia</a><a href='"+safeDownload+"' target='_blank' rel='noopener noreferrer'>Ver paquete</a>":"<a href='"+safeUrl+"' target='_blank' rel='noopener noreferrer'>Ver fuente</a>";
  return "<article class='reference-card'>"+media+"<div class='reference-body'><b>"+safeTitle+"</b><div class='"+fitClass+"'>"+escapeHtml(fit)+"</div><div class='overlay-fit-pill "+overlayClass+"'>"+overlayText+"</div><div class='"+cls+"'>"+escapeHtml(r.license_status)+"</div><p>"+escapeHtml(r.description)+"</p><div class='reference-meta'>"+escapeHtml(r.source_name)+" · "+escapeHtml((r.tags||[]).slice(0,6).join(", "))+"</div><div class='reference-actions'>"+buttons+"</div><p>"+detail+"</p><p>"+escapeHtml(r.notes)+"</p></div></article>";
 }).join("");
}
function closeLibrary(){const m=$("libraryOverlay");if(m)m.classList.remove("open");}
function labelsLen(n){return n==="short"?"Corto":n==="medium"?"Medio":"Largo";}
function drawThumb(r,canvas){
 const c=canvas.getContext("2d"),w=canvas.width,h=canvas.height;
 const seed=Number((r.id.match(/(\d+)$/)||[])[1]||1);
 c.clearRect(0,0,w,h);
 const palette=[["#4a3970","#bf609c"],["#344c72","#7e9ed9"],["#5a373f","#d17b7d"],["#3f4f4a","#9bbda3"],["#5b4635","#c39b70"],["#373b55","#a1a0d7"]];
 const colors=palette[seed%palette.length],hair=c.createLinearGradient(25,15,105,145);hair.addColorStop(0,colors[0]);hair.addColorStop(1,colors[1]);
 const end=r.length==="short"?91:r.length==="medium"?119:153,shift=(seed%5)-2;
 c.lineCap="round";c.lineJoin="round";
 c.fillStyle=hair;c.beginPath();c.moveTo(31,77);c.bezierCurveTo(25,43,33,20,59,19);c.bezierCurveTo(85,13,103,36,96,72);c.lineTo(99+shift,end-7);c.quadraticCurveTo(94,end+3,82,end-1);c.lineTo(77,81);c.lineTo(51,82);c.lineTo(45,end-2);c.quadraticCurveTo(26,end+2,26,end-8);c.closePath();c.fill();
 if(r.shape==="shag"||r.shape==="wolf"||r.shape==="layers-long"){c.strokeStyle=colors[0];c.lineWidth=3;for(let k=0;k<4;k++){c.beginPath();c.moveTo(35+k*13,70);c.quadraticCurveTo(24+k*16,93+k*3,31+k*14,end-2);c.stroke();}}
 c.fillStyle="#e6ac9a";c.fillRect(55,91,18,19);
 c.fillStyle="#f4cbb7";c.beginPath();c.ellipse(64,63,25,33,0,0,Math.PI*2);c.fill();
 c.fillStyle="#e8b1a2";c.beginPath();c.ellipse(38,66,4,7,0,0,Math.PI*2);c.ellipse(90,66,4,7,0,0,Math.PI*2);c.fill();
 c.fillStyle=hair;c.beginPath();c.moveTo(34,65);c.bezierCurveTo(28,35,40,20,62,22);c.bezierCurveTo(86,17,100,37,94,64);c.quadraticCurveTo(81,49,76,40);c.quadraticCurveTo(58,55,37,48);c.closePath();c.fill();
 c.strokeStyle="#493d56";c.lineWidth=2;c.beginPath();c.moveTo(48,65);c.lineTo(56,65);c.moveTo(72,65);c.lineTo(80,65);c.stroke();
 c.strokeStyle="#ad6b75";c.lineWidth=1.5;c.beginPath();c.moveTo(60,80);c.quadraticCurveTo(64,83,68,80);c.stroke();
 if(r.bangs==="blunt_bangs"){c.fillStyle=hair;c.beginPath();c.moveTo(37,46);c.quadraticCurveTo(64,37,91,47);c.lineTo(86,61);for(let x=81;x>=42;x-=8)c.lineTo(x,59+(x%3));c.closePath();c.fill();}
 else if(r.bangs==="curtain_bangs"){c.fillStyle=hair;c.beginPath();c.moveTo(38,44);c.quadraticCurveTo(52,38,62,47);c.lineTo(58,62);c.quadraticCurveTo(48,54,43,60);c.closePath();c.fill();c.beginPath();c.moveTo(65,47);c.quadraticCurveTo(77,37,90,45);c.lineTo(86,61);c.quadraticCurveTo(76,53,68,62);c.closePath();c.fill();}
 else if(r.bangs==="swept_bangs"){c.fillStyle=hair;c.beginPath();c.moveTo(36,44);c.quadraticCurveTo(62,34,92,42);c.quadraticCurveTo(76,52,49,60);c.closePath();c.fill();}
 else if(r.bangs==="parted_bangs"){c.fillStyle=hair;c.beginPath();c.moveTo(37,44);c.quadraticCurveTo(50,38,61,45);c.lineTo(57,61);c.quadraticCurveTo(48,55,43,60);c.closePath();c.fill();c.beginPath();c.moveTo(67,45);c.quadraticCurveTo(79,38,91,44);c.lineTo(85,60);c.quadraticCurveTo(77,55,69,61);c.closePath();c.fill();}
 if((r.accents||[]).includes("long_sidelocks")){c.strokeStyle=colors[1];c.lineWidth=6;c.beginPath();c.moveTo(39,65);c.quadraticCurveTo(37,90,43,end-1);c.moveTo(89,65);c.quadraticCurveTo(92,90,86,end-2);c.stroke();}
 if(r.arrangement==="side_ponytail"){c.fillStyle=hair;c.beginPath();c.moveTo(87,48);c.quadraticCurveTo(104,45,108,67);c.quadraticCurveTo(112,84,102,95);c.quadraticCurveTo(96,81,98,68);c.closePath();c.fill();c.strokeStyle=colors[1];c.lineWidth=4;c.beginPath();c.moveTo(91,58);c.lineTo(100,59);c.stroke();}
 if(r.arrangement==="half_updo"){c.fillStyle=hair;c.beginPath();c.ellipse(66,25,13,9,-.3,0,Math.PI*2);c.fill();c.strokeStyle=colors[1];c.lineWidth=3;c.beginPath();c.moveTo(60,24);c.lineTo(69,24);c.stroke();}
 if((r.accents||[]).includes("ahoge")){c.strokeStyle=colors[1];c.lineWidth=3;c.beginPath();c.moveTo(62,25);c.bezierCurveTo(54,10,74,5,70,18);c.stroke();}
 if((r.accents||[]).includes("hair_ribbon")){c.fillStyle="#f2a5ca";c.beginPath();c.moveTo(85,52);c.lineTo(96,45);c.lineTo(94,57);c.closePath();c.moveTo(85,52);c.lineTo(76,44);c.lineTo(77,57);c.closePath();c.fill();}
 c.fillStyle="#6d7990";c.beginPath();c.moveTo(45,112);c.quadraticCurveTo(64,105,83,112);c.lineTo(103,150);c.lineTo(25,150);c.closePath();c.fill();
 c.fillStyle="#bfc8d8";c.font="9px system-ui";c.textAlign="center";c.fillText("BOCETO · NO PNG",64,166);
}
function renderLibrary(){
 if(!library)return;
 if(activeViewerTab!=="recipes"){renderWebReferences();return;}
 const q=$("recipeSearch").value.trim().toLowerCase(),fam=$("recipeFamily").value,len=$("recipeLength").value;
 const rows=library.recipes.filter(r=>(!fam||r.family===fam)&&(!len||r.length===len)&&(!q||[r.name,r.description,r.family].concat(r.tags||[],r.accents||[]).join(" ").toLowerCase().includes(q)));
 const a=api(),baseCount=a?a.getCatalogHairCount():0;
 $("libraryCount").textContent=rows.length+" de "+library.recipes.length+" recetas · "+baseCount+" PNG de cabello candidatos registrados · no son 120 recortes reales.";
 const root=$("recipeGrid");
 if(!rows.length){root.innerHTML="<div class='library-empty'>No hay recetas con esos filtros. Probá otro término o quitá un filtro.</div>";return;}
 root.innerHTML=rows.map(r=>"<article class='recipe-card'><canvas width='128' height='170' data-recipe-thumb='"+r.id+"' aria-label='Boceto esquemático de "+r.name.replace(/&/g,"&amp;").replace(/</g,"&lt;")+"'></canvas><div class='recipe-body'><b>"+r.name+"</b><div class='recipe-tags'>"+r.tags.slice(0,4).map(t=>"<span>"+t.replaceAll("_"," ")+"</span>").join("")+"</div><p>"+r.description+"</p><div class='recipe-meta'>"+r.family+" · "+labelsLen(r.length)+" · receta "+r.id+"</div><button data-try-recipe='"+r.id+"' class='primary'>Probar en el lienzo</button></div></article>").join("");
 root.querySelectorAll("[data-recipe-thumb]").forEach(canvas=>{const r=library.recipes.find(x=>x.id===canvas.dataset.recipeThumb);if(r)drawThumb(r,canvas);});
 root.querySelectorAll("[data-try-recipe]").forEach(btn=>btn.addEventListener("click",()=>tryRecipe(btn.dataset.tryRecipe)));
}
function componentScore(layer,comp){
 const tags=(layer.tags||[]).map(t=>String(t).toLowerCase()),wanted=(comp.tags||[]).map(t=>String(t).toLowerCase()),overlap=wanted.filter(t=>tags.includes(t)),lengthTags=["short_hair","medium_hair","long_hair"],specific=wanted.filter(t=>!lengthTags.includes(t)),sp=specific.filter(t=>tags.includes(t));
 return {score:overlap.length,specific:sp.length,exact:specific.length>0&&sp.length>0};
}
function tryRecipe(id){
 const r=library&&library.recipes.find(x=>x.id===id),a=api();if(!r||!a)return;
 const layers=a.getLayers();a.setActiveRecipe(r);
 const previousHaircuts=layers.filter(l=>l.category==="haircut"&&l.visible!==false).map(l=>l.id);
 layers.filter(l=>HAIR_CATEGORIES.includes(l.category)).forEach(l=>l.visible=false);
 const used=new Set(),missing=[],approx=[];let baseMatched=false;
 r.components.forEach(comp=>{
  const cand=layers.filter(l=>l.category===comp.slot&&!used.has(l.id)).map(l=>({layer:l,...componentScore(l,comp)})).filter(x=>x.score>0).sort((x,y)=>y.specific-x.specific||y.score-x.score);
  const hit=cand[0];
  if(!hit){if(["haircut","bangs","sidelocks","tie","ahoge","accessory"].includes(comp.slot))missing.push(comp.description+" ["+comp.tags.join(", ")+"]");return;}
  hit.layer.visible=true;used.add(hit.layer.id);
  if(comp.slot==="haircut"){baseMatched=true;if(!hit.exact)approx.push(hit.layer.name+" (silueta aproximada; no es "+r.name+")");}
 });
 if(!baseMatched){
  layers.filter(l=>l.category==="haircut"&&previousHaircuts.includes(l.id)).forEach(l=>l.visible=true);
  if(previousHaircuts.length)approx.push("se conserva el corte base que ya estaba seleccionado porque no hay una silueta PNG para "+r.name);
 }
 a.setStyleName(r.name);a.render();closeLibrary();
 const note=[];
 if(approx.length)note.push("La base disponible es aproximada: "+approx.join("; ")+".");
 if(missing.length)note.push("Faltan recortes independientes: "+missing.join("; ")+". Importalos como PNG transparente y etiquetá cada pieza.");
 if(!missing.length&&!approx.length){a.say("La receta se compuso con piezas etiquetadas coincidentes. Guardala como variante para conservarla.","ok");a.setStatus("Receta "+r.id+" aplicada con coincidencias etiquetadas.");}
 else {a.say("Receta conceptual "+r.id+" seleccionada. "+note.join(" ")+(used.size?" Se activaron "+used.size+" pieza(s) coincidentes.":" No se encontraron piezas coincidentes; el cabello previo quedó desactivado."),"");a.setStatus("Idea "+r.id+" · "+used.size+" coincidencias · "+missing.length+" componentes pendientes.");}
}
function renderCombiner(){
 const root=$("combinationTray"),status=$("combinationStatus"),a=api();if(!root||!a)return;
 const layers=a.getLayers().filter(l=>HAIR_CATEGORIES.includes(l.category));
 if(!layers.length){status.textContent="Aún no hay piezas de cabello.";root.innerHTML="<p class='combo-note'>Importá PNG separados como corte, flequillo, mechón lateral, coleta/trenza, ahoge o accesorio. Cargá la muestra para ver cinco cortes de prueba.</p>";return;}
 status.textContent=layers.length+" pieza(s) de cabello disponibles · cambios en vivo.";
 root.innerHTML=layers.slice().sort((x,y)=>(x.order||0)-(y.order||0)).map(l=>"<label class='combo-option'><input type='checkbox' data-combo='"+l.id+"' "+(l.visible!==false?"checked":"")+"><span><b>"+l.name+"</b><small>"+(l.category||"capa")+" · "+((l.tags||[]).join(", ")||"sin etiquetas")+(l.status==="pending_visual_review"?" · pendiente de revisión":"")+"</small></span></label>").join("");
 root.querySelectorAll("[data-combo]").forEach(input=>input.addEventListener("change",()=>{
  const l=a.getLayers().find(x=>x.id===input.dataset.combo);if(!l)return;
  if(input.checked&&l.category==="haircut")a.getLayers().filter(x=>x.category==="haircut"&&x.id!==l.id).forEach(x=>x.visible=false);
  l.visible=input.checked;a.render();
 }));
}
function init(){
 installSlot();installUI();
 const a=api();if(a){a.renderHooks.push(renderCombiner);renderCombiner();}
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();
