(() => {
  "use strict";

  const form = document.getElementById("creator-form");
  const generateButton = document.getElementById("generate-button");
  const refreshButton = document.getElementById("refresh-button");
  const statusCard = document.getElementById("job-status");
  const statusTitle = statusCard.querySelector("strong");
  const statusText = statusCard.querySelector("p");
  const statusIcon = statusCard.querySelector(".status-icon");
  const jobOutput = document.getElementById("job-output");
  const gallery = document.getElementById("gallery");
  const galleryCount = document.getElementById("gallery-count");
  let activeJobId = null;
  let pollTimer = null;
  let requestInFlight = false;

  const $ = (id) => document.getElementById(id);
  const value = (id) => $(id).value;
  const checked = (id) => $(id).checked;

  function setStatus(kind, title, text) {
    statusCard.dataset.kind = kind;
    statusTitle.textContent = title;
    statusText.textContent = text;
    statusIcon.textContent = kind === "working" ? "◌" : kind === "success" ? "✓" : kind === "error" ? "!" : "✳";
  }

  function setBusy(busy) {
    generateButton.disabled = busy;
    generateButton.firstElementChild.textContent = busy ? "Generando…" : "Generar imágenes";
  }

  async function api(url, options = {}) {
    const response = await fetch(url, {
      cache: "no-store",
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) }
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || ("Error HTTP " + response.status));
    return data;
  }

  function showLog(job) {
    const text = [job.stdout, job.stderr].filter(Boolean).join("\n\n");
    if (!text) {
      jobOutput.hidden = true;
      jobOutput.replaceChildren();
      return;
    }
    jobOutput.hidden = false;
    const pre = document.createElement("pre");
    pre.textContent = text;
    jobOutput.replaceChildren(pre);
  }

  function renderGallery(items) {
    gallery.replaceChildren();
    galleryCount.textContent = items.length + " " + (items.length === 1 ? "imagen" : "imágenes");
    if (!items.length) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      const symbol = document.createElement("div");
      symbol.className = "empty-symbol";
      symbol.textContent = "▧";
      const title = document.createElement("strong");
      title.textContent = "Todavía no hay resultados";
      const description = document.createElement("p");
      description.textContent = "Las imágenes generadas se guardarán en outputs/generated.";
      empty.append(symbol, title, description);
      gallery.append(empty);
      return;
    }

    for (const item of items) {
      const card = document.createElement("article");
      card.className = "gallery-item";
      const link = document.createElement("a");
      link.href = item.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.setAttribute("aria-label", "Abrir " + item.path);
      const image = document.createElement("img");
      image.loading = "lazy";
      image.src = item.url;
      image.alt = item.prompt || item.path;
      link.append(image);

      const info = document.createElement("div");
      info.className = "gallery-info";
      const name = document.createElement("strong");
      name.textContent = item.path.split("/").pop();
      const prompt = document.createElement("p");
      prompt.textContent = item.prompt || "Sin prompt registrado";
      const details = document.createElement("p");
      const detailsParts = [];
      if (item.seed !== undefined && item.seed !== "") detailsParts.push("Semilla " + item.seed);
      if (item.lora) detailsParts.push("LoRA: " + item.lora);
      details.textContent = detailsParts.join(" · ") || item.model || "Generación local";
      const metadataLink = document.createElement("a");
      metadataLink.href = item.url.replace(/\.png$/i, ".json");
      metadataLink.target = "_blank";
      metadataLink.rel = "noopener noreferrer";
      metadataLink.textContent = "Ver parámetros ↗";
      info.append(name, prompt, details, metadataLink);
      card.append(link, info);
      gallery.append(card);
    }
  }

  async function refreshGallery() {
    try {
      const data = await api("/api/runs");
      renderGallery(Array.isArray(data.runs) ? data.runs : []);
    } catch (error) {
      setStatus("error", "No se pudo cargar la galería", error.message);
    }
  }

  function payloadFromForm() {
    return {
      model: value("model").trim(),
      lora: value("lora").trim(),
      prompt: value("prompt").trim(),
      negative_prompt: value("negative-prompt").trim(),
      width: Number(value("width")),
      height: Number(value("height")),
      steps: Number(value("steps")),
      count: Number(value("count")),
      seed: Number(value("seed")),
      guidance_scale: Number(value("guidance-scale")),
      lora_scale: Number(value("lora-scale")),
      device: value("device"),
      precision: value("precision"),
      low_memory: checked("low-memory"),
      cpu_offload: checked("cpu-offload"),
      allow_download: checked("allow-download")
    };
  }

  async function pollJob(jobId) {
    try {
      const job = await api("/api/jobs/" + encodeURIComponent(jobId));
      if (job.status === "queued" || job.status === "running") {
        setBusy(true);
        setStatus("working", job.status === "queued" ? "En cola" : "Generando en esta PC", "El modelo está procesando la solicitud. El tiempo depende del modelo, la resolución y el hardware.");
        pollTimer = window.setTimeout(() => pollJob(jobId), 1400);
        return;
      }
      activeJobId = null;
      setBusy(false);
      showLog(job);
      if (job.status === "completed" || job.status === "partial") {
        const count = Array.isArray(job.images) ? job.images.length : 0;
        const requested = Number(job.requested_count || (job.config && job.config.count) || count);
        if (job.status === "partial") {
          setStatus("error", "Generación parcial", count + " de " + requested + " imágenes guardadas. " + (job.error || "Revisá el registro del motor."));
        } else {
          setStatus("success", "Generación terminada", count + " " + (count === 1 ? "imagen guardada" : "imágenes guardadas") + ". Los parámetros se conservaron junto a los archivos.");
        }
      } else {
        setStatus("error", "No se pudo completar la generación", job.error || "Revisá la salida del motor y la ruta del modelo/LoRA.");
      }
      await refreshGallery();
    } catch (error) {
      activeJobId = null;
      setBusy(false);
      showLog({ stderr: error.message });
      setStatus("error", "Se perdió el estado del trabajo", error.message);
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (requestInFlight || activeJobId) return;
    if (!form.reportValidity()) return;
    requestInFlight = true;
    setBusy(true);
    jobOutput.hidden = true;
    setStatus("working", "Preparando el motor", "Se validan parámetros y se carga el modelo local. Si el modelo no está instalado, la ejecución fallará sin descargar nada.");
    try {
      const data = await api("/api/generate", {
        method: "POST",
        body: JSON.stringify(payloadFromForm())
      });
      activeJobId = data.job_id;
      pollJob(activeJobId);
    } catch (error) {
      setBusy(false);
      setStatus("error", "No se pudo iniciar", error.message);
    } finally {
      requestInFlight = false;
    }
  });


  const diagnoseButton = $("diagnose-button");
  const diagnosticsPanel = $("diagnostics-panel");
  const diagnosticsList = $("diagnostics-list");
  const diagnosticsSummary = $("diagnostics-summary");

  function addDiagnosticRow(label, detail, kind) {
    const row = document.createElement("div");
    row.className = "diagnostic-row";
    row.dataset.kind = kind;
    const title = document.createElement("strong");
    title.textContent = label;
    const description = document.createElement("span");
    description.textContent = detail;
    row.append(title, description);
    diagnosticsList.append(row);
  }

  async function runDiagnostics() {
    diagnoseButton.disabled = true;
    diagnoseButton.textContent = "Comprobando…";
    diagnosticsPanel.hidden = false;
    diagnosticsList.replaceChildren();
    diagnosticsSummary.textContent = "Analizando sin generar ni descargar";
    try {
      const query = new URLSearchParams({
        model: value("model").trim(),
        lora: value("lora").trim(),
        device: value("device"),
        allow_download: String(checked("allow-download"))
      });
      const report = await api("/api/diagnostics?" + query.toString());
      addDiagnosticRow("Python", report.python_version + " · " + report.platform, "ok");
      addDiagnosticRow("Motor", report.engine_exists ? "Script de inferencia encontrado." : "No se encontró ml/generate_diffusion.py.", report.engine_exists ? "ok" : "error");
      for (const [name, present] of Object.entries(report.dependencies || {})) {
        addDiagnosticRow(name, present ? "Paquete detectable en este entorno." : "Falta instalar este paquete para usar difusión local.", present ? "ok" : "error");
      }
      addDiagnosticRow("Modelo", report.model.message, report.model.ready_to_try ? "ok" : "warn");
      const loraKind = ["not_configured", "local_file", "local_directory"].includes(report.lora.state) ? "ok" : "warn";
      addDiagnosticRow("LoRA", report.lora.message, loraKind);
      addDiagnosticRow("Dispositivo", (report.device_requested || "auto") + " · " + report.device_note, "warn");
      const ready = report.dependencies_ready && report.model.ready_to_try;
      diagnosticsSummary.textContent = ready ? "REQUISITOS BÁSICOS DETECTADOS" : "REVISAR ANTES DE GENERAR";
      setStatus(ready ? "success" : "idle", ready ? "Revisión preliminar aprobada" : "Todavía faltan comprobaciones", ready ? "Los requisitos básicos parecen estar presentes. La carga e inferencia reales aún pueden revelar incompatibilidades." : "Corregí los puntos señalados. Esta revisión no descargó modelos ni lanzó una generación.");
    } catch (error) {
      diagnosticsSummary.textContent = "No se pudo completar";
      addDiagnosticRow("Diagnóstico", error.message, "error");
      setStatus("error", "No se pudo comprobar el motor", error.message);
    } finally {
      diagnoseButton.disabled = false;
      diagnoseButton.textContent = "Volver a comprobar requisitos";
    }
  }


  const scanModelsButton = $("scan-models-button");
  const modelPicker = $("local-model-picker");
  const useModelButton = $("use-model-button");
  const modelScanStatus = $("model-scan-status");
  const modelOptions = $("local-model-options");

  async function scanLocalModels() {
    scanModelsButton.disabled = true;
    useModelButton.disabled = true;
    scanModelsButton.textContent = "Buscando…";
    modelScanStatus.textContent = "Inspeccionando carpetas de modelos existentes sin cargar pesos ni descargar archivos.";
    modelPicker.replaceChildren(new Option("Buscando modelos…", ""));
    modelPicker.disabled = true;
    modelOptions.replaceChildren();
    try {
      const result = await api("/api/models");
      modelPicker.replaceChildren();
      modelOptions.replaceChildren();
      if (!Array.isArray(result.models) || result.models.length === 0) {
        modelPicker.add(new Option("No se encontraron modelos", ""));
        modelScanStatus.textContent = "No encontré carpetas con model_index.json en las ubicaciones locales inspeccionadas. No se descargó nada; podés especificar manualmente una carpeta compatible.";
        return;
      }
      modelPicker.add(new Option("Elegí un modelo detectado…", ""));
      for (const model of result.models) {
        const option = new Option(model.label + " · " + model.pipeline_class, model.path);
        modelPicker.add(option);
        modelOptions.append(new Option(model.label, model.path));
      }
      modelPicker.disabled = false;
      modelScanStatus.textContent = "Detectados " + result.count + " pipelines locales en " + result.scanned_directories + " carpetas inspeccionadas." + (result.truncated ? " Búsqueda limitada por seguridad; hay más carpetas que revisar." : "") + " No se cargaron pesos ni se hicieron descargas.";
    } catch (error) {
      modelPicker.replaceChildren(new Option("No se pudo escanear", ""));
      modelScanStatus.textContent = "No se pudo leer el inventario local: " + error.message;
    } finally {
      scanModelsButton.disabled = false;
      scanModelsButton.textContent = "Volver a buscar";
      useModelButton.disabled = !modelPicker.value;
    }
  }

  modelPicker.addEventListener("change", () => {
    useModelButton.disabled = !modelPicker.value;
  });
  useModelButton.addEventListener("click", () => {
    const selectedPath = modelPicker.value;
    if (!selectedPath) return;
    $("model").value = selectedPath;
    setStatus("idle", "Modelo local seleccionado", "Se eligió una carpeta que contiene model_index.json. Ejecutá el diagnóstico antes de generar; la compatibilidad de inferencia aún debe comprobarse.");
  });
  scanModelsButton.addEventListener("click", scanLocalModels);

  diagnoseButton.addEventListener("click", runDiagnostics);

  refreshButton.addEventListener("click", refreshGallery);
  $("cpu-offload").addEventListener("change", (event) => {
    if (event.target.checked) {
      $("device").value = "cuda";
      setStatus("idle", "Ajustes actualizados", "La descarga de componentes a RAM requiere una GPU CUDA.");
    }
  });
  $("device").addEventListener("change", () => {
    if ($("device").value !== "cuda") $("cpu-offload").checked = false;
  });
  $("lora").addEventListener("input", () => {
    $("lora-scale").disabled = !$("lora").value.trim();
  });
  $("lora-scale").disabled = !$("lora").value.trim();

  refreshGallery();
})();