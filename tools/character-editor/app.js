(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const stage = $("stage");
  const ctx = stage.getContext("2d");
  const assetGrid = $("asset-grid");
  const layerList = $("layer-list");
  const notice = $("notice");
  const cropDialog = $("crop-dialog");
  const cropCanvas = $("crop-canvas");
  const cropCtx = cropCanvas.getContext("2d", { willReadFrequently: true });
  const state = {
    query: "", offset: 0, pageSize: 48, total: 0, assets: [],
    layers: [], selectedLayerId: null, width: 768, height: 1024,
    imageCache: new Map(), crop: null, requestId: 0,
    designTool: "move", drawStroke: null
  };
  const categories = {
    reference: "Referencia completa", hair: "Cabello / peinado", head: "Cabeza / rostro",
    eyes: "Ojos / expresión", body: "Cuerpo / torso", arms: "Brazos / manos",
    legs: "Piernas / pies", clothing: "Ropa", shoes: "Calzado",
    accessory: "Accesorios", other: "Otro"
  };
  function setNotice(message, isError = false) {
    notice.textContent = message;
    notice.style.borderColor = isError ? "#854c4b" : "#435236";
    notice.style.background = isError ? "#2b171a" : "#1b2516";
    notice.style.color = isError ? "#ffd7d7" : "#e2f4c9";
  }
  function assetUrl(path) { return "/api/asset?path=" + encodeURIComponent(path); }
  function imageFor(source) {
    if (state.imageCache.has(source)) return state.imageCache.get(source);
    const image = new Image();
    const promise = new Promise((resolve, reject) => {
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error("No se pudo abrir la imagen."));
      image.src = source;
    });
    state.imageCache.set(source, promise);
    return promise;
  }
  function layerSource(layer) { return layer.dataUrl || assetUrl(layer.path); }
  function isDrawingLayer(layer) { return Boolean(layer && layer.editableDrawing && layer.drawBuffer); }
  function syncDrawingLayer(layer) {
    if (!isDrawingLayer(layer)) return;
    try { layer.dataUrl = layer.drawBuffer.toDataURL("image/png"); }
    catch { setNotice("No se pudo guardar la vista previa de la capa de diseño.", true); }
  }
  function selectedLayer() { return state.layers.find(layer => layer.id === state.selectedLayerId) || null; }

  async function drawStage(showSelection = true) {
    ctx.clearRect(0, 0, stage.width, stage.height);
    for (const layer of state.layers) {
      if (!layer.visible) continue;
      try {
        ctx.save();
        ctx.globalAlpha = Math.max(0, Math.min(1, layer.opacity));
        if ("filter" in ctx && window.ImageProEditing) ctx.filter = window.ImageProEditing.layerAdjustmentsToCanvasFilter(layer.adjustments || {});
        ctx.translate(layer.x, layer.y);
        ctx.rotate(layer.rotation * Math.PI / 180);
        ctx.scale(layer.flipX ? -1 : 1, layer.flipY ? -1 : 1);
        if (isDrawingLayer(layer)) {
          ctx.drawImage(layer.drawBuffer, -layer.width / 2, -layer.height / 2, layer.width, layer.height);
        } else {
          const image = await imageFor(layerSource(layer));
          ctx.drawImage(image, -layer.width / 2, -layer.height / 2, layer.width, layer.height);
        }
        ctx.restore();
      } catch {
        setNotice("No se pudo cargar una capa. Comprueba que la carpeta de imágenes original sigue disponible.", true);
      }
    }
    const selected = selectedLayer();
    if (showSelection && selected && selected.visible) drawSelection(selected);
  }
  function drawSelection(layer) {
    ctx.save();
    ctx.translate(layer.x, layer.y);
    ctx.rotate(layer.rotation * Math.PI / 180);
    ctx.setLineDash([7, 4]);
    ctx.lineWidth = Math.max(1, stage.width / 700);
    ctx.strokeStyle = "#6b9dff";
    ctx.strokeRect(-layer.width / 2, -layer.height / 2, layer.width, layer.height);
    ctx.setLineDash([]);
    ctx.fillStyle = "#6b9dff";
    const size = Math.max(5, stage.width / 100);
    [[-layer.width / 2, -layer.height / 2], [layer.width / 2, -layer.height / 2], [-layer.width / 2, layer.height / 2], [layer.width / 2, layer.height / 2]].forEach(point => ctx.fillRect(point[0] - size / 2, point[1] - size / 2, size, size));
    ctx.restore();
  }
  function updateCanvasSize() {
    stage.width = state.width; stage.height = state.height;
    $("canvas-coordinates").textContent = state.width + " × " + state.height + " px";
    stage.style.aspectRatio = state.width + " / " + state.height;
    drawStage();
  }

  function renderAssets() {
    assetGrid.replaceChildren();
    if (!state.assets.length) {
      const empty = document.createElement("p");
      empty.className = "muted small";
      empty.textContent = state.total ? "No hay coincidencias en esta página." : "No se encontraron imágenes en la carpeta.";
      assetGrid.append(empty); return;
    }
    for (const asset of state.assets) {
      const card = document.createElement("article"); card.className = "asset-card";
      const image = document.createElement("img"); image.loading = "lazy"; image.alt = ""; image.src = assetUrl(asset.path);
      image.onerror = () => { image.alt = "No disponible"; image.removeAttribute("src"); };
      const name = document.createElement("span"); name.className = "asset-name"; name.title = asset.path; name.textContent = asset.name;
      const add = document.createElement("button"); add.className = "button secondary"; add.type = "button"; add.textContent = "Añadir capa";
      add.addEventListener("click", () => addAssetLayer(asset));
      card.append(image, name, add); assetGrid.append(card);
    }
  }
  async function refreshAssets() {
    const requestId = ++state.requestId;
    assetGrid.innerHTML = '<p class="muted small">Buscando imágenes…</p>';
    try {
      const params = new URLSearchParams({ query: state.query, offset: String(state.offset), limit: String(state.pageSize) });
      const response = await fetch("/api/assets?" + params.toString(), { cache: "no-store" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "No se pudo leer la biblioteca.");
      if (requestId !== state.requestId) return;
      state.assets = data.items; state.total = data.total;
      $("library-total").textContent = String(data.total) + (data.truncated ? "+" : "");
      $("root-label").textContent = "Carpeta local: " + data.root_label;
      $("page-label").textContent = data.total ? "Página " + (Math.floor(state.offset / state.pageSize) + 1) + " / " + Math.ceil(data.total / state.pageSize) : "Sin resultados";
      $("previous-page").disabled = state.offset <= 0;
      $("next-page").disabled = state.offset + state.pageSize >= data.total;
      if (data.truncated || data.skipped_large) {
        setNotice("Biblioteca de solo lectura: " + data.total + (data.truncated ? "+" : "") + " imágenes indexadas." + (data.skipped_large ? " Se omitieron " + data.skipped_large + " archivos de más de 100 MB." : "") + " Los originales no se modifican.");
      }
      renderAssets();
    } catch (error) {
      if (requestId !== state.requestId) return;
      assetGrid.replaceChildren(); setNotice(error.message, true);
    }
  }
  function createDrawingLayer(options = {}) {
    const category = options.category || $("design-category").value || "clothing";
    const canvas = document.createElement("canvas");
    canvas.width = state.width; canvas.height = state.height;
    const layer = {
      id: crypto.randomUUID(),
      name: options.name || ("Diseño nuevo — " + (categories[category] || categories.other)),
      path: "", dataUrl: "", category, editableDrawing: true, isGarmentGuide: Boolean(options.isGarmentGuide), drawBuffer: canvas,
      x: state.width / 2, y: state.height / 2, width: state.width, height: state.height,
      rotation: 0, opacity: 1, visible: true, flipX: false, flipY: false
    };
    syncDrawingLayer(layer); state.layers.push(layer); state.selectedLayerId = layer.id;
    renderLayers(); renderInspector(); drawStage();
    return layer;
  }
  function getOrCreateDrawingLayer() {
    const selected = selectedLayer();
    if (isDrawingLayer(selected) && !selected.isGarmentGuide) return selected;
    const guideName = selected && selected.isGarmentGuide ? selected.name : "";
    const layer = createDrawingLayer({
      category: selected && selected.category ? selected.category : "clothing",
      name: guideName ? "Trazos encima — " + guideName.replace(/^Guía gris — /, "") : undefined
    });
    setNotice(guideName
      ? "Creé una capa transparente encima de la guía. Las líneas grises permanecen intactas."
      : "Creé una capa de diseño transparente para no modificar la imagen de referencia.");
    return layer;
  }
  function setDesignTool(tool) {
    const wasGarmentGuideSelected = Boolean(selectedLayer() && selectedLayer().isGarmentGuide);
    state.designTool = tool;
    document.querySelectorAll("[data-tool]").forEach(button => button.classList.toggle("active",button.dataset.tool===tool));
    stage.style.cursor = tool === "move" ? "grab" : tool === "bucket" ? "copy" : "crosshair";
    if (tool !== "move" && (!isDrawingLayer(selectedLayer()) || selectedLayer().isGarmentGuide)) getOrCreateDrawingLayer();
    const labels = { move:"Modo mover.", pen:"Pincel: dibuja en la capa transparente.", eraser:"Borrador: solo elimina pintura de la capa de diseño.", line:"Línea: arrastra para trazarla.", rect:"Rectángulo: arrastra para dibujar.", ellipse:"Elipse: arrastra para dibujar.", bucket:"Relleno: haz clic dentro de una zona cerrada o de color uniforme." };
    setNotice(wasGarmentGuideSelected && tool !== "move"
      ? "Creé una capa transparente encima de la guía gris. Dibuja en ella; el bosquejo original permanece intacto."
      : labels[tool] || "Herramienta seleccionada.");
  }

  const garmentCatalog = {
    "shirt": {name:"Remera clásica",zone:"top",type:"top"},
    "fitted-shirt": {name:"Remera ajustada",zone:"top",type:"top"},
    "oversized-shirt": {name:"Remera oversize",zone:"top",type:"top"},
    "crop-top": {name:"Top corto",zone:"top",type:"top"},
    "tank-top": {name:"Musculosa",zone:"top",type:"top"},
    "blouse": {name:"Blusa",zone:"top",type:"top"},
    "button-shirt": {name:"Camisa con botones",zone:"top",type:"top"},
    "sweater": {name:"Suéter",zone:"top",type:"top"},
    "hoodie": {name:"Buzo con capucha",zone:"top",type:"top"},
    "jacket": {name:"Campera cerrada",zone:"top",type:"top"},
    "open-jacket": {name:"Campera abierta",zone:"top",type:"top"},
    "blazer": {name:"Blazer",zone:"top",type:"top"},
    "long-coat": {name:"Abrigo largo",zone:"top",type:"top"},
    "vest": {name:"Chaleco",zone:"top",type:"top"},
    "corset": {name:"Corsé",zone:"top",type:"top"},
    "bikini-top": {name:"Top de bikini",zone:"top",type:"top"},
    "bodysuit": {name:"Body",zone:"top",type:"top"},
    "school-shirt": {name:"Camisa de uniforme",zone:"top",type:"top"},
    "apron": {name:"Delantal",zone:"top",type:"top"},
    "mini-skirt": {name:"Minifalda",zone:"bottom",type:"skirt"},
    "pleated-skirt": {name:"Falda plisada",zone:"bottom",type:"skirt"},
    "long-skirt": {name:"Falda larga",zone:"bottom",type:"skirt"},
    "shorts": {name:"Shorts",zone:"bottom",type:"pants"},
    "pants": {name:"Pantalón recto",zone:"bottom",type:"pants"},
    "wide-pants": {name:"Pantalón ancho",zone:"bottom",type:"pants"},
    "cargo-pants": {name:"Pantalón cargo",zone:"bottom",type:"pants"},
    "overalls": {name:"Jardinero / overol",zone:"bottom",type:"pants"},
    "short-dress": {name:"Vestido corto",zone:"full",type:"dress"},
    "long-dress": {name:"Vestido largo",zone:"full",type:"dress"},
    "princess-dress": {name:"Vestido princesa",zone:"full",type:"dress"},
    "gothic-dress": {name:"Vestido gótico",zone:"full",type:"dress"},
    "school-dress": {name:"Vestido de uniforme",zone:"full",type:"dress"},
    "kimono": {name:"Kimono",zone:"full",type:"robe"},
    "cape": {name:"Capa / manto",zone:"full",type:"cape"},
    "fantasy-robe": {name:"Túnica fantástica",zone:"full",type:"robe"},
    "armor-top": {name:"Armadura de torso",zone:"top",type:"armor"}
  };
  function createGarmentTemplate(kind, mode = "guide") {
    const item = garmentCatalog[kind] || garmentCatalog.shirt;
    const variant = Math.max(1, Math.min(8, Number($("garment-variant").value) || 1));
    const isGuide = mode === "guide";
    const unit = Math.min(1, state.width / 768, state.height / 1024);
    const layer = createDrawingLayer({
      category: "clothing",
      isGarmentGuide: isGuide,
      name: (isGuide ? "Guía gris — " : "Prenda editable — ") + item.name + " · " + String(variant).padStart(2, "0")
    });
    const canvas = layer.drawBuffer;
    canvas.width = Math.max(1, Math.round(500 * unit));
    canvas.height = Math.max(1, Math.round(600 * unit));
    layer.width = canvas.width;
    layer.height = canvas.height;
    layer.x = state.width / 2;
    layer.y = state.height * (item.zone === "top" ? 0.34 : item.zone === "bottom" ? 0.63 : 0.49);

    const c = canvas.getContext("2d");
    const widthFactors = [1, 0.86, 1.17, 0.98, 1.06, 1.12, 0.92, 1.04];
    const heightFactors = [1, 0.98, 1.05, 0.76, 1.16, 1.02, 0.91, 1.08];
    const widthFactor = widthFactors[variant - 1];
    const heightFactor = heightFactors[variant - 1];
    const cx = 250;
    const color = $("design-color").value || "#d7a9e8";
    c.save();
    c.scale(unit, unit);
    c.translate(cx, 300);
    c.scale(widthFactor, heightFactor);
    c.translate(-cx, -300);
    c.lineJoin = "round";
    c.lineCap = "round";
    c.strokeStyle = isGuide ? "#aeb7c5" : "#363d49";
    c.fillStyle = isGuide ? "rgba(174,183,197,0.055)" : color;
    c.lineWidth = isGuide ? 2.6 : 3;
    c.setLineDash([]);

    function paintShape(drawPath) {
      c.beginPath();
      drawPath();
      c.closePath();
      c.fill();
      c.stroke();
    }
    function seam(drawPath, dashed = false) {
      c.save();
      c.beginPath();
      drawPath();
      c.lineWidth = isGuide ? 1.55 : 1.8;
      c.strokeStyle = isGuide ? "#818b9b" : "#6a536f";
      c.setLineDash(dashed ? [6, 7] : []);
      c.stroke();
      c.restore();
    }
    function detailDot(x, y, radius = 3) {
      c.beginPath();
      c.arc(x, y, radius, 0, Math.PI * 2);
      if (isGuide) { c.strokeStyle = "#818b9b"; c.stroke(); }
      else { c.fillStyle = "#e8d4a1"; c.fill(); }
    }

    if (item.type === "top") {
      const fitted = kind === "fitted-shirt" || kind === "corset" || kind === "bodysuit";
      const oversized = kind === "oversized-shirt" || variant === 3;
      const sleeveless = ["tank-top", "vest", "corset", "bikini-top", "bodysuit"].includes(kind);
      const longSleeves = ["sweater", "hoodie", "jacket", "open-jacket", "blazer", "long-coat", "button-shirt", "school-shirt"].includes(kind);
      const sleeveEnd = longSleeves ? (variant === 6 ? 285 : 255) : (variant === 5 ? 215 : 177);
      const shoulder = oversized ? 112 : 91;
      const torso = oversized ? 106 : fitted ? 67 : 80;
      const hem = kind === "crop-top" || variant === 4 ? 267 :
        kind === "long-coat" ? 485 :
        kind === "apron" ? 450 :
        kind === "bodysuit" ? 425 :
        (kind === "hoodie" || kind === "jacket" || kind === "open-jacket" || kind === "blazer") ? 405 :
        kind === "corset" ? 355 : 365;
      const sleeveOuter = kind === "blouse" ? 218 : 205;
      paintShape(() => {
        c.moveTo(cx - 25, 65);
        c.quadraticCurveTo(cx - 55, 68, cx - shoulder, 92);
        if (sleeveless) {
          c.lineTo(cx - torso - 12, 126);
          c.quadraticCurveTo(cx - torso, 145, cx - torso, 166);
        } else {
          c.lineTo(cx - shoulder - 8, 103);
          c.lineTo(cx - sleeveOuter, sleeveEnd - 18);
          c.lineTo(cx - sleeveOuter + (kind === "blouse" ? 48 : 38), sleeveEnd + 3);
          c.lineTo(cx - shoulder + 10, 137);
          c.lineTo(cx - torso, 154);
        }
        c.lineTo(cx - torso, hem - 18);
        c.quadraticCurveTo(cx, hem + (variant === 8 ? -12 : 5), cx + torso, hem - 18);
        c.lineTo(cx + torso, 154);
        if (sleeveless) {
          c.quadraticCurveTo(cx + torso, 145, cx + torso + 12, 126);
          c.lineTo(cx + shoulder, 92);
        } else {
          c.lineTo(cx + shoulder - 10, 137);
          c.lineTo(cx + sleeveOuter - (kind === "blouse" ? 48 : 38), sleeveEnd + 3);
          c.lineTo(cx + sleeveOuter, sleeveEnd - 18);
          c.lineTo(cx + shoulder + 8, 103);
        }
        c.quadraticCurveTo(cx + 55, 68, cx + 25, 65);
        if (variant === 2 || kind === "corset") {
          c.quadraticCurveTo(cx, 111, cx - 25, 65);
        } else {
          c.quadraticCurveTo(cx, variant === 6 ? 84 : 102, cx + 25, 65);
        }
      });

      if (kind === "tank-top" || kind === "vest" || kind === "corset" || kind === "bodysuit") {
        seam(() => { c.moveTo(cx - 38, 78); c.lineTo(cx - 41, 137); });
        seam(() => { c.moveTo(cx + 38, 78); c.lineTo(cx + 41, 137); });
      }
      if (kind === "hoodie") {
        seam(() => { c.moveTo(cx - 42, 77); c.quadraticCurveTo(cx, 35, cx + 42, 77); c.quadraticCurveTo(cx + 32, 120, cx, 120); c.quadraticCurveTo(cx - 32, 120, cx - 42, 77); });
        seam(() => { c.moveTo(cx - 55, 286); c.lineTo(cx - 35, 332); c.lineTo(cx + 35, 332); c.lineTo(cx + 55, 286); });
      }
      if (kind === "jacket" || kind === "open-jacket" || kind === "blazer" || kind === "long-coat" || kind === "vest" || kind === "armor-top") {
        seam(() => { c.moveTo(cx - 20, 95); c.lineTo(cx - 42, kind === "blazer" ? 190 : hem - 18); });
        seam(() => { c.moveTo(cx + 20, 95); c.lineTo(cx + 42, kind === "blazer" ? 190 : hem - 18); });
        if (kind === "blazer" || kind === "long-coat") {
          seam(() => { c.moveTo(cx - 22, 105); c.lineTo(cx + 5, 165); c.lineTo(cx - 17, 214); });
          seam(() => { c.moveTo(cx + 22, 105); c.lineTo(cx - 5, 165); c.lineTo(cx + 17, 214); });
        }
        if (kind === "open-jacket") seam(() => { c.moveTo(cx, 115); c.lineTo(cx, hem - 12); }, true);
      }
      if (kind === "button-shirt" || kind === "school-shirt" || kind === "jacket" || kind === "open-jacket" || kind === "long-coat") {
        seam(() => { c.moveTo(cx, 106); c.lineTo(cx, hem - 12); });
        for (let y = 165; y < hem - 35; y += 37) detailDot(cx + (kind === "open-jacket" ? 0 : 4), y, 2.5);
      }
      if (kind === "blouse") {
        seam(() => { c.moveTo(cx - 125, 150); c.quadraticCurveTo(cx - 154, 180, cx - 135, 209); });
        seam(() => { c.moveTo(cx + 125, 150); c.quadraticCurveTo(cx + 154, 180, cx + 135, 209); });
      }
      if (kind === "corset") {
        for (let x = cx - 42; x <= cx + 42; x += 28) seam(() => { c.moveTo(x, 145); c.lineTo(x, 338); });
        seam(() => { c.moveTo(cx - 66, 215); c.quadraticCurveTo(cx, 236, cx + 66, 215); });
      }
      if (kind === "bikini-top") {
        seam(() => { c.moveTo(cx - 25, 95); c.lineTo(cx - 49, 63); c.moveTo(cx + 25, 95); c.lineTo(cx + 49, 63); });
        seam(() => { c.moveTo(cx - 66, 155); c.quadraticCurveTo(cx, 171, cx + 66, 155); });
      }
      if (kind === "armor-top") {
        seam(() => { c.moveTo(cx - 100, 115); c.lineTo(cx - 125, 145); c.lineTo(cx - 100, 180); c.moveTo(cx + 100, 115); c.lineTo(cx + 125, 145); c.lineTo(cx + 100, 180); });
        seam(() => { c.moveTo(cx - 57, 180); c.lineTo(cx, 222); c.lineTo(cx + 57, 180); });
        seam(() => { c.moveTo(cx - 35, 250); c.lineTo(cx, 278); c.lineTo(cx + 35, 250); });
      }
      if (kind === "apron") {
        seam(() => { c.moveTo(cx - 48, 145); c.lineTo(cx - 68, 220); c.lineTo(cx - 74, 450); c.lineTo(cx + 74, 450); c.lineTo(cx + 68, 220); c.lineTo(cx + 48, 145); });
        seam(() => { c.moveTo(cx - 74, 280); c.lineTo(cx + 74, 280); });
      }
      if (kind === "tracksuit-top") {
        seam(() => { c.moveTo(cx - 55, 130); c.lineTo(cx - 55, hem - 16); c.moveTo(cx + 55, 130); c.lineTo(cx + 55, hem - 16); });
        seam(() => { c.moveTo(cx - 25, 110); c.lineTo(cx + 25, 110); });
      }
      seam(() => { c.moveTo(cx - torso + 7, hem - 29); c.quadraticCurveTo(cx, hem - 8, cx + torso - 7, hem - 29); });
      if (isGuide) {
        seam(() => { c.moveTo(cx, 132); c.lineTo(cx, hem - 34); }, true);
        seam(() => { c.moveTo(cx - 76, 190); c.lineTo(cx + 76, 190); }, true);
      }
    } else if (item.type === "skirt") {
      const waist = 82, hem = kind === "mini-skirt" ? 270 : kind === "long-skirt" ? 520 : 430;
      const flare = kind === "pleated-skirt" ? 150 : kind === "long-skirt" ? 175 : 125;
      paintShape(() => {
        c.moveTo(cx - 75, waist); c.quadraticCurveTo(cx, waist + 22, cx + 75, waist);
        c.lineTo(cx + flare, hem - 16);
        c.quadraticCurveTo(cx, hem + (variant === 8 ? -8 : 10), cx - flare, hem - 16);
      });
      seam(() => { c.moveTo(cx - 76, waist + 18); c.quadraticCurveTo(cx, waist + 39, cx + 76, waist + 18); });
      if (kind === "pleated-skirt") {
        for (let x = cx - 105; x <= cx + 105; x += 35) seam(() => { c.moveTo(x, waist + 28); c.lineTo(cx + (x - cx) * 1.32, hem - 25); });
      } else if (kind === "long-skirt") {
        seam(() => { c.moveTo(cx - 48, waist + 25); c.lineTo(cx - 68, hem - 25); });
        seam(() => { c.moveTo(cx + 48, waist + 25); c.lineTo(cx + 68, hem - 25); });
      } else {
        seam(() => { c.moveTo(cx - 45, waist + 25); c.lineTo(cx - 65, hem - 25); });
        seam(() => { c.moveTo(cx + 45, waist + 25); c.lineTo(cx + 65, hem - 25); });
      }
      if (isGuide) seam(() => { c.moveTo(cx, waist + 12); c.lineTo(cx, hem - 20); }, true);
      if (kind === "mini-skirt") {
        seam(() => { c.moveTo(cx - flare + 15, hem - 34); c.quadraticCurveTo(cx, hem - 20, cx + flare - 15, hem - 34); });
      }
    } else if (item.type === "pants") {
      const shorts = kind === "shorts";
      const wide = kind === "wide-pants" || kind === "overalls";
      const cargo = kind === "cargo-pants";
      const crotch = shorts ? 255 : 300;
      const hem = shorts ? 300 : 525;
      const leg = wide ? 112 : 76;
      paintShape(() => {
        c.moveTo(cx - 86, 72);
        c.quadraticCurveTo(cx, 95, cx + 86, 72);
        c.lineTo(cx + 112, crotch);
        c.lineTo(cx + leg, hem - 18);
        c.lineTo(cx + 8, hem - 18);
        c.lineTo(cx, crotch + 25);
        c.lineTo(cx - 8, hem - 18);
        c.lineTo(cx - leg, hem - 18);
        c.lineTo(cx - 112, crotch);
      });
      seam(() => { c.moveTo(cx - 86, 94); c.quadraticCurveTo(cx, 115, cx + 86, 94); });
      seam(() => { c.moveTo(cx, 98); c.lineTo(cx, crotch + 24); });
      seam(() => { c.moveTo(cx - 105, crotch); c.lineTo(cx - leg + 7, hem - 31); });
      seam(() => { c.moveTo(cx + 105, crotch); c.lineTo(cx + leg - 7, hem - 31); });
      seam(() => { c.moveTo(cx - leg + 2, hem - 27); c.lineTo(cx - 10, hem - 27); c.moveTo(cx + 10, hem - 27); c.lineTo(cx + leg - 2, hem - 27); });
      if (kind === "overalls") {
        seam(() => { c.moveTo(cx - 54, 90); c.lineTo(cx - 48, 170); c.lineTo(cx + 48, 170); c.lineTo(cx + 54, 90); });
        seam(() => { c.moveTo(cx - 48, 170); c.lineTo(cx - 42, 225); c.lineTo(cx + 42, 225); c.lineTo(cx + 48, 170); });
      }
      if (cargo) {
        seam(() => { c.moveTo(cx - 103, 235); c.lineTo(cx - 48, 235); c.lineTo(cx - 48, 302); c.lineTo(cx - 103, 302); c.closePath(); });
        seam(() => { c.moveTo(cx + 48, 235); c.lineTo(cx + 103, 235); c.lineTo(cx + 103, 302); c.lineTo(cx + 48, 302); c.closePath(); });
      }
      if (isGuide) seam(() => { c.moveTo(cx - 125, 195); c.lineTo(cx + 125, 195); }, true);
    } else if (item.type === "dress") {
      const hem = kind === "short-dress" || kind === "school-dress" ? 420 : kind === "princess-dress" || kind === "gothic-dress" ? 545 : 515;
      const skirtWidth = kind === "princess-dress" || kind === "gothic-dress" ? 205 : kind === "school-dress" ? 145 : 170;
      paintShape(() => {
        c.moveTo(cx - 28, 42);
        c.quadraticCurveTo(cx - 56, 46, cx - 90, 80);
        c.lineTo(cx - 130, 128);
        c.lineTo(cx - 84, 172);
        c.lineTo(cx - 63, 145);
        c.lineTo(cx - 66, 210);
        c.quadraticCurveTo(cx - 90, 245, cx - skirtWidth, hem - 14);
        c.quadraticCurveTo(cx, hem + (variant === 8 ? -12 : 12), cx + skirtWidth, hem - 14);
        c.quadraticCurveTo(cx + 90, 245, cx + 66, 210);
        c.lineTo(cx + 63, 145);
        c.lineTo(cx + 84, 172);
        c.lineTo(cx + 130, 128);
        c.lineTo(cx + 90, 80);
        c.quadraticCurveTo(cx + 56, 46, cx + 28, 42);
        c.quadraticCurveTo(cx, 85, cx - 28, 42);
      });
      seam(() => { c.moveTo(cx - 62, 185); c.lineTo(cx - skirtWidth + 25, hem - 32); });
      seam(() => { c.moveTo(cx + 62, 185); c.lineTo(cx + skirtWidth - 25, hem - 32); });
      seam(() => { c.moveTo(cx - 65, 215); c.quadraticCurveTo(cx, 238, cx + 65, 215); });
      if (kind === "princess-dress") {
        seam(() => { c.moveTo(cx - 50, 245); c.quadraticCurveTo(cx, 275, cx + 50, 245); });
        for (let x = cx - 120; x <= cx + 120; x += 48) seam(() => { c.moveTo(cx + (x - cx) * 0.48, 255); c.lineTo(x, hem - 24); });
      }
      if (kind === "gothic-dress") {
        seam(() => { c.moveTo(cx - 25, 87); c.lineTo(cx, 115); c.lineTo(cx + 25, 87); });
        seam(() => { c.moveTo(cx - 45, 300); c.lineTo(cx - 25, 370); c.lineTo(cx - 5, 300); });
        seam(() => { c.moveTo(cx + 45, 300); c.lineTo(cx + 25, 370); c.lineTo(cx + 5, 300); });
      }
      if (kind === "school-dress") {
        seam(() => { c.moveTo(cx - 60, 125); c.lineTo(cx, 175); c.lineTo(cx + 60, 125); });
        seam(() => { c.moveTo(cx - 45, 248); c.lineTo(cx + 45, 248); });
      }
      if (isGuide) seam(() => { c.moveTo(cx, 125); c.lineTo(cx, hem - 22); }, true);
    } else if (item.type === "robe") {
      const hem = kind === "kimono" ? 540 : 520;
      paintShape(() => {
        c.moveTo(cx - 35, 42);
        c.lineTo(cx - 92, 78);
        c.lineTo(cx - 188, 180);
        c.lineTo(cx - 132, 220);
        c.lineTo(cx - 82, 175);
        c.lineTo(cx - 118, hem - 18);
        c.quadraticCurveTo(cx, hem + 8, cx + 118, hem - 18);
        c.lineTo(cx + 82, 175);
        c.lineTo(cx + 132, 220);
        c.lineTo(cx + 188, 180);
        c.lineTo(cx + 92, 78);
        c.lineTo(cx + 35, 42);
        c.lineTo(cx, 100);
      });
      seam(() => { c.moveTo(cx - 34, 42); c.lineTo(cx + 2, 137); c.lineTo(cx - 8, hem - 15); });
      seam(() => { c.moveTo(cx + 34, 42); c.lineTo(cx - 2, 137); c.lineTo(cx + 8, hem - 15); });
      seam(() => { c.moveTo(cx - 110, 270); c.quadraticCurveTo(cx, 295, cx + 110, 270); });
      if (kind === "kimono") {
        seam(() => { c.moveTo(cx - 72, 245); c.lineTo(cx + 72, 245); });
        seam(() => { c.moveTo(cx - 35, 255); c.lineTo(cx - 48, 305); c.lineTo(cx + 48, 305); c.lineTo(cx + 35, 255); });
      }
      if (isGuide) seam(() => { c.moveTo(cx, 150); c.lineTo(cx, hem - 24); }, true);
    } else if (item.type === "cape") {
      paintShape(() => {
        c.moveTo(cx - 48, 48); c.quadraticCurveTo(cx, 93, cx + 48, 48);
        c.lineTo(cx + 100, 85); c.lineTo(cx + 190, 510);
        c.quadraticCurveTo(cx, 560, cx - 190, 510);
        c.lineTo(cx - 100, 85); c.closePath();
      });
      seam(() => { c.moveTo(cx - 48, 48); c.lineTo(cx - 27, 110); c.lineTo(cx, 140); c.lineTo(cx + 27, 110); c.lineTo(cx + 48, 48); });
      seam(() => { c.moveTo(cx - 95, 170); c.quadraticCurveTo(cx, 205, cx + 95, 170); });
      if (isGuide) seam(() => { c.moveTo(cx, 141); c.lineTo(cx, 530); }, true);
    } else if (item.type === "armor") {
      paintShape(() => {
        c.moveTo(cx - 35, 54); c.lineTo(cx - 100, 70); c.lineTo(cx - 148, 112);
        c.lineTo(cx - 114, 164); c.lineTo(cx - 78, 137); c.lineTo(cx - 70, 340);
        c.quadraticCurveTo(cx, 374, cx + 70, 340); c.lineTo(cx + 78, 137);
        c.lineTo(cx + 114, 164); c.lineTo(cx + 148, 112); c.lineTo(cx + 100, 70); c.lineTo(cx + 35, 54);
        c.lineTo(cx, 98);
      });
      seam(() => { c.moveTo(cx - 95, 92); c.lineTo(cx - 35, 156); c.lineTo(cx, 190); c.lineTo(cx + 35, 156); c.lineTo(cx + 95, 92); });
      seam(() => { c.moveTo(cx - 62, 215); c.lineTo(cx, 251); c.lineTo(cx + 62, 215); });
      seam(() => { c.moveTo(cx - 55, 282); c.lineTo(cx, 315); c.lineTo(cx + 55, 282); });
      if (isGuide) seam(() => { c.moveTo(cx, 190); c.lineTo(cx, 355); }, true);
    }

    if (isGuide) {
      c.save();
      c.strokeStyle = "#808a9a";
      c.lineWidth = 1.2;
      c.setLineDash([5, 7]);
      if (item.zone === "top") {
        c.beginPath(); c.moveTo(cx - 125, 190); c.lineTo(cx + 125, 190); c.stroke();
        c.beginPath(); c.moveTo(cx - 100, 275); c.lineTo(cx + 100, 275); c.stroke();
      }
      c.setLineDash([]);
      c.restore();
    }
    c.restore();
    syncDrawingLayer(layer);
    renderLayers();
    renderInspector();
    drawStage();
    setDesignTool(isGuide ? "move" : "pen");
    setNotice(isGuide
      ? "Guía gris añadida: " + item.name + ", variante " + variant + ". Muévela ahora; al elegir el pincel se creará una capa transparente encima para conservar intacta la guía."
      : "Prenda base con color añadida: " + item.name + ", variante " + variant + ". Puedes dibujar y añadir detalles sobre esta capa.");
    return layer;
  }

  
  // Original garment concepts informed by published runway season archives and fashion-history references.
  // These are original 2D interpretations, not replicas of copyrighted runway illustrations.
  const historicalFashionCatalog = {};
  function fashionLook(name, template, variant, motif, color, accent, note) {
    return { name, template, variant, motif, color, accent, note };
  }
  function addFashionSeason(year, season, looks) {
    const spring = season === "spring";
    const key = year + "-" + season;
    historicalFashionCatalog[key] = {
      key, year, season,
      label: (spring ? "Primavera / Verano " : "Otoño / Invierno ") + year,
      source: "https://www.vogue.com/fashion-shows/" + season + "-" + year + "-ready-to-wear",
      looks
    };
  }
  addFashionSeason(2000,"spring",[
    fashionLook("Top satinado de tirantes finos","tank-top",2,"satin-drape","#b8a0a9","#f3d8e0","Escote suave, tirantes finos y pliegues diagonales de inspiración minimalista."),
    fashionLook("Camiseta corta Y2K","crop-top",4,"y2k","#91a8cf","#f5e5a1","Largo corto, líneas limpias y detalles de costura inspirados en la transición al nuevo milenio."),
    fashionLook("Chaqueta entallada de solapa estrecha","blazer",2,"tailored","#333744","#d4b58b","Hombro definido, solapa fina y bolsillos discretos.")
  ]);
  addFashionSeason(2000,"fall",[
    fashionLook("Blusa de cuello drapeado","blouse",5,"satin-drape","#59505e","#d5c5cf","Cuello fluido, pinzas finas y pliegues que sugieren satén sin copiar una pieza concreta."),
    fashionLook("Jersey fino de cuello alto","sweater",2,"rib-knit","#8b807b","#d8c7ab","Cuerpo ajustado y líneas de tejido verticales, pensado para capas."),
    fashionLook("Abrigo lineal con cierre lateral","long-coat",5,"minimal","#37393d","#b3a08b","Silueta sobria con paneles largos y cierre desplazado.")
  ]);
  addFashionSeason(2001,"spring",[
    fashionLook("Top halter con banda al cuello","bikini-top",2,"halter","#e0a6a5","#fff0dc","Escote halter reinterpretado con contorno gráfico y banda al cuello."),
    fashionLook("Camiseta metálica de paneles","fitted-shirt",2,"metallic","#a5a9b4","#eef0fb","Paneles geométricos y líneas brillantes sugeridas con costuras."),
    fashionLook("Blusa semitransparente en capas","blouse",5,"sheer","#d4b6b0","#f8e7df","Panel ligero con trama de puntos; funciona como guía para capas transparentes.")
  ]);
  addFashionSeason(2001,"fall",[
    fashionLook("Chaqueta de cuero de corte recto","jacket",2,"leather","#795d4b","#e3c9a4","Cierre diagonal y paneles limpios inspirados en sastrería de cuero."),
    fashionLook("Cárdigan corto de punto","sweater",4,"rib-knit","#736c81","#e5d5da","Largo corto, líneas de canalé y botonadura sencilla."),
    fashionLook("Vestido lencero de caída recta","short-dress",5,"slip","#463d50","#c1a9b9","Tirantes finos, escote cowl y caída vertical de inspiración lencera.")
  ]);
  addFashionSeason(2002,"spring",[
    fashionLook("Blusa bohemia fruncida","blouse",5,"boho","#d6b987","#975f45","Escote fruncido, detalles florales pequeños y puños sugeridos."),
    fashionLook("Top corto con lazo frontal","crop-top",4,"tie-front","#d9a6a2","#f2ddcc","Lazo central y bordes redondeados, reinterpretación original del top atado."),
    fashionLook("Chaleco utilitario ligero","vest",3,"utility","#a0a789","#e0c99b","Bolsillos de parche y costuras prácticas con volumen relajado.")
  ]);
  addFashionSeason(2002,"fall",[
    fashionLook("Chaqueta militar femenina","jacket",5,"military","#59614b","#d7bd86","Doble botonadura, hombreras y bolsillos de parche."),
    fashionLook("Jersey de cuello chimenea","sweater",5,"minimal","#8d867f","#d6c9b9","Cuello alto sencillo y paneles verticales limpios."),
    fashionLook("Vestido de costura diagonal","long-dress",5,"asym","#5e4a5d","#cfa9ad","Drapeado asimétrico y costuras diagonales, sin copiar un vestido de pasarela concreto.")
  ]);
  addFashionSeason(2003,"spring",[
    fashionLook("Baby tee gráfico","fitted-shirt",4,"graphic","#a5c1dc","#f3b4cb","Cuerpo corto y un panel gráfico original para personalizar."),
    fashionLook("Bolero corto con borde redondeado","jacket",4,"ruffle","#8a7f9a","#f1d5de","Chaqueta mini con hombro suave y remate curvo."),
    fashionLook("Top denim con canesú","corset",2,"denim","#7497b9","#e4c9a0","Canesú, costuras dobles y bolsillos frontales sencillos.")
  ]);
  addFashionSeason(2003,"fall",[
    fashionLook("Blazer corto de terciopelo","blazer",2,"tailored","#554153","#c5a3b0","Solapa fina, pinzas verticales y botones discretos."),
    fashionLook("Suéter ajustado con cuello vuelto","sweater",5,"rib-knit","#6f7379","#d8d0c7","Tejido acanalado y puños marcados."),
    fashionLook("Falda plisada con cinturilla","pleated-skirt",5,"pleats","#77716b","#c6b78e","Cinturilla ancha y pliegues repetidos para completar un conjunto de época.")
  ]);
  addFashionSeason(2004,"spring",[
    fashionLook("Blusa campesina con manga globo","blouse",5,"boho","#d9c5ae","#bd7f72","Escote amplio, manga con volumen y motivos de bordado."),
    fashionLook("Túnica ligera con caída","fantasy-robe",5,"boho","#8eaaa0","#f0d7b7","Línea alargada, bordado vertical y apertura suave."),
    fashionLook("Camisola de encaje romántico","tank-top",5,"lace","#e7d9d2","#c59ba8","Borde festoneado y tirantes finos para una capa delicada.")
  ]);
  addFashionSeason(2004,"fall",[
    fashionLook("Abrigo corto de inspiración militar","jacket",5,"military","#6b6451","#d4b67f","Solapas estructuradas, hombreras y doble botonadura."),
    fashionLook("Cárdigan largo de punto fino","sweater",5,"rib-knit","#8f8a83","#d4c4b2","Líneas de canalé y cinturilla, pensado para combinar en capas."),
    fashionLook("Blusa de terciopelo con lazada","blouse",5,"bow-collar","#573b4c","#c9a3b4","Lazada en el cuello y silueta ligeramente romántica.")
  ]);
  addFashionSeason(2005,"spring",[
    fashionLook("Camisola con encaje y pinzas","tank-top",2,"lace","#d8bcb4","#f4e6df","Escote festoneado y pinzas verticales discretas."),
    fashionLook("Bolero denim con costura doble","jacket",4,"denim","#668bb0","#edcaa0","Canesú corto, puños y líneas de pespunte."),
    fashionLook("Blusa drapeada de un hombro","blouse",2,"asym","#c7a2a8","#f1dfe1","Escote irregular y pliegues laterales para una caída original.")
  ]);
  addFashionSeason(2005,"fall",[
    fashionLook("Blusa imperio con costuras precisas","blouse",5,"empire","#b1a3a0","#d9c5b5","Costura bajo el busto, pinzas y superficie limpia."),
    fashionLook("Abrigo arquitectónico de paneles","long-coat",5,"minimal","#30333a","#c2a88e","Paneles rectos y cuello alto de inspiración minimalista; referencia histórica general."),
    fashionLook("Suéter de cuello alto satinado","sweater",5,"minimal","#625c61","#cbb5ad","Cuello alto y costuras verticales sobrias.")
  ]);
  addFashionSeason(2006,"spring",[
    fashionLook("Blusa estampada de manga globo","blouse",5,"puff","#e0b0a5","#6c8b7a","Manga voluminosa y panel central para añadir estampado original."),
    fashionLook("Túnica gráfica de panel ancho","fantasy-robe",5,"graphic","#6f8d9a","#e2bb78","Panel frontal amplio para gráfica o estampado propio."),
    fashionLook("Blazer corto de hombro redondeado","blazer",4,"sculptural","#a5a0a5","#d6c4bb","Hombro curvo y solapas reducidas.")
  ]);
  addFashionSeason(2006,"fall",[
    fashionLook("Abrigo cocoon con hombro redondo","long-coat",5,"sculptural","#746d6a","#c9b9a8","Volumen de abrigo ovalado y costuras de panel."),
    fashionLook("Vestido túnica con medias capas","short-dress",5,"layered","#504653","#a9b6b5","Silueta de túnica con líneas de superposición."),
    fashionLook("Jersey de punto con manga larga","sweater",5,"rib-knit","#9c7f76","#e5d2b9","Punto acanalado y puños acentuados.")
  ]);
  addFashionSeason(2007,"spring",[
    fashionLook("Blusa babydoll de cintura elevada","blouse",4,"empire","#e6c6c5","#9e9ab1","Costura alta y vuelo inferior, en una interpretación original."),
    fashionLook("Chaleco sastre entallado","vest",2,"tailored","#4c535e","#c4b29a","Pinzas y solapa pequeña para un conjunto sastre."),
    fashionLook("Blusa drapeada de manga tres cuartos","blouse",5,"satin-drape","#c0b0a2","#e6d3c0","Escote fluido y líneas diagonales de caída.")
  ]);
  addFashionSeason(2007,"fall",[
    fashionLook("Abrigo sastre con cintura marcada","long-coat",5,"tailored","#5b5b60","#b8a088","Solapas definidas, costuras de entalle y bolsillos."),
    fashionLook("Top de cuello vuelto bajo chaqueta","sweater",5,"minimal","#333943","#c8c1b8","Base de punto ceñida pensada para vestir en capas."),
    fashionLook("Chaqueta biker con cierre oblicuo","jacket",5,"leather","#33353b","#b4a09a","Solapas y cierre diagonal de lenguaje rock.")
  ]);
  addFashionSeason(2008,"spring",[
    fashionLook("Top geométrico de bloques de color","fitted-shirt",4,"colorblock","#d6b45d","#6887a7","Paneles angulares pensados para colorear de manera independiente."),
    fashionLook("Blusa asimétrica con pliegues laterales","blouse",5,"asym","#c4a4b5","#ebd9df","Escote desigual y pliegues concentrados hacia un costado."),
    fashionLook("Camiseta deportiva con bandas","fitted-shirt",5,"sporty","#687e96","#e5c46f","Bandas de manga y paneles laterales sencillos.")
  ]);
  addFashionSeason(2008,"fall",[
    fashionLook("Jersey oversize con cuello amplio","oversized-shirt",5,"rib-knit","#8a8589","#c9c0b7","Volumen relajado y líneas de tejido dibujadas como guía."),
    fashionLook("Chaqueta biker con paneles","jacket",5,"leather","#373a3e","#b0a5a0","Cierre oblicuo, paneles y remaches geométricos."),
    fashionLook("Túnica drapeada sobre pantalón","fantasy-robe",5,"layered","#615c6c","#c9acaa","Largo extendido y líneas de capas superpuestas.")
  ]);
  addFashionSeason(2009,"spring",[
    fashionLook("Blusa romántica de encaje","blouse",5,"lace","#dfcfca","#ad8994","Bordes festoneados y líneas pequeñas de encaje."),
    fashionLook("Top drapeado con escote suave","blouse",5,"satin-drape","#c8a2a1","#eedbd6","Escote cowl y pliegues diagonales."),
    fashionLook("Chaqueta utilitaria ligera","jacket",5,"utility","#8a927b","#d5bd91","Bolsillos y costuras prácticas de una chaqueta ligera.")
  ]);
  addFashionSeason(2009,"fall",[
    fashionLook("Camisa de cuadros punk","button-shirt",5,"plaid","#9b5e61","#e0c58b","Rejilla de cuadros original y botonadura frontal."),
    fashionLook("Chaleco militar de capas","vest",5,"military","#6b7156","#d3bb83","Hombreras, bolsillos y botones en doble fila."),
    fashionLook("Chaqueta rock de solapas","jacket",5,"leather","#3f4248","#b7a5a0","Solapas marcadas y cierre oblicuo.")
  ]);
  addFashionSeason(2010,"spring",[
    fashionLook("Blusa de panel semitransparente","blouse",5,"sheer","#d7c0bd","#f6e5dd","Panel con malla de puntos para practicar transparencias."),
    fashionLook("Top lencero con encaje","tank-top",2,"slip","#c7a6ad","#f2e2e0","Tirantes, escote drapeado y borde festoneado."),
    fashionLook("Vestido floral de silueta suave","short-dress",5,"floral","#b5b7a0","#d58d91","Motivos florales pequeños repartidos en el cuerpo.")
  ]);
  addFashionSeason(2010,"fall",[
    fashionLook("Abrigo militar de doble botonadura","long-coat",5,"military","#676650","#cfb681","Doble botonadura, solapas y hombreras."),
    fashionLook("Blusa con lazo al cuello","blouse",5,"bow-collar","#b6a3a0","#e8d6c9","Lazo protagonista y pinzas de sastrería."),
    fashionLook("Chaqueta camel de líneas limpias","jacket",5,"minimal","#b28e6b","#e4cfac","Paneles estructurados y detalles mínimos.")
  ]);
  addFashionSeason(2011,"spring",[
    fashionLook("Top de bloques cromáticos","fitted-shirt",4,"colorblock","#e07e79","#6b93b4","Paneles en contraste para explorar combinaciones de color."),
    fashionLook("Chaqueta deportiva estructurada","jacket",5,"sporty","#6d8194","#d8d9cc","Bandas, cuello funcional y mangas de corte recto."),
    fashionLook("Blusa plisada con cuello pequeño","blouse",5,"pleats","#d8bba2","#8e9e8e","Pliegues frontales y cuello redondeado.")
  ]);
  addFashionSeason(2011,"fall",[
    fashionLook("Blusa joya con detalle central","blouse",5,"baroque","#73506d","#d9ba75","Ornamento original en el delantero, sin copiar estampados de marca."),
    fashionLook("Blusa romántica de lazada","blouse",5,"bow-collar","#7d5e6f","#d7b2bd","Lazo de cuello y puños marcados."),
    fashionLook("Blazer entallado de hombro claro","blazer",5,"tailored","#514d53","#c6a17e","Solapa estructurada, pinzas y bolsillos.")
  ]);
  addFashionSeason(2012,"spring",[
    fashionLook("Blusa péplum con cintura marcada","blouse",4,"peplum","#dcaaa4","#6d8598","Cintura ceñida y pequeño vuelo inferior característico del péplum."),
    fashionLook("Top corto de líneas limpias","crop-top",4,"minimal","#e8d7cf","#b2a0bd","Silueta recortada con pinzas sencillas."),
    fashionLook("Chaqueta geométrica de paneles","jacket",5,"geometric","#7c8b9c","#e1ba61","Paneles angulares y cuello definido.")
  ]);
  addFashionSeason(2012,"fall",[
    fashionLook("Blazer brocado ornamental","blazer",5,"baroque","#44394a","#d4b66d","Paneles ornamentales dibujados como guía para un patrón propio."),
    fashionLook("Blusa oscura con cuello romántico","blouse",5,"lace","#55404e","#c9a3ad","Cuello detallado y puños estrechos."),
    fashionLook("Abrigo entallado con línea princesa","long-coat",5,"tailored","#5b555e","#b6a08a","Entalle vertical y paneles de sastrería.")
  ]);
  addFashionSeason(2013,"spring",[
    fashionLook("Blusa monocromática de corte limpio","blouse",5,"minimal","#eeeeeb","#555965","Paneles sencillos y contraste en blanco y negro."),
    fashionLook("Top con recortes geométricos","fitted-shirt",4,"geometric","#555b68","#e1e0d7","Líneas gráficas y paneles asimétricos."),
    fashionLook("Falda plisada con cintura alta","pleated-skirt",5,"pleats","#b2b7b4","#565a63","Cintura alta y pliegues estructurados.")
  ]);
  addFashionSeason(2013,"fall",[
    fashionLook("Camisa de cuadros grunge","button-shirt",5,"plaid","#7d5359","#d0b58b","Cuadros originales y botonadura delantera."),
    fashionLook("Chaqueta punk con solapas","jacket",5,"leather","#35353b","#aa9c98","Cierre oblicuo y remaches sugeridos."),
    fashionLook("Abrigo oversize de hombro caído","long-coat",5,"sculptural","#77777a","#c2b5aa","Hombro caído y volumen amplio.")
  ]);
  addFashionSeason(2014,"spring",[
    fashionLook("Top de paneles ligeros y recortes","blouse",5,"sheer","#ded9d5","#7d9a9b","Panel central semitransparente y costuras visibles."),
    fashionLook("Chaqueta sporty de bandas","jacket",5,"sporty","#b9b9b0","#e07f7c","Franjas de manga y líneas laterales."),
    fashionLook("Camisa corta de corte cuadrado","button-shirt",4,"minimal","#9fb3c1","#f0e3cf","Cuerpo corto, cuello claro y botonadura geométrica.")
  ]);
  addFashionSeason(2014,"fall",[
    fashionLook("Abrigo recto con cuello protagonista","long-coat",5,"sculptural","#9b9690","#d8c7b2","Cuello amplio y paneles rectangulares."),
    fashionLook("Blusa de cuero con costuras limpias","blouse",5,"leather","#5a4e50","#bc9e92","Paneles curvos y cierre parcial."),
    fashionLook("Vestido mod de línea A","short-dress",5,"mod","#b8b2a7","#5d6475","Corte A y cuello redondeado inspirados en formas sesenteras.")
  ]);
  addFashionSeason(2015,"spring",[
    fashionLook("Blusa setentera de cuello lazo","blouse",5,"retro70","#d7b88b","#8d6e5d","Cuello alargado con lazada y líneas verticales."),
    fashionLook("Chaqueta suede con paneles","jacket",5,"retro70","#9c7556","#e0c6a5","Paneles curvos y bolsillos inspirados en prendas setenteras."),
    fashionLook("Blusa de manga acampanada","blouse",5,"flare-sleeve","#d2a39e","#ece0d4","Mangas acampanadas y costuras curvas.")
  ]);
  addFashionSeason(2015,"fall",[
    fashionLook("Suéter de cuello alto estilizado","sweater",5,"rib-knit","#6a6566","#c5b8a5","Punto acanalado y proporción vertical."),
    fashionLook("Blusa con lazada y puño acampanado","blouse",5,"retro70","#b0a0ad","#e3c9ba","Lazada al cuello y puños amplios."),
    fashionLook("Abrigo A-line de inspiración retro","long-coat",5,"mod","#777a7f","#c2a77e","Hombro definido, cuello simple y forma A.")
  ]);

  function updateHistoricalFashionLooks() {
    const seasonKey = $("fashion-season").value;
    const season = historicalFashionCatalog[seasonKey];
    const select = $("fashion-look");
    select.replaceChildren();
    if (!season) return;
    season.looks.forEach((look, index) => {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = (index + 1) + ". " + look.name;
      select.append(option);
    });
    updateHistoricalFashionInfo();
  }
  function updateHistoricalFashionInfo() {
    const season = historicalFashionCatalog[$("fashion-season").value];
    if (!season) return;
    const look = season.looks[Number($("fashion-look").value) || 0];
    if (!look) return;
    $("fashion-look-title").textContent = look.name;
    $("fashion-look-note").textContent = look.note;
    $("fashion-source").href = season.source;
    $("fashion-source").textContent = "Consultar archivo de pasarela de " + season.label;
  }

  function drawHistoricalMotif(layer, look, isGuide) {
    if (!isDrawingLayer(layer)) return;
    const c = layer.drawBuffer.getContext("2d");
    const unit = Math.min(1, state.width / 768, state.height / 1024);
    const variant = Math.max(1, Math.min(8, Number(look.variant) || 1));
    const wf = [1,.86,1.17,.98,1.06,1.12,.92,1.04][variant-1];
    const hf = [1,.98,1.05,.76,1.16,1.02,.91,1.08][variant-1];
    const accent = isGuide ? "#8792a3" : look.accent;
    c.save();
    c.scale(unit,unit);
    c.translate(250,300); c.scale(wf,hf); c.translate(-250,-300);
    c.lineJoin="round"; c.lineCap="round"; c.strokeStyle=accent; c.fillStyle=accent;
    c.lineWidth=isGuide?2.1:3.2;
    c.setLineDash([]);
    const line=(points,width)=>{c.save();if(width)c.lineWidth=width;c.beginPath();points(c);c.stroke();c.restore();};
    const dot=(x,y,r=3)=>{c.beginPath();c.arc(x,y,r,0,Math.PI*2);if(isGuide)c.stroke();else c.fill();};
    const rect=(x,y,w,h,fill=false)=>{if(fill)c.fillRect(x,y,w,h);else c.strokeRect(x,y,w,h);};
    const flower=(x,y,r=6)=>{for(let n=0;n<5;n++){const a=n*Math.PI*2/5;c.beginPath();c.arc(x+Math.cos(a)*r*.9,y+Math.sin(a)*r*.9,r*.45,0,Math.PI*2);if(isGuide)c.stroke();else c.fill();}dot(x,y,r*.28);};
    switch(look.motif){
      case "satin-drape":
        line(p=>{p.moveTo(190,112);p.quadraticCurveTo(250,155,308,118);p.moveTo(200,130);p.quadraticCurveTo(250,174,297,136);p.moveTo(211,148);p.quadraticCurveTo(250,183,286,153);});
        break;
      case "y2k":
        line(p=>{p.moveTo(207,155);p.lineTo(220,170);p.lineTo(220,270);p.moveTo(293,155);p.lineTo(280,170);p.lineTo(280,270);});
        for(let x=225;x<=275;x+=25)dot(x,250,2.5);
        break;
      case "halter":
        line(p=>{p.moveTo(230,110);p.lineTo(238,68);p.moveTo(270,110);p.lineTo(262,68);p.moveTo(238,68);p.quadraticCurveTo(250,58,262,68);p.moveTo(225,128);p.quadraticCurveTo(250,145,275,128);});
        break;
      case "sheer":
        c.save();c.globalAlpha=isGuide?1:.22;c.beginPath();c.moveTo(220,130);c.lineTo(280,130);c.lineTo(285,220);c.lineTo(215,220);c.closePath();if(!isGuide)c.fill();c.stroke();c.restore();
        for(let x=222;x<280;x+=12)for(let y=140;y<215;y+=12)dot(x,y,1.7);
        break;
      case "slip":
        line(p=>{p.moveTo(214,107);p.lineTo(219,67);p.moveTo(286,107);p.lineTo(281,67);p.moveTo(210,112);p.quadraticCurveTo(250,147,290,112);p.moveTo(220,150);p.quadraticCurveTo(248,174,280,151);});
        break;
      case "boho":
        line(p=>{p.moveTo(212,118);p.quadraticCurveTo(250,136,288,118);p.moveTo(214,127);p.quadraticCurveTo(250,145,286,127);});
        for(let y=155;y<220;y+=22){flower(230,y,4);flower(270,y,4);}
        for(let x=155;x<=345;x+=25){dot(x,250,2);dot(x,258,1.5);}
        break;
      case "military":
        line(p=>{p.moveTo(180,100);p.lineTo(220,108);p.lineTo(215,123);p.lineTo(180,115);p.closePath();p.moveTo(320,100);p.lineTo(280,108);p.lineTo(285,123);p.lineTo(320,115);p.closePath();p.moveTo(220,100);p.lineTo(235,145);p.moveTo(280,100);p.lineTo(265,145);});
        for(let y=155;y<278;y+=29){dot(238,y,3);dot(262,y,3);}
        rect(200,190,28,30);rect(272,190,28,30);
        line(p=>{p.moveTo(197,198);p.lineTo(228,198);p.moveTo(269,198);p.lineTo(300,198);});
        break;
      case "tailored":
        line(p=>{p.moveTo(218,90);p.lineTo(242,132);p.lineTo(230,158);p.moveTo(282,90);p.lineTo(258,132);p.lineTo(270,158);p.moveTo(226,160);p.lineTo(222,240);p.moveTo(274,160);p.lineTo(278,240);});
        rect(194,205,28,24);rect(278,205,28,24);
        break;
      case "ruffle":
      case "lace":
        line(p=>{p.moveTo(205,112);for(let x=205;x<=295;x+=10)p.quadraticCurveTo(x+5,105,x+10,112);});
        for(let x=210;x<=290;x+=12)dot(x,119,2);
        line(p=>{p.moveTo(205,272);for(let x=205;x<=295;x+=10)p.quadraticCurveTo(x+5,265,x+10,272);});
        if(look.motif==="ruffle")line(p=>{p.moveTo(160,135);p.quadraticCurveTo(180,155,160,175);p.moveTo(340,135);p.quadraticCurveTo(320,155,340,175);});
        break;
      case "tie-front":
        line(p=>{p.moveTo(250,125);p.lineTo(230,150);p.lineTo(250,175);p.lineTo(270,150);p.closePath();p.moveTo(230,150);p.lineTo(210,137);p.lineTo(207,168);p.lineTo(230,150);p.moveTo(270,150);p.lineTo(290,137);p.lineTo(293,168);p.lineTo(270,150);});
        break;
      case "graphic":
      case "geometric":
        c.save();if(!isGuide){c.globalAlpha=.28;c.beginPath();c.moveTo(205,135);c.lineTo(250,135);c.lineTo(218,210);c.lineTo(205,210);c.closePath();c.fill();c.beginPath();c.moveTo(250,135);c.lineTo(295,135);c.lineTo(295,210);c.lineTo(282,210);c.closePath();c.fill();}c.restore();
        line(p=>{p.moveTo(205,135);p.lineTo(250,210);p.lineTo(295,135);p.moveTo(215,218);p.lineTo(285,218);p.moveTo(250,135);p.lineTo(250,218);});
        break;
      case "denim":
        line(p=>{p.moveTo(190,120);p.quadraticCurveTo(250,153,310,120);p.moveTo(205,128);p.lineTo(215,150);p.lineTo(285,150);p.lineTo(295,128);p.moveTo(212,165);p.lineTo(235,165);p.lineTo(235,195);p.lineTo(212,195);p.closePath();p.moveTo(265,165);p.lineTo(288,165);p.lineTo(288,195);p.lineTo(265,195);p.closePath();});
        for(let y=165;y<235;y+=28)dot(250,y,2.4);
        break;
      case "utility":
        rect(198,170,36,42);rect(266,170,36,42);
        line(p=>{p.moveTo(198,180);p.lineTo(234,180);p.moveTo(266,180);p.lineTo(302,180);p.moveTo(207,147);p.lineTo(207,255);p.moveTo(293,147);p.lineTo(293,255);});
        break;
      case "leather":
        line(p=>{p.moveTo(210,92);p.lineTo(240,130);p.lineTo(220,150);p.moveTo(290,92);p.lineTo(260,130);p.lineTo(280,150);p.moveTo(220,151);p.lineTo(280,265);});
        for(let x=220;x<250;x+=12)dot(x,180,2.5);
        break;
      case "colorblock":
        c.save();if(!isGuide){c.globalAlpha=.32;c.beginPath();c.moveTo(250,135);c.lineTo(295,135);c.lineTo(295,245);c.lineTo(250,220);c.closePath();c.fill();c.beginPath();c.moveTo(205,135);c.lineTo(250,135);c.lineTo(250,220);c.lineTo(205,245);c.closePath();c.fill();}c.restore();
        line(p=>{p.moveTo(250,135);p.lineTo(250,240);p.moveTo(205,190);p.lineTo(295,190);});
        break;
      case "sporty":
        for(let offset=0;offset<3;offset++)line(p=>{p.moveTo(135,132+offset*9);p.lineTo(177,148+offset*9);p.moveTo(323,148+offset*9);p.lineTo(365,132+offset*9);});
        line(p=>{p.moveTo(206,180);p.lineTo(206,250);p.moveTo(294,180);p.lineTo(294,250);});
        break;
      case "asym":
        line(p=>{p.moveTo(198,100);p.lineTo(296,112);p.lineTo(280,139);p.moveTo(280,139);p.quadraticCurveTo(255,160,220,145);p.moveTo(217,146);p.quadraticCurveTo(228,158,238,168);p.moveTo(226,153);p.quadraticCurveTo(240,166,252,175);});
        break;
      case "peplum":
        line(p=>{p.moveTo(204,208);p.quadraticCurveTo(250,226,296,208);p.moveTo(204,212);p.quadraticCurveTo(180,232,175,254);p.quadraticCurveTo(250,279,325,254);p.quadraticCurveTo(320,232,296,212);});
        break;
      case "pleats":
        line(p=>{p.moveTo(214,136);p.lineTo(214,255);p.moveTo(230,136);p.lineTo(230,255);p.moveTo(246,136);p.lineTo(246,255);p.moveTo(262,136);p.lineTo(262,255);p.moveTo(278,136);p.lineTo(278,255);p.moveTo(294,136);p.lineTo(294,255);});
        break;
      case "plaid":
        c.save();c.beginPath();c.rect(200,145,100,105);c.clip();
        for(let x=205;x<=300;x+=19)line(p=>{p.moveTo(x,140);p.lineTo(x,255);},isGuide?1.3:2.1);
        for(let y=150;y<=255;y+=18)line(p=>{p.moveTo(195,y);p.lineTo(305,y);},isGuide?1.3:2.1);
        c.restore();
        break;
      case "empire":
        line(p=>{p.moveTo(205,183);p.quadraticCurveTo(250,202,295,183);p.moveTo(214,130);p.lineTo(225,182);p.moveTo(286,130);p.lineTo(275,182);});
        for(let x=220;x<=280;x+=20)line(p=>{p.moveTo(x,205);p.quadraticCurveTo(x-5,226,x,244);});
        break;
      case "puff":
        line(p=>{p.moveTo(170,120);p.quadraticCurveTo(150,135,165,160);p.moveTo(178,125);p.quadraticCurveTo(163,143,176,162);p.moveTo(330,120);p.quadraticCurveTo(350,135,335,160);p.moveTo(322,125);p.quadraticCurveTo(337,143,324,162);});
        line(p=>{p.moveTo(205,115);p.quadraticCurveTo(250,145,295,115);});
        break;
      case "sculptural":
        line(p=>{p.moveTo(175,100);p.lineTo(205,88);p.lineTo(223,115);p.lineTo(205,130);p.moveTo(325,100);p.lineTo(295,88);p.lineTo(277,115);p.lineTo(295,130);});
        line(p=>{p.moveTo(216,147);p.lineTo(284,147);p.moveTo(224,155);p.lineTo(276,155);});
        break;
      case "layered":
        line(p=>{p.moveTo(205,130);p.lineTo(250,160);p.lineTo(295,130);p.moveTo(205,145);p.lineTo(250,175);p.lineTo(295,145);p.moveTo(215,190);p.lineTo(285,190);});
        break;
      case "minimal":
        line(p=>{p.moveTo(220,140);p.lineTo(230,260);p.moveTo(280,140);p.lineTo(270,260);p.moveTo(240,145);p.lineTo(240,245);p.moveTo(260,145);p.lineTo(260,245);});
        break;
      case "bow-collar":
        line(p=>{p.moveTo(226,96);p.lineTo(250,122);p.lineTo(274,96);p.lineTo(269,127);p.lineTo(250,137);p.lineTo(231,127);p.closePath();p.moveTo(226,96);p.lineTo(205,83);p.lineTo(205,117);p.lineTo(226,96);p.moveTo(274,96);p.lineTo(295,83);p.lineTo(295,117);p.lineTo(274,96);});
        for(let y=160;y<250;y+=30)dot(250,y,2.5);
        break;
      case "baroque":
        line(p=>{p.moveTo(213,170);p.bezierCurveTo(190,145,232,135,238,160);p.bezierCurveTo(245,183,214,190,220,211);p.bezierCurveTo(226,231,256,225,259,204);p.bezierCurveTo(262,181,290,185,287,158);p.bezierCurveTo(284,137,260,146,268,166);});
        flower(225,240,5);flower(275,240,5);
        break;
      case "retro70":
        line(p=>{p.moveTo(215,96);p.lineTo(240,123);p.lineTo(232,145);p.lineTo(210,120);p.moveTo(285,96);p.lineTo(260,123);p.lineTo(268,145);p.lineTo(290,120);p.moveTo(250,127);p.lineTo(250,245);});
        line(p=>{p.moveTo(240,127);p.lineTo(250,151);p.lineTo(260,127);});
        break;
      case "flare-sleeve":
        line(p=>{p.moveTo(176,120);p.quadraticCurveTo(155,167,130,190);p.moveTo(184,125);p.quadraticCurveTo(170,170,147,200);p.moveTo(324,120);p.quadraticCurveTo(345,167,370,190);p.moveTo(316,125);p.quadraticCurveTo(330,170,353,200);});
        break;
      case "mod":
        line(p=>{p.moveTo(220,102);p.quadraticCurveTo(250,135,280,102);p.moveTo(220,102);p.quadraticCurveTo(250,82,280,102);});
        for(let y=156;y<255;y+=25){dot(250,y,3.2);}
        break;
      case "metallic":
        line(p=>{p.moveTo(210,130);p.lineTo(250,150);p.lineTo(290,130);p.lineTo(280,178);p.lineTo(220,178);p.closePath();p.moveTo(220,190);p.lineTo(280,190);p.moveTo(230,205);p.lineTo(270,205);});
        for(let x=222;x<280;x+=14)dot(x,224,2.5);
        break;
      case "crochet":
        c.save();c.beginPath();c.rect(210,140,80,95);c.clip();
        for(let y=140;y<240;y+=15)for(let x=210;x<295;x+=16)line(p=>{p.moveTo(x,y+7);p.lineTo(x+8,y);p.lineTo(x+16,y+7);p.lineTo(x+8,y+14);p.closePath();},isGuide?1.2:1.8);
        c.restore();
        break;
      default:
        line(p=>{p.moveTo(215,150);p.lineTo(215,245);p.moveTo(285,150);p.lineTo(285,245);p.moveTo(220,155);p.lineTo(280,155);});
    }
    c.restore();
  }
  function createHistoricalFashionPiece(mode) {
    const season = historicalFashionCatalog[$("fashion-season").value];
    if (!season) { setNotice("Selecciona una temporada del archivo.", true); return; }
    const look = season.looks[Number($("fashion-look").value) || 0];
    if (!look) { setNotice("Selecciona una propuesta de diseño.", true); return; }
    $("garment-template").value = look.template;
    $("garment-variant").value = String(look.variant);
    if (mode !== "guide") $("design-color").value = look.color;
    const layer = createGarmentTemplate(look.template, mode === "guide" ? "guide" : "filled");
    if (!layer) return;
    layer.name = (mode === "guide" ? "Guía histórica — " : "Diseño histórico — ") + season.label + " — " + look.name;
    drawHistoricalMotif(layer, look, mode === "guide");
    syncDrawingLayer(layer);
    renderLayers(); renderInspector(); drawStage();
    setNotice((mode === "guide" ? "Guía histórica gris" : "Diseño original con color") + " creada: " + look.name + ". Inspiración: " + season.label + ". Ajusta tamaño y posición para adaptarla a tu personaje.");
  }
  function initHistoricalFashionArchive() {
    const select = $("fashion-season");
    Object.values(historicalFashionCatalog).forEach(season => {
      const option = document.createElement("option");
      option.value = season.key;
      option.textContent = season.label;
      select.append(option);
    });
    select.value = "2015-spring";
    updateHistoricalFashionLooks();
    select.addEventListener("change", updateHistoricalFashionLooks);
    $("fashion-look").addEventListener("change", updateHistoricalFashionInfo);
    $("create-fashion-guide").addEventListener("click", () => createHistoricalFashionPiece("guide"));
    $("create-fashion-color").addEventListener("click", () => createHistoricalFashionPiece("color"));
  }

function mapStagePointToLayer(layer,point){
    const dx=point.x-layer.x,dy=point.y-layer.y,radians=-layer.rotation*Math.PI/180;
    let rx=dx*Math.cos(radians)-dy*Math.sin(radians),ry=dx*Math.sin(radians)+dy*Math.cos(radians);
    if(layer.flipX)rx=-rx;if(layer.flipY)ry=-ry;
    return{x:Math.max(0,Math.min(layer.drawBuffer.width,(rx/layer.width+.5)*layer.drawBuffer.width)),y:Math.max(0,Math.min(layer.drawBuffer.height,(ry/layer.height+.5)*layer.drawBuffer.height))};
  }
  function traceStroke(context,stroke,mapped=false,layer=null,preview=false){
    const points=mapped&&layer?stroke.points.map(point=>mapStagePointToLayer(layer,point)):stroke.points;if(!points.length)return;
    context.save();context.globalCompositeOperation=!preview&&stroke.tool==="eraser"?"destination-out":"source-over";
    context.strokeStyle=preview&&stroke.tool==="eraser"?"#ff6d7e":stroke.color;context.fillStyle=stroke.color;
    context.lineWidth=Math.max(1,stroke.size*(mapped&&layer?(layer.drawBuffer.width/layer.width+layer.drawBuffer.height/layer.height)/2:1));context.lineCap="round";context.lineJoin="round";
    if(stroke.tool==="pen"||stroke.tool==="eraser"){
      context.beginPath();context.moveTo(points[0].x,points[0].y);for(let i=1;i<points.length;i++)context.lineTo(points[i].x,points[i].y);
      if(points.length===1){context.arc(points[0].x,points[0].y,Math.max(.5,context.lineWidth/2),0,Math.PI*2);context.fill();}else context.stroke();
    }else if(stroke.tool==="line"){context.beginPath();context.moveTo(points[0].x,points[0].y);context.lineTo(points[points.length-1].x,points[points.length-1].y);context.stroke();}
    else if(stroke.tool==="rect"){
      const a=points[0],b=points[points.length-1],x=Math.min(a.x,b.x),y=Math.min(a.y,b.y),w=Math.abs(b.x-a.x),h=Math.abs(b.y-a.y);
      if(stroke.fillShape)context.fillRect(x,y,w,h);context.strokeRect(x,y,w,h);
    }else if(stroke.tool==="ellipse"){
      const a=points[0],b=points[points.length-1],x=(a.x+b.x)/2,y=(a.y+b.y)/2,rx=Math.abs(b.x-a.x)/2,ry=Math.abs(b.y-a.y)/2;
      if(rx>0&&ry>0){context.beginPath();context.ellipse(x,y,rx,ry,0,0,Math.PI*2);if(stroke.fillShape)context.fill();context.stroke();}
    }
    context.restore();
  }
  function floodFill(layer,x,y,colour){
    if(!isDrawingLayer(layer))return;
    const canvas=layer.drawBuffer,width=canvas.width,height=canvas.height,total=width*height;
    if(total>4200000){setNotice("El relleno se limita para proteger la memoria. Reduce el tamaño del lienzo.",true);return;}
    x=Math.floor(x);y=Math.floor(y);if(x<0||y<0||x>=width||y>=height)return;
    const context=canvas.getContext("2d",{willReadFrequently:true}),image=context.getImageData(0,0,width,height),data=image.data,start=(y*width+x)*4;
    const target=[data[start],data[start+1],data[start+2],data[start+3]];
    if(target[3]<12){setNotice("El relleno no funciona sobre la transparencia vacía; haz clic dentro de una forma cerrada.",true);return;}
    const rgb=[parseInt(colour.slice(1,3),16),parseInt(colour.slice(3,5),16),parseInt(colour.slice(5,7),16)];
    if(Math.abs(target[0]-rgb[0])+Math.abs(target[1]-rgb[1])+Math.abs(target[2]-rgb[2])<8)return;
    const seen=new Uint8Array(total),queue=new Int32Array(total),tolerance=68;let head=0,tail=0;
    const add=index=>{if(index<0||index>=total||seen[index])return;const p=index*4;if(data[p+3]<12)return;if(Math.abs(data[p]-target[0])+Math.abs(data[p+1]-target[1])+Math.abs(data[p+2]-target[2])>tolerance)return;seen[index]=1;queue[tail++]=index;};
    add(y*width+x);
    while(head<tail){const index=queue[head++],p=index*4;data[p]=rgb[0];data[p+1]=rgb[1];data[p+2]=rgb[2];const px=index%width,py=Math.floor(index/width);if(px>0)add(index-1);if(px<width-1)add(index+1);if(py>0)add(index-width);if(py<height-1)add(index+width);}
    context.putImageData(image,0,0);syncDrawingLayer(layer);renderLayers();drawStage();setNotice("Relleno aplicado a "+tail.toLocaleString("es-AR")+" píxeles de la capa actual.");
  }

  async function addAssetLayer(asset) {
    try {
      const image = await imageFor(assetUrl(asset.path));
      const fit = Math.min((state.width * .72) / image.naturalWidth, (state.height * .72) / image.naturalHeight, 1);
      const scale = Math.max(.02, fit);
      const layer = {
        id: crypto.randomUUID(), name: asset.name, path: asset.path, dataUrl: "",
        category: "reference", x: state.width / 2, y: state.height / 2,
        width: image.naturalWidth * scale, height: image.naturalHeight * scale,
        rotation: 0, opacity: 1, visible: true, flipX: false, flipY: false
      };
      state.layers.push(layer); state.selectedLayerId = layer.id;
      renderLayers(); renderInspector(); drawStage();
      setNotice("Añadida como capa: " + asset.path + ". Puedes moverla, ajustar su tamaño o recortar una pieza.");
    } catch (error) { setNotice(error.message, true); }
  }
  async function getLayerPixels(layer) {
    if (!layer) throw new Error("Selecciona primero una capa con una imagen.");
    const image = await imageFor(layerSource(layer));
    const width = Number(image.naturalWidth || image.width), height = Number(image.naturalHeight || image.height);
    if (!Number.isInteger(width) || !Number.isInteger(height) || width < 1 || height < 1 || width * height > 16_000_000) {
      throw new Error("La edición local admite imágenes de hasta 16 megapíxeles por operación. Reduce el tamaño o recorta la imagen primero.");
    }
    const canvas = document.createElement("canvas");
    canvas.width = width; canvas.height = height;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    if (!context) throw new Error("No se pudo crear el lienzo de procesamiento.");
    context.drawImage(image, 0, 0, width, height);
    return { image, canvas, context, imageData: context.getImageData(0, 0, width, height) };
  }

  function addEditableRasterResult(sourceLayer, canvas, title) {
    const layer = {
      id: crypto.randomUUID(),
      name: (title + " — " + sourceLayer.name).slice(0, 150),
      path: "", dataUrl: "",
      category: sourceLayer.category === "reference" ? ($("design-category").value || "other") : sourceLayer.category,
      editableDrawing: true, isGarmentGuide: false, drawBuffer: canvas,
      x: sourceLayer.x, y: sourceLayer.y, width: sourceLayer.width, height: sourceLayer.height,
      rotation: sourceLayer.rotation, opacity: sourceLayer.opacity,
      visible: true, flipX: sourceLayer.flipX, flipY: sourceLayer.flipY,
      adjustments: sourceLayer.adjustments ? { ...sourceLayer.adjustments } : undefined
    };
    // Keep the source as a hidden baseline: this is reversible and never writes to the original file.
    sourceLayer.visible = false;
    state.layers.push(layer);
    state.selectedLayerId = layer.id;
    syncDrawingLayer(layer);
    renderLayers(); renderInspector(); drawStage();
    return layer;
  }

  async function rasterizeSelectedCopy() {
    const source = selectedLayer();
    if (!source) { setNotice("Selecciona el personaje o la capa de pelo que quieras retocar.", true); return; }
    try {
      const result = await getLayerPixels(source);
      const copyCanvas = document.createElement("canvas");
      copyCanvas.width = result.canvas.width; copyCanvas.height = result.canvas.height;
      copyCanvas.getContext("2d").drawImage(result.canvas, 0, 0);
      const layer = addEditableRasterResult(source, copyCanvas, "Copia editable");
      setNotice("Copia editable creada: «" + layer.name + "». El original quedó oculto, no modificado. Usa Borrador solo sobre esta copia.");
    } catch (error) { setNotice(error.message || "No se pudo crear una copia editable.", true); }
  }

  async function removeBackgroundFromSelected() {
    const source = selectedLayer();
    if (!source) { setNotice("Selecciona primero una capa de imagen.", true); return; }
    try {
      const result = await getLayerPixels(source);
      const processed = window.ImageProEditing.removeConnectedBackground(result.imageData, {
        targetColor: $("pro-bg-target").value,
        tolerance: Number($("pro-bg-tolerance").value),
        feather: Number($("pro-bg-feather").value),
        edgeSensitivity: Number($("pro-bg-edge").value),
        protectLineArt: $("pro-bg-protect-ink").checked,
        decontaminate: true
      });
      if (!processed.changed) {
        setNotice("No se detectó un fondo conectado con esos ajustes. Sube la tolerancia o elige otro color de fondo.", true);
        return;
      }
      const canvas = document.createElement("canvas");
      canvas.width = processed.width; canvas.height = processed.height;
      canvas.getContext("2d").putImageData(new ImageData(processed.data, processed.width, processed.height), 0, 0);
      const layer = addEditableRasterResult(source, canvas, "Fondo quitado");
      setNotice("Fondo retirado en una capa editable: «" + layer.name + "». Comprueba los bordes; el original se conserva oculto debajo.");
    } catch (error) { setNotice(error.message || "No se pudo quitar el fondo.", true); }
  }

  async function replaceColorOnSelected() {
    const source = selectedLayer();
    if (!source) { setNotice("Selecciona primero una capa de imagen.", true); return; }
    try {
      const result = await getLayerPixels(source);
      const processed = window.ImageProEditing.replaceColorRange(result.imageData, {
        sourceColor: $("pro-color-source").value,
        targetColor: $("pro-color-target").value,
        tolerance: Number($("pro-color-tolerance").value),
        softness: Number($("pro-color-softness").value),
        preserveShading: $("pro-color-preserve-shading").checked
      });
      const canvas = document.createElement("canvas");
      canvas.width = processed.width; canvas.height = processed.height;
      canvas.getContext("2d").putImageData(new ImageData(processed.data, processed.width, processed.height), 0, 0);
      const layer = addEditableRasterResult(source, canvas, "Color recoloreado");
      setNotice("Recoloración aplicada a una capa nueva: «" + layer.name + "». Ajusta el color de origen si afectó zonas que querías conservar.");
    } catch (error) { setNotice(error.message || "No se pudo reemplazar el color.", true); }
  }

  function syncProAdjustmentControls(layer) {
    if (!window.ImageProEditing) return;
    const values = window.ImageProEditing.normalizeLayerAdjustments(layer && layer.adjustments ? layer.adjustments : {});
    const controls = { brightness: "pro-brightness", contrast: "pro-contrast", saturation: "pro-saturation", hue: "pro-hue" };
    const labels = { brightness: "pro-brightness-value", contrast: "pro-contrast-value", saturation: "pro-saturation-value", hue: "pro-hue-value" };
    for (const [key, id] of Object.entries(controls)) {
      const input = $(id); input.value = values[key]; input.disabled = !layer;
      $(labels[key]).textContent = values[key] + (key === "hue" ? "°" : "");
    }
    const presets = window.ImageProEditing.LAYER_ADJUSTMENT_PRESETS;
    const match = presets.find(preset => Object.keys(values).every(key => values[key] === preset.values[key]));
    $("pro-adjustment-preset").value = match ? match.id : "custom";
    $("pro-adjustment-preset").disabled = !layer;
  }

  function setProAdjustmentInputs(values) {
    const normalized = window.ImageProEditing.normalizeLayerAdjustments(values);
    const controls = { brightness: "pro-brightness", contrast: "pro-contrast", saturation: "pro-saturation", hue: "pro-hue" };
    for (const [key, id] of Object.entries(controls)) $(id).value = normalized[key];
    const labels = { brightness: "pro-brightness-value", contrast: "pro-contrast-value", saturation: "pro-saturation-value", hue: "pro-hue-value" };
    for (const [key, id] of Object.entries(controls)) $(labels[key]).textContent = normalized[key] + (key === "hue" ? "°" : "");
  }

  function applyProAdjustments() {
    const layer = selectedLayer();
    if (!layer) { setNotice("Selecciona una capa antes de aplicar ajustes.", true); return; }
    layer.adjustments = window.ImageProEditing.normalizeLayerAdjustments({
      brightness: $("pro-brightness").value,
      contrast: $("pro-contrast").value,
      saturation: $("pro-saturation").value,
      hue: $("pro-hue").value,
      temperature: 0, tint: 0, blur: 0
    });
    renderLayers(); renderInspector(); drawStage();
    setNotice("Ajustes visuales guardados en «" + layer.name + "». Son reversibles y se conservan en el proyecto JSON.");
  }

  function initProEditingTools() {
    const sliders = [
      ["pro-bg-tolerance", "pro-bg-tolerance-value"],
      ["pro-bg-feather", "pro-bg-feather-value"],
      ["pro-bg-edge", "pro-bg-edge-value"],
      ["pro-color-tolerance", "pro-color-tolerance-value"],
      ["pro-color-softness", "pro-color-softness-value"]
    ];
    for (const [inputId, valueId] of sliders) {
      $(inputId).addEventListener("input", () => $(valueId).textContent = $(inputId).value);
    }
    for (const key of ["brightness", "contrast", "saturation", "hue"]) {
      const input = $("pro-" + key);
      input.addEventListener("input", () => $("pro-" + key + "-value").textContent = input.value + (key === "hue" ? "°" : ""));
    }
    $("pro-adjustment-preset").addEventListener("change", () => {
      const preset = window.ImageProEditing.LAYER_ADJUSTMENT_PRESETS.find(item => item.id === $("pro-adjustment-preset").value);
      if (preset) setProAdjustmentInputs(preset.values);
    });
    $("pro-rasterize-copy").addEventListener("click", rasterizeSelectedCopy);
    $("pro-remove-background").addEventListener("click", removeBackgroundFromSelected);
    $("pro-replace-color").addEventListener("click", replaceColorOnSelected);
    $("pro-apply-adjustments").addEventListener("click", applyProAdjustments);
    $("pro-reset-adjustments").addEventListener("click", () => {
      const layer = selectedLayer(); if (!layer) return;
      delete layer.adjustments; syncProAdjustmentControls(layer); drawStage(); renderLayers();
      setNotice("Ajustes restaurados al aspecto original de «" + layer.name + "».");
    });
  }

  function renderLayers() {
    layerList.replaceChildren();
    $("empty-layers").hidden = state.layers.length > 0;
    for (const layer of [...state.layers].reverse()) {
      const row = document.createElement("div");
      row.className = "layer-row" + (layer.id === state.selectedLayerId ? " selected" : "");
      const thumb = document.createElement("img"); thumb.alt = ""; thumb.src = layerSource(layer);
      const details = document.createElement("div"); details.style.minWidth = "0";
      const title = document.createElement("div"); title.className = "layer-title"; title.textContent = layer.name;
      const subtitle = document.createElement("div"); subtitle.className = "layer-subtitle"; subtitle.textContent = categories[layer.category] || categories.other;
      details.append(title, subtitle);
      const toggle = document.createElement("button"); toggle.className = "eye"; toggle.type = "button"; toggle.title = layer.visible ? "Ocultar capa" : "Mostrar capa"; toggle.textContent = layer.visible ? "◉" : "○";
      toggle.addEventListener("click", event => { event.stopPropagation(); layer.visible = !layer.visible; renderLayers(); drawStage(); });
      row.append(thumb, details, toggle);
      row.addEventListener("click", () => { state.selectedLayerId = layer.id; renderLayers(); renderInspector(); drawStage(); });
      layerList.append(row);
    }
    const hasLayer = Boolean(selectedLayer());
    ["duplicate-layer", "delete-layer", "crop-layer", "flip-layer", "send-back", "bring-front", "pro-rasterize-copy", "pro-remove-background", "pro-replace-color", "pro-apply-adjustments", "pro-reset-adjustments"].forEach(id => { if ($(id)) $(id).disabled = !hasLayer; });
  }
  function renderInspector() {
    const layer = selectedLayer();
    ["layer-category", "layer-x", "layer-y", "layer-width", "layer-height", "layer-rotation", "layer-opacity"].forEach(id => $(id).disabled = !layer);
    $("selected-layer-name").textContent = layer ? layer.name : "Selecciona una capa";
    if (!layer) return;
    $("layer-category").value = layer.category; $("layer-x").value = Math.round(layer.x); $("layer-y").value = Math.round(layer.y);
    $("layer-width").value = Math.round(layer.width); $("layer-height").value = Math.round(layer.height);
    $("layer-rotation").value = Math.round(layer.rotation); $("layer-opacity").value = Math.round(layer.opacity * 100);
    syncProAdjustmentControls(layer);
  }
  function updateSelectedFromControls() {
    const layer = selectedLayer(); if (!layer) return;
    const number = (id, fallback) => { const value = Number($(id).value); return Number.isFinite(value) ? value : fallback; };
    layer.category = $("layer-category").value;
    layer.x = Math.max(-state.width * 4, Math.min(state.width * 5, number("layer-x", layer.x)));
    layer.y = Math.max(-state.height * 4, Math.min(state.height * 5, number("layer-y", layer.y)));
    layer.width = Math.max(1, Math.min(10000, number("layer-width", layer.width)));
    layer.height = Math.max(1, Math.min(10000, number("layer-height", layer.height)));
    layer.rotation = Math.max(-360, Math.min(360, number("layer-rotation", layer.rotation)));
    layer.opacity = Math.max(0, Math.min(1, number("layer-opacity", layer.opacity * 100) / 100));
    renderLayers(); drawStage();
  }
  function findLayerAt(x, y) {
    const containsPoint = layer => {
      if (!layer || !layer.visible) return false;
      const dx = x - layer.x, dy = y - layer.y, radians = -layer.rotation * Math.PI / 180;
      const rx = dx * Math.cos(radians) - dy * Math.sin(radians);
      const ry = dx * Math.sin(radians) + dy * Math.cos(radians);
      return Math.abs(rx) <= layer.width / 2 && Math.abs(ry) <= layer.height / 2;
    };
    const selected = selectedLayer();
    if (containsPoint(selected)) return selected;
    for (const layer of [...state.layers].reverse()) {
      if (selected && layer.id === selected.id) continue;
      if (containsPoint(layer)) return layer;
    }
    return null;
  }
  let drag = null;
  stage.addEventListener("pointerdown",async event=>{
    const rect=stage.getBoundingClientRect(),point={x:(event.clientX-rect.left)*stage.width/rect.width,y:(event.clientY-rect.top)*stage.height/rect.height};
    if(state.designTool!=="move"){
      const layer=getOrCreateDrawingLayer();stage.setPointerCapture(event.pointerId);await drawStage(false);
      if(state.designTool==="bucket"){const mapped=mapStagePointToLayer(layer,point);floodFill(layer,mapped.x,mapped.y,$("design-color").value);return;}
      state.drawStroke={layerId:layer.id,tool:state.designTool,start:point,points:[point],color:$("design-color").value,size:Number($("design-brush-size").value),fillShape:$("design-fill-shapes").checked,baseImage:ctx.getImageData(0,0,stage.width,stage.height)};
      traceStroke(ctx,state.drawStroke,false,null,true);return;
    }
    const hit=findLayerAt(point.x,point.y);if(!hit)return;
    state.selectedLayerId=hit.id;drag={x:point.x,y:point.y,layerX:hit.x,layerY:hit.y,id:hit.id};
    stage.setPointerCapture(event.pointerId);renderLayers();renderInspector();drawStage();
  });
  stage.addEventListener("pointermove",event=>{
    const rect=stage.getBoundingClientRect(),point={x:(event.clientX-rect.left)*stage.width/rect.width,y:(event.clientY-rect.top)*stage.height/rect.height};
    $("canvas-coordinates").textContent=Math.round(point.x)+" , "+Math.round(point.y)+" px · "+state.width+" × "+state.height;
    if(state.drawStroke){const stroke=state.drawStroke;if(stroke.tool==="pen"||stroke.tool==="eraser")stroke.points.push(point);else stroke.points=[stroke.start,point];ctx.putImageData(stroke.baseImage,0,0);traceStroke(ctx,stroke,false,null,true);return;}
    if(!drag)return;const layer=state.layers.find(item=>item.id===drag.id);if(!layer)return;
    layer.x=drag.layerX+point.x-drag.x;layer.y=drag.layerY+point.y-drag.y;$("layer-x").value=Math.round(layer.x);$("layer-y").value=Math.round(layer.y);drawStage();
  });
  async function finishStagePointer(){
    if(state.drawStroke){const stroke=state.drawStroke;state.drawStroke=null;const layer=state.layers.find(item=>item.id===stroke.layerId);
      if(!isDrawingLayer(layer)){await drawStage();return;}
      traceStroke(layer.drawBuffer.getContext("2d"),stroke,true,layer,false);syncDrawingLayer(layer);renderLayers();renderInspector();await drawStage(true);
      setNotice((stroke.tool==="eraser"?"Borrado":"Trazo")+" aplicado a la capa editable «"+layer.name+"».");
    }
    drag=null;
  }
  stage.addEventListener("pointerup",finishStagePointer);stage.addEventListener("pointercancel",finishStagePointer);
  $("design-tools").querySelectorAll("[data-tool]").forEach(button=>button.addEventListener("click",()=>setDesignTool(button.dataset.tool)));
  $("design-brush-size").addEventListener("input",event=>$("brush-size-label").textContent=event.target.value+" px");
  $("new-design-layer").addEventListener("click",()=>createDrawingLayer());
  $("create-garment-guide").addEventListener("click",()=>createGarmentTemplate($("garment-template").value,"guide"));
  $("create-garment").addEventListener("click",()=>createGarmentTemplate($("garment-template").value,"filled"));

  $("asset-search").addEventListener("input", event => { state.query = event.target.value; state.offset = 0; refreshAssets(); });
  $("previous-page").addEventListener("click", () => { state.offset = Math.max(0, state.offset - state.pageSize); refreshAssets(); });
  $("next-page").addEventListener("click", () => { state.offset += state.pageSize; refreshAssets(); });
  $("apply-size").addEventListener("click", () => {
    const width = Number($("doc-width").value), height = Number($("doc-height").value);
    if (!Number.isInteger(width) || !Number.isInteger(height) || width < 128 || width > 2048 || height < 128 || height > 2048) { setNotice("El lienzo debe medir entre 128 y 2048 píxeles por lado.", true); return; }
    state.width = width; state.height = height; updateCanvasSize(); setNotice("Tamaño de lienzo actualizado a " + width + " × " + height + " px.");
  });
  ["layer-category", "layer-x", "layer-y", "layer-width", "layer-height", "layer-rotation", "layer-opacity"].forEach(id => $(id).addEventListener("change", updateSelectedFromControls));
  $("duplicate-layer").addEventListener("click", () => {
    const layer = selectedLayer(); if (!layer) return;
    const copy = { ...layer, id: crypto.randomUUID(), name: layer.name + " (copia)", x: layer.x + 20, y: layer.y + 20 };
    state.layers.push(copy); state.selectedLayerId = copy.id; renderLayers(); renderInspector(); drawStage();
  });
  $("delete-layer").addEventListener("click", () => {
    if (!selectedLayer()) return;
    state.layers = state.layers.filter(layer => layer.id !== state.selectedLayerId);
    state.selectedLayerId = state.layers.length ? state.layers[state.layers.length - 1].id : null;
    renderLayers(); renderInspector(); drawStage();
  });
  $("flip-layer").addEventListener("click", () => { const layer = selectedLayer(); if (layer) { layer.flipX = !layer.flipX; drawStage(); } });
  $("send-back").addEventListener("click", () => {
    const index = state.layers.findIndex(layer => layer.id === state.selectedLayerId);
    if (index > 0) { const layer = state.layers.splice(index, 1)[0]; state.layers.unshift(layer); renderLayers(); drawStage(); }
  });
  $("bring-front").addEventListener("click", () => {
    const index = state.layers.findIndex(layer => layer.id === state.selectedLayerId);
    if (index >= 0 && index < state.layers.length - 1) { const layer = state.layers.splice(index, 1)[0]; state.layers.push(layer); renderLayers(); drawStage(); }
  });

  function openCrop() {
    const layer = selectedLayer(); if (!layer) return;
    imageFor(layerSource(layer)).then(image => {
      const scale = Math.min(1, 1200 / image.naturalWidth, 1200 / image.naturalHeight);
      cropCanvas.width = Math.max(1, Math.round(image.naturalWidth * scale)); cropCanvas.height = Math.max(1, Math.round(image.naturalHeight * scale));
      cropCtx.clearRect(0, 0, cropCanvas.width, cropCanvas.height); cropCtx.drawImage(image, 0, 0, cropCanvas.width, cropCanvas.height);
      state.crop = { layerId: layer.id, image, scale, start: null, selection: null, strokes: [], activeStroke: null };
      $("crop-name").value = layer.name.replace(/\.[^.]+$/, "") + "-pieza";
      $("crop-category").value = layer.category === "reference" ? "other" : layer.category;
      $("create-crop").disabled = true; cropDialog.showModal();
    }).catch(error => setNotice(error.message, true));
  }
  function cropPoint(event) {
    const rect = cropCanvas.getBoundingClientRect();
    return { x: Math.max(0, Math.min(cropCanvas.width, (event.clientX - rect.left) * cropCanvas.width / rect.width)), y: Math.max(0, Math.min(cropCanvas.height, (event.clientY - rect.top) * cropCanvas.height / rect.height)) };
  }
  function redrawCrop() {
    if (!state.crop) return;
    const crop = state.crop;
    cropCtx.clearRect(0, 0, cropCanvas.width, cropCanvas.height);
    cropCtx.drawImage(crop.image, 0, 0, cropCanvas.width, cropCanvas.height);
    if (crop.selection) {
      const r = crop.selection;
      cropCtx.fillStyle = "#7da7ff24"; cropCtx.fillRect(r.x, r.y, r.w, r.h);
      cropCtx.strokeStyle = "#8eb4ff"; cropCtx.lineWidth = Math.max(2, cropCanvas.width / 500);
      cropCtx.setLineDash([8, 4]); cropCtx.strokeRect(r.x, r.y, r.w, r.h); cropCtx.setLineDash([]);
    }
    crop.strokes.forEach(stroke => paintMaskStroke(cropCtx, stroke, Number($("mask-brush-size").value), 0, 0, 1, 1, true));
    if (crop.activeStroke) paintMaskStroke(cropCtx, crop.activeStroke, Number($("mask-brush-size").value), 0, 0, 1, 1, true);
  }
  function currentCropTool() {
    const input = document.querySelector('input[name="crop-tool"]:checked');
    return input ? input.value : "select";
  }
  function paintMaskStroke(context, stroke, lineWidth, offsetX = 0, offsetY = 0, scaleX = 1, scaleY = 1, preview = false) {
    if (!stroke || !stroke.points || !stroke.points.length) return;
    context.save();
    context.globalAlpha = preview ? 0.62 : 1;
    context.globalCompositeOperation = "source-over";
    context.strokeStyle = preview ? (stroke.mode === "erase" ? "#ff5b70" : "#51e5cd") : (stroke.mode === "erase" ? "#000000" : "#ffffff");
    context.fillStyle = context.strokeStyle;
    context.lineWidth = Math.max(1, lineWidth); context.lineCap = "round"; context.lineJoin = "round";
    context.beginPath();
    const first = stroke.points[0], x0 = (first.x - offsetX) * scaleX, y0 = (first.y - offsetY) * scaleY;
    context.moveTo(x0, y0);
    for (let i = 1; i < stroke.points.length; i++) {
      const point = stroke.points[i]; context.lineTo((point.x - offsetX) * scaleX, (point.y - offsetY) * scaleY);
    }
    context.stroke();
    if (stroke.points.length === 1) { context.beginPath(); context.arc(x0, y0, Math.max(1, lineWidth / 2), 0, Math.PI * 2); context.fill(); }
    context.restore();
  }
  cropCanvas.addEventListener("pointerdown", event => {
    if (!state.crop) return;
    const point = cropPoint(event), tool = currentCropTool();
    if (tool === "select") {
      state.crop.start = point; state.crop.selection = { x: point.x, y: point.y, w: 0, h: 0 };
    } else {
      if (!state.crop.selection || state.crop.selection.w < 4 || state.crop.selection.h < 4) { setNotice("Primero selecciona el rectángulo de la pieza; después puedes borrar o restaurar zonas.", true); return; }
      state.crop.activeStroke = { mode: tool, points: [point] };
    }
    cropCanvas.setPointerCapture(event.pointerId); redrawCrop();
  });
  cropCanvas.addEventListener("pointermove", event => {
    if (!state.crop) return;
    const point = cropPoint(event);
    if (state.crop.start && currentCropTool() === "select") {
      const start = state.crop.start;
      state.crop.selection = { x: Math.min(start.x, point.x), y: Math.min(start.y, point.y), w: Math.abs(start.x - point.x), h: Math.abs(start.y - point.y) };
      redrawCrop();
    } else if (state.crop.activeStroke) { state.crop.activeStroke.points.push(point); redrawCrop(); }
  });
  function finishCropPointer() {
    if (!state.crop) return;
    if (state.crop.activeStroke) { state.crop.strokes.push(state.crop.activeStroke); state.crop.activeStroke = null; }
    state.crop.start = null;
    const rect = state.crop.selection; $("create-crop").disabled = !rect || rect.w < 4 || rect.h < 4;
    redrawCrop();
  }
  cropCanvas.addEventListener("pointerup", finishCropPointer);
  cropCanvas.addEventListener("pointercancel", finishCropPointer);
  $("undo-mask-stroke").addEventListener("click", () => {
    if (!state.crop || !state.crop.strokes.length) return;
    state.crop.strokes.pop(); redrawCrop();
  });
  $("background-tolerance").addEventListener("input", event => { $("tolerance-value").textContent = event.target.value; });

  function removeUniformBorderBackground(canvas, tolerance) {
    const context = canvas.getContext("2d", { willReadFrequently: true });
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data, width = canvas.width, height = canvas.height;
    if (!width || !height) return;
    const bg = [data[0], data[1], data[2]], limit = tolerance * tolerance * 3;
    const total = width * height, visited = new Uint8Array(total), queue = new Int32Array(total);
    let head = 0, tail = 0;
    const add = index => {
      if (index < 0 || index >= total || visited[index]) return;
      const p = index * 4, dr = data[p] - bg[0], dg = data[p + 1] - bg[1], db = data[p + 2] - bg[2];
      if (dr * dr + dg * dg + db * db > limit) return;
      visited[index] = 1; queue[tail++] = index;
    };
    for (let x = 0; x < width; x++) { add(x); add((height - 1) * width + x); }
    for (let y = 0; y < height; y++) { add(y * width); add(y * width + width - 1); }
    while (head < tail) {
      const index = queue[head++]; data[index * 4 + 3] = 0;
      const x = index % width, y = Math.floor(index / width);
      if (x > 0) add(index - 1); if (x < width - 1) add(index + 1);
      if (y > 0) add(index - width); if (y < height - 1) add(index + width);
    }
    context.putImageData(imageData, 0, 0);
  }
  $("create-crop").addEventListener("click", () => {
    const crop = state.crop, rect = crop && crop.selection;
    if (!crop || !rect || rect.w < 4 || rect.h < 4) return;
    const sx = Math.round(rect.x / crop.scale), sy = Math.round(rect.y / crop.scale);
    const sw = Math.max(1, Math.min(crop.image.naturalWidth - sx, Math.round(rect.w / crop.scale)));
    const sh = Math.max(1, Math.min(crop.image.naturalHeight - sy, Math.round(rect.h / crop.scale)));
    if (sw * sh > 4000000) { setNotice("Ese recorte es demasiado grande para el perfil de memoria conservador. Selecciona una zona de hasta 4 millones de píxeles.", true); return; }
    const out = document.createElement("canvas"); out.width = sw; out.height = sh;
    const outCtx = out.getContext("2d", { willReadFrequently: true }); outCtx.drawImage(crop.image, sx, sy, sw, sh, 0, 0, sw, sh);
    if (crop.strokes.length) {
      const mask = document.createElement("canvas"); mask.width = sw; mask.height = sh;
      const maskCtx = mask.getContext("2d"); maskCtx.fillStyle = "#ffffff"; maskCtx.fillRect(0, 0, sw, sh);
      const scaleX = sw / rect.w, scaleY = sh / rect.h, brush = Number($("mask-brush-size").value) / crop.scale;
      crop.strokes.forEach(stroke => paintMaskStroke(maskCtx, stroke, brush, rect.x, rect.y, scaleX, scaleY, false));
      outCtx.save(); outCtx.globalCompositeOperation = "destination-in"; outCtx.drawImage(mask, 0, 0); outCtx.restore();
    }
    if ($("remove-background").checked) removeUniformBorderBackground(out, Number($("background-tolerance").value));
    let dataUrl;
    try { dataUrl = out.toDataURL("image/png"); } catch { setNotice("No se pudo preparar el recorte. Prueba con una zona más pequeña.", true); return; }
    const fit = Math.min((state.width * .82) / sw, (state.height * .82) / sh, 1);
    const cleanName = ($("crop-name").value.trim() || "pieza-recortada").replace(/[<>:"/\\|?*]/g, "-");
    const layer = {
      id: crypto.randomUUID(), name: cleanName, path: "", dataUrl, category: $("crop-category").value,
      x: state.width / 2, y: state.height / 2, width: sw * Math.max(.02, fit), height: sh * Math.max(.02, fit),
      rotation: 0, opacity: 1, visible: true, flipX: false, flipY: false
    };
    state.layers.push(layer); state.selectedLayerId = layer.id; cropDialog.close(); state.crop = null;
    renderLayers(); renderInspector(); drawStage();
    setNotice("Pieza creada: " + layer.name + ". Se incluirá dentro del proyecto JSON; el original no cambió.");
  });
  $("cancel-crop").addEventListener("click", () => { cropDialog.close(); state.crop = null; });
  $("crop-dialog").addEventListener("close", () => { state.crop = null; });
  $("crop-layer").addEventListener("click", openCrop);

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob), anchor = document.createElement("a");
    anchor.href = url; anchor.download = filename; document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1500);
  }
  function projectData() {
    return {
      format: "IMAGE-CharacterProject", version: 1,
      canvas: { width: state.width, height: state.height, background: "transparent" },
      layers: state.layers.map(layer => ({
        ...layer,
        dataUrl: isDrawingLayer(layer) ? layer.drawBuffer.toDataURL("image/png") : layer.dataUrl,
        drawBuffer: undefined
      })),
      note: "Layers with path refer to the original local asset folder. Cropped dataUrl layers are embedded. Source images are not modified."
    };
  }
  $("save-project").addEventListener("click", () => {
    downloadBlob(new Blob([JSON.stringify(projectData(), null, 2)], { type: "application/json;charset=utf-8" }), "IMAGE-character-project.json");
    setNotice("Proyecto editable descargado. Conserva la carpeta de imágenes original para las capas que enlazan archivos.");
  });
  function validateProject(data) {
    if (!data || data.format !== "IMAGE-CharacterProject" || data.version !== 1 || !data.canvas || !Array.isArray(data.layers)) throw new Error("El archivo no es un proyecto de IMAGE compatible.");
    if (data.layers.length > 200) throw new Error("Este proyecto supera 200 capas; no se cargó para proteger la memoria.");
    const width = Number(data.canvas.width), height = Number(data.canvas.height);
    if (!Number.isInteger(width) || !Number.isInteger(height) || width < 128 || width > 2048 || height < 128 || height > 2048) throw new Error("El tamaño del lienzo del proyecto no es válido.");
    const layers = data.layers.map((layer, index) => {
      if (!layer || typeof layer !== "object" || typeof layer.path !== "string" || (typeof layer.dataUrl !== "string" && layer.dataUrl !== undefined)) throw new Error("La capa " + (index + 1) + " no es válida.");
      if (layer.dataUrl && !/^data:image\/(png|jpeg|webp);base64,/i.test(layer.dataUrl)) throw new Error("La capa " + (index + 1) + " contiene un tipo de archivo incrustado no permitido.");
      ["x", "y", "width", "height", "rotation", "opacity"].forEach(key => { if (!Number.isFinite(Number(layer[key]))) throw new Error("La propiedad " + key + " de la capa " + (index + 1) + " no es válida."); });
      if (Number(layer.width) <= 0 || Number(layer.width) > 10000 || Number(layer.height) <= 0 || Number(layer.height) > 10000) throw new Error("El tamaño de la capa " + (index + 1) + " no es válido.");
      const category = Object.prototype.hasOwnProperty.call(categories, layer.category) ? layer.category : "other";
      return {
        id: crypto.randomUUID(), name: String(layer.name || ("Capa " + (index + 1))).slice(0, 160),
        path: layer.path, dataUrl: layer.dataUrl || "", category,
        x: Math.max(-width * 4, Math.min(width * 5, Number(layer.x))), y: Math.max(-height * 4, Math.min(height * 5, Number(layer.y))),
        width: Number(layer.width), height: Number(layer.height), rotation: Math.max(-360, Math.min(360, Number(layer.rotation))),
        opacity: Math.max(0, Math.min(1, Number(layer.opacity))), visible: layer.visible !== false, flipX: Boolean(layer.flipX), flipY: Boolean(layer.flipY),
        editableDrawing: Boolean(layer.editableDrawing), isGarmentGuide: Boolean(layer.isGarmentGuide),
        adjustments: layer.adjustments ? window.ImageProEditing.normalizeLayerAdjustments(layer.adjustments) : undefined, drawBuffer: null
      };
    });
    if (layers.some(layer => !layer.path && !layer.dataUrl)) throw new Error("Hay una pieza sin archivo de origen ni datos incrustados.");
    return { width, height, layers };
  }
  async function hydrateDrawingLayers() {
    for (const layer of state.layers) {
      if (!layer.editableDrawing || !layer.dataUrl) continue;
      try { const image=await imageFor(layer.dataUrl); const buffer=document.createElement("canvas");buffer.width=image.naturalWidth;buffer.height=image.naturalHeight;buffer.getContext("2d").drawImage(image,0,0);layer.drawBuffer=buffer; }
      catch { setNotice("No se pudo recuperar una capa de dibujo del proyecto.",true); }
    }
  }
  $("load-project-button").addEventListener("click", () => $("load-project").click());
  $("load-project").addEventListener("change", async event => {
    const file = event.target.files && event.target.files[0]; if (!file) return;
    try {
      if (file.size > 60 * 1024 * 1024) throw new Error("El proyecto supera 60 MB; abre un proyecto más pequeño para proteger la memoria.");
      const loaded = validateProject(JSON.parse(await file.text()));
      state.width = loaded.width; state.height = loaded.height; state.layers = loaded.layers;
      state.selectedLayerId = state.layers.length ? state.layers[state.layers.length - 1].id : null;
      $("doc-width").value = state.width; $("doc-height").value = state.height;
      await hydrateDrawingLayers();
      updateCanvasSize(); renderLayers(); renderInspector(); drawStage();
      setNotice("Proyecto cargado. Si alguna capa enlazada no aparece, selecciona la carpeta original al iniciar el editor.");
    } catch (error) { setNotice(error.message, true); }
    finally { event.target.value = ""; }
  });
  $("export-png").addEventListener("click", async () => {
    if (!state.layers.length) { setNotice("Añade al menos una capa antes de exportar.", true); return; }
    await drawStage(false);
    stage.toBlob(blob => {
      drawStage(true);
      if (!blob) { setNotice("No se pudo exportar el PNG.", true); return; }
      downloadBlob(blob, "IMAGE-character.png"); setNotice("PNG exportado con fondo transparente.");
    }, "image/png");
  });
  $("new-project").addEventListener("click", () => {
    if (state.layers.length && !window.confirm("¿Empezar un proyecto nuevo? Guarda primero el proyecto actual si quieres conservarlo.")) return;
    state.layers = []; state.selectedLayerId = null; state.width = 768; state.height = 1024; state.designTool = "move";
    $("doc-width").value = 768; $("doc-height").value = 1024;
    document.querySelectorAll("[data-tool]").forEach(button=>button.classList.toggle("active",button.dataset.tool==="move"));
    updateCanvasSize(); renderLayers(); renderInspector();
    setNotice("Proyecto nuevo. Puedes añadir referencias, crear prendas desde plantillas o dibujar una pieza desde cero.");
  });
  updateCanvasSize(); renderLayers(); renderInspector(); initHistoricalFashionArchive(); initProEditingTools(); refreshAssets();
})();
