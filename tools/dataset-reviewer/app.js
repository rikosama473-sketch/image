(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const PAGE_SIZE = 24;
  const FIELDS = [
    "path","size_bytes","git_blob_sha","filename_origin_hint","source_url","author",
    "base_model_identifier","lora_identifiers","lora_weights_or_settings","visual_review","license_review","training_permission","hair","clothing","legs","pose","background","notes","lora_target_identifiers"
  ];
  const ATTRIBUTES = ["hair","clothing","legs","pose","background"];
  const REVIEW_FIELDS = ["visual_review","license_review","training_permission"];
  let records = new Map();
  let fileMap = new Map();
  let page = 0;
  let objectUrls = [];
  let currentVisible = [];

  function defaultRecord(path, file) {
    return {
      path,
      size_bytes: file ? String(file.size) : "",
      git_blob_sha: "",
      filename_origin_hint: path.startsWith("from-PixAI-") ? "PixAI-like filename; verify account and origin" : /^\d+\.png$/i.test(path) ? "numeric filename; origin unknown" : "unknown; review source",
      source_url: "",
      author: "",
      base_model_identifier: "",
      lora_identifiers: "",
      lora_weights_or_settings: "",
      lora_target_identifiers: "",
      visual_review: "unreviewed",
      license_review: "unreviewed",
      training_permission: "unreviewed",
      hair: "",
      clothing: "",
      legs: "",
      pose: "",
      background: "",
      notes: file ? "Inspect source, visual content and rights before training." : ""
    };
  }

  function normalizePath(file) {
    const raw = file.webkitRelativePath || file.name;
    const parts = raw.split("/");
    return (parts.length > 1 ? parts.slice(1) : parts).join("/");
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (c) => ({
      "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
    }[c]));
  }

  function parseCsv(text) {
    const rows = [];
    let row = [], field = "", quoted = false;
    for (let i = 0; i < text.length; i++) {
      const char = text[i];
      if (quoted) {
        if (char === '"' && text[i + 1] === '"') { field += '"'; i++; }
        else if (char === '"') quoted = false;
        else field += char;
      } else if (char === '"' && field.length === 0) quoted = true;
      else if (char === ",") { row.push(field); field = ""; }
      else if (char === "\n") { row.push(field); rows.push(row); row = []; field = ""; }
      else if (char !== "\r") field += char;
    }
    if (field.length || row.length) { row.push(field); rows.push(row); }
    return rows.filter((r) => r.some((v) => v !== ""));
  }

  function parseManifest(text) {
    const parsed = parseCsv(text);
    if (parsed.length < 2) return;
    const headers = parsed[0].map((h) => h.replace(/^\uFEFF/, "").trim());
    for (const values of parsed.slice(1)) {
      const incoming = {};
      headers.forEach((header, index) => { incoming[header] = values[index] ?? ""; });
      const path = (incoming.path || incoming.file || "").trim().replaceAll("\\", "/");
      if (!path) continue;
      const existing = records.get(path) || defaultRecord(path);
      records.set(path, { ...existing, ...incoming, path });
    }
  }

  function statusValue(value) {
    const normalized = String(value || "unreviewed").toLowerCase();
    if (normalized === "approved") return "approved";
    if (normalized === "reject" || normalized === "rejected" || normalized === "no") return "reject";
    return "unreviewed";
  }

  function isReady(record) {
    return REVIEW_FIELDS.every((f) => statusValue(record[f]) === "approved") &&
      ATTRIBUTES.every((f) => String(record[f] || "").trim() && String(record[f]).trim().toLowerCase() !== "unknown");
  }

  function isExcluded(record) {
    return REVIEW_FIELDS.some((f) => statusValue(record[f]) === "reject");
  }

  function statusOptions(current, label) {
    const value = statusValue(current);
    const options = [
      ["unreviewed","Pendiente"],
      ["approved","Aprobado"],
      ["reject","Excluir"]
    ];
    return '<label class="field"><span>' + label + '</span><select data-field="' + label + '" aria-label="' + label + '">' +
      options.map(([v,name]) => '<option value="' + v + '"' + (value === v ? " selected" : "") + '>' + name + '</option>').join("") +
      '</select></label>';
  }

  function textField(path, field, label, value, listId = "") {
    return '<label class="field"><span>' + label + '</span><input type="text" data-path="' + escapeHtml(path) +
      '" data-field="' + field + '" value="' + escapeHtml(value) + '"' +
      (listId ? ' list="' + listId + '"' : "") + ' autocomplete="off"></label>';
  }

  function renderCard(path, file, record) {
    const blobUrl = URL.createObjectURL(file);
    objectUrls.push(blobUrl);
    const labelStatuses = REVIEW_FIELDS.map((field) => {
      const value = statusValue(record[field]);
      const text = value === "approved" ? "Aprobado" : value === "reject" ? "Excluido" : "Pendiente";
      const cls = value === "approved" ? "ready-tag" : value === "reject" ? "exclude-tag" : "pending-tag";
      return '<span class="' + cls + '">' + field.replaceAll("_"," ") + ': ' + text + '</span>';
    }).join(" · ");
    const categoryFields = [
      textField(path,"hair","Cabello",record.hair,"hair-options"),
      textField(path,"clothing","Ropa",record.clothing,"clothing-options"),
      textField(path,"legs","Piernas",record.legs,"legs-options"),
      textField(path,"pose","Pose",record.pose,"pose-options"),
      textField(path,"background","Fondo",record.background,"background-options")
    ].join("");
    const provenance = [
      textField(path,"source_url","URL de origen",record.source_url),
      textField(path,"author","Autor/creador",record.author),
      textField(path,"base_model_identifier","Modelo base usado",record.base_model_identifier),
      textField(path,"lora_identifiers","LoRA(s) usada(s)",record.lora_identifiers),
      textField(path,"lora_weights_or_settings","Pesos/ajustes de LoRA de origen",record.lora_weights_or_settings),
      textField(path,"lora_target_identifiers","LoRA destino(s) que quiero usar/probar",record.lora_target_identifiers),
      '<label class="field"><span>Notas</span><input type="text" data-path="' + escapeHtml(path) + '" data-field="notes" value="' + escapeHtml(record.notes) + '"></label>'
    ].join("");
    const labelSet = isReady(record) ? "Listo para entrenar" : isExcluded(record) ? "Excluido del conjunto" : "Revisión pendiente";
    const labelClass = isReady(record) ? "ready-tag" : isExcluded(record) ? "exclude-tag" : "pending-tag";
    return '<article class="image-card" data-card-path="' + escapeHtml(path) + '">' +
      '<div class="preview"><img src="' + blobUrl + '" alt="Vista previa de ' + escapeHtml(path) + '" loading="lazy"></div>' +
      '<div class="card-content">' +
      '<div><div class="filename">' + escapeHtml(path) + '</div><div class="file-meta">' + (Number(record.size_bytes || file.size)/1024/1024).toFixed(2) + ' MiB · ' + escapeHtml(record.filename_origin_hint || "origen no revisado") + '</div></div>' +
      '<div class="' + labelClass + '">' + labelSet + '</div>' +
      '<div class="review-grid">' +
        statusOptions(record.visual_review,"visual_review").replace('data-field="visual_review"','data-path="' + escapeHtml(path) + '" data-field="visual_review"') +
        statusOptions(record.license_review,"license_review").replace('data-field="license_review"','data-path="' + escapeHtml(path) + '" data-field="license_review"') +
        statusOptions(record.training_permission,"training_permission").replace('data-field="training_permission"','data-path="' + escapeHtml(path) + '" data-field="training_permission"') +
      '</div>' +
      '<div class="attributes">' + categoryFields + '</div>' +
      '<details class="details"><summary>Procedencia y notas</summary><div class="details-body">' + provenance + '</div></details>' +
      '</div></article>';
  }

  function updateStats() {
    const all = [...fileMap.keys()].map((path) => records.get(path) || defaultRecord(path,fileMap.get(path)));
    $("#stat-total").textContent = String(all.length);
    $("#stat-pending").textContent = String(all.filter((r) => !isReady(r) && !isExcluded(r)).length);
    $("#stat-ready").textContent = String(all.filter(isReady).length);
    $("#stat-reject").textContent = String(all.filter(isExcluded).length);
  }

  function filteredFiles() {
    const search = $("#search-input").value.trim().toLowerCase();
    const filter = $("#filter-select").value;
    const sort = $("#sort-select").value;
    let items = [...fileMap.entries()].map(([path,file]) => {
      if (!records.has(path)) records.set(path, defaultRecord(path,file));
      return {path,file,record:records.get(path)};
    });
    items = items.filter(({path,record}) => {
      const searchable = [path, record.base_model_identifier, record.lora_identifiers, record.lora_weights_or_settings, record.lora_target_identifiers].join(" ").toLowerCase();
      if (search && !searchable.includes(search)) return false;
      if (filter === "ready" && !isReady(record)) return false;
      if (filter === "unreviewed" && (isReady(record) || isExcluded(record))) return false;
      if (filter === "excluded" && !isExcluded(record)) return false;
      return true;
    });
    items.sort((a,b) => {
      if (sort === "size-desc") return Number(b.record.size_bytes || b.file.size)-Number(a.record.size_bytes || a.file.size);
      if (sort === "size-asc") return Number(a.record.size_bytes || a.file.size)-Number(b.record.size_bytes || b.file.size);
      if (sort === "pending-first") return Number(isReady(a.record))-Number(isReady(b.record)) || a.path.localeCompare(b.path);
      return a.path.localeCompare(b.path,undefined,{numeric:true});
    });
    return items;
  }

  function render() {
    for (const url of objectUrls) URL.revokeObjectURL(url);
    objectUrls = [];
    currentVisible = filteredFiles();
    const totalPages = Math.ceil(currentVisible.length / PAGE_SIZE);
    if (page >= totalPages) page = Math.max(0,totalPages-1);
    const start = page * PAGE_SIZE;
    const slice = currentVisible.slice(start,start+PAGE_SIZE);
    $("#cards").innerHTML = slice.map(({path,file,record}) => renderCard(path,file,record)).join("");
    $("#cards").hidden = slice.length === 0;
    $("#empty-state").hidden = slice.length > 0;
    $("#empty-state").textContent = fileMap.size ? "No hay imágenes que coincidan con este filtro." : "Selecciona la carpeta local que contiene las imágenes para verlas en esta cuadrícula.";
    $("#range-label").textContent = currentVisible.length ? ((start+1) + "–" + (start+slice.length) + " de " + currentVisible.length + " resultados") : "0 resultados";
    $("#page-label").textContent = "Página " + (totalPages ? page+1 : 0) + " / " + totalPages;
    $("#prev-page").disabled = page <= 0;
    $("#next-page").disabled = page >= totalPages-1;
    updateStats();
  }

  $("#folder-input").addEventListener("change", (event) => {
    fileMap = new Map();
    for (const file of event.target.files || []) {
      if (!file.type.startsWith("image/")) continue;
      const path = normalizePath(file);
      fileMap.set(path,file);
      if (!records.has(path)) records.set(path,defaultRecord(path,file));
      else records.get(path).size_bytes = String(file.size);
    }
    page = 0;
    render();
  });

  $("#manifest-input").addEventListener("change", async (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    parseManifest(await file.text());
    render();
  });

  $("#cards").addEventListener("change", (event) => {
    const control = event.target.closest("[data-path][data-field]");
    if (!control) return;
    const record = records.get(control.dataset.path);
    if (!record) return;
    record[control.dataset.field] = control.value.trim();
    updateStats();
    if (REVIEW_FIELDS.includes(control.dataset.field)) render();
  });

  $("#search-input").addEventListener("input", () => { page = 0; render(); });
  $("#filter-select").addEventListener("change", () => { page = 0; render(); });
  $("#sort-select").addEventListener("change", () => { page = 0; render(); });
  $("#prev-page").addEventListener("click", () => { page = Math.max(0,page-1); render(); window.scrollTo({top:$("#cards").offsetTop,behavior:"smooth"}); });
  $("#next-page").addEventListener("click", () => { page++; render(); window.scrollTo({top:$("#cards").offsetTop,behavior:"smooth"}); });

  $("#export-button").addEventListener("click", () => {
    const all = [...records.values()].sort((a,b) => a.path.localeCompare(b.path,undefined,{numeric:true}));
    const csvValue = (value) => '"' + String(value ?? "").replaceAll('"','""') + '"';
    const text = [FIELDS.join(","), ...all.map((record) => FIELDS.map((field) => csvValue(record[field])).join(","))].join("\r\n") + "\r\n";
    const blob = new Blob(["\uFEFF",text],{type:"text/csv;charset=utf-8"});
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "training-labels.csv";
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url),1000);
  });
})();
