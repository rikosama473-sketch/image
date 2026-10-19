(() => {
  "use strict";
  const canvas = document.getElementById("preview-canvas");
  const ctx = canvas.getContext("2d");
  const toggle = document.getElementById("toggle-hair");
  const download = document.getElementById("download-preview");
  const status = document.getElementById("preview-status");
  let original = null;
  let hair = null;
  let showHair = true;

  function loadImage(path) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error("No se pudo abrir: " + path));
      image.src = "/api/asset?path=" + encodeURIComponent(path);
    });
  }
  function render() {
    if (!original) return;
    canvas.width = original.naturalWidth;
    canvas.height = original.naturalHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(original, 0, 0, canvas.width, canvas.height);
    if (showHair && hair) ctx.drawImage(hair, 0, 0, canvas.width, canvas.height);
    toggle.textContent = showHair ? "Ocultar coleta añadida" : "Mostrar coleta añadida";
    status.textContent = showHair
      ? "Vista compuesta: 12.png + cabello_01.svg. Solo se añadió una capa encima."
      : "Vista original: 12.png sin la pieza añadida.";
  }
  toggle.addEventListener("click", () => { showHair = !showHair; render(); });
  download.addEventListener("click", () => {
    canvas.toBlob(blob => {
      if (!blob) { status.textContent = "No se pudo exportar la vista compuesta."; return; }
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = "personaje-cabello-01-preview.png";
      a.click(); URL.revokeObjectURL(url);
    }, "image/png");
  });
  Promise.all([
    loadImage("12.png"),
    loadImage("assets/parts/hair/cabello_01.svg")
  ]).then(([base, hairImage]) => {
    original = base; hair = hairImage; render();
    toggle.disabled = false; download.disabled = false;
  }).catch(error => {
    status.textContent = error.message + ". Selecciona la raíz del repositorio como carpeta de imágenes al iniciar IMAGE.";
    status.classList.add("error");
  });
})();
