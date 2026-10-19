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
    imageCache: new Map(), crop: null, requestId: 0
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
  function selectedLayer() { return state.layers.find(layer => layer.id === state.selectedLayerId) || null; }

  async function drawStage(showSelection = true) {
    ctx.clearRect(0, 0, stage.width, stage.height);
    for (const layer of state.layers) {
      if (!layer.visible) continue;
      try {
        const image = await imageFor(layerSource(layer));
        ctx.save();
        ctx.globalAlpha = Math.max(0, Math.min(1, layer.opacity));
        ctx.translate(layer.x, layer.y);
        ctx.rotate(layer.rotation * Math.PI / 180);
        ctx.scale(layer.flipX ? -1 : 1, layer.flipY ? -1 : 1);
        ctx.drawImage(image, -layer.width / 2, -layer.height / 2, layer.width, layer.height);
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
    ["duplicate-layer", "delete-layer", "crop-layer", "flip-layer", "send-back", "bring-front"].forEach(id => $(id).disabled = !hasLayer);
  }
  function renderInspector() {
    const layer = selectedLayer();
    ["layer-category", "layer-x", "layer-y", "layer-width", "layer-height", "layer-rotation", "layer-opacity"].forEach(id => $(id).disabled = !layer);
    $("selected-layer-name").textContent = layer ? layer.name : "Selecciona una capa";
    if (!layer) return;
    $("layer-category").value = layer.category; $("layer-x").value = Math.round(layer.x); $("layer-y").value = Math.round(layer.y);
    $("layer-width").value = Math.round(layer.width); $("layer-height").value = Math.round(layer.height);
    $("layer-rotation").value = Math.round(layer.rotation); $("layer-opacity").value = Math.round(layer.opacity * 100);
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
    for (const layer of [...state.layers].reverse()) {
      if (!layer.visible) continue;
      const dx = x - layer.x, dy = y - layer.y, radians = -layer.rotation * Math.PI / 180;
      const rx = dx * Math.cos(radians) - dy * Math.sin(radians);
      const ry = dx * Math.sin(radians) + dy * Math.cos(radians);
      if (Math.abs(rx) <= layer.width / 2 && Math.abs(ry) <= layer.height / 2) return layer;
    }
    return null;
  }
  let drag = null;
  stage.addEventListener("pointerdown", event => {
    const rect = stage.getBoundingClientRect();
    const x = (event.clientX - rect.left) * stage.width / rect.width, y = (event.clientY - rect.top) * stage.height / rect.height;
    const hit = findLayerAt(x, y); if (!hit) return;
    state.selectedLayerId = hit.id; drag = { x, y, layerX: hit.x, layerY: hit.y, id: hit.id };
    stage.setPointerCapture(event.pointerId); renderLayers(); renderInspector(); drawStage();
  });
  stage.addEventListener("pointermove", event => {
    const rect = stage.getBoundingClientRect();
    const x = (event.clientX - rect.left) * stage.width / rect.width, y = (event.clientY - rect.top) * stage.height / rect.height;
    $("canvas-coordinates").textContent = Math.round(x) + " , " + Math.round(y) + " px · " + state.width + " × " + state.height;
    if (!drag) return;
    const layer = state.layers.find(item => item.id === drag.id); if (!layer) return;
    layer.x = drag.layerX + x - drag.x; layer.y = drag.layerY + y - drag.y;
    $("layer-x").value = Math.round(layer.x); $("layer-y").value = Math.round(layer.y); drawStage();
  });
  stage.addEventListener("pointerup", () => { drag = null; });
  stage.addEventListener("pointercancel", () => { drag = null; });

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
      layers: state.layers.map(layer => ({ ...layer })),
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
        opacity: Math.max(0, Math.min(1, Number(layer.opacity))), visible: layer.visible !== false, flipX: Boolean(layer.flipX), flipY: Boolean(layer.flipY)
      };
    });
    if (layers.some(layer => !layer.path && !layer.dataUrl)) throw new Error("Hay una pieza sin archivo de origen ni datos incrustados.");
    return { width, height, layers };
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
    state.layers = []; state.selectedLayerId = null; state.width = 768; state.height = 1024;
    $("doc-width").value = 768; $("doc-height").value = 1024; updateCanvasSize(); renderLayers(); renderInspector();
    setNotice("Proyecto nuevo. Elige piezas de la biblioteca para componer un personaje.");
  });
  updateCanvasSize(); renderLayers(); renderInspector(); refreshAssets();
})();
