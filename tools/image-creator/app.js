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