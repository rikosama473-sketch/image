/* Referencias web de peinados para IMAGE.
 * Solo se muestran imágenes enlazadas desde sus sitios originales: no se copian al repo,
 * no se importan al lienzo y no se usan para entrenamiento.
 */
(() => {
  "use strict";
  const entries = [
  {
    "title": "Referencia principal: pelo corto con coleta lateral",
    "url": "https://images-ng.pixai.art/images/orig/808223a5-fff9-464d-bdb9-db5b96b5a38e",
    "source": "PixAI",
    "sourceUrl": "https://pixai.art/ja/model/1808757777133023840",
    "credit": "Modelo y ejemplos publicados por Jarvis en PixAI.",
    "kind": "Coleta lateral / pelo corto"
  },
  {
    "title": "Ejemplo PixAI 01",
    "url": "https://images-ng.pixai.art/images/thumb/c20c4c02-781e-4207-8a08-5a1186a2968e",
    "source": "PixAI",
    "sourceUrl": "https://pixai.art/ja/model/1808757777133023840",
    "credit": "Modelo y ejemplos publicados por Jarvis en PixAI.",
    "kind": "Coleta lateral / pelo corto"
  },
  {
    "title": "Ejemplo PixAI 02",
    "url": "https://images-ng.pixai.art/images/thumb/e6a1fe42-e699-43aa-bd78-f8a575b0cfa2",
    "source": "PixAI",
    "sourceUrl": "https://pixai.art/ja/model/1808757777133023840",
    "credit": "Modelo y ejemplos publicados por Jarvis en PixAI.",
    "kind": "Coleta lateral / pelo corto"
  },
  {
    "title": "Ejemplo PixAI 03",
    "url": "https://images-ng.pixai.art/images/thumb/21083fc1-4072-4745-8da1-ca2b45c37bd5",
    "source": "PixAI",
    "sourceUrl": "https://pixai.art/ja/model/1808757777133023840",
    "credit": "Modelo y ejemplos publicados por Jarvis en PixAI.",
    "kind": "Coleta lateral / pelo corto"
  },
  {
    "title": "Ejemplo PixAI 04",
    "url": "https://images-ng.pixai.art/images/thumb/34f1853e-6965-4f88-839d-bba887071810",
    "source": "PixAI",
    "sourceUrl": "https://pixai.art/ja/model/1808757777133023840",
    "credit": "Modelo y ejemplos publicados por Jarvis en PixAI.",
    "kind": "Coleta lateral / pelo corto"
  },
  {
    "title": "Ejemplo de peinado note.com 01",
    "url": "https://assets.st-note.com/img/1740583417-uhROzVbCQNA4vL85K0DFJoTq.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 02",
    "url": "https://assets.st-note.com/img/1740584032-l7XDryosGRUIAjETfJtYexMv.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 03",
    "url": "https://assets.st-note.com/img/1740584299-MZ0DnhFvT4xLauJ1QRwVIepc.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 04",
    "url": "https://assets.st-note.com/img/1740640649-lweTLvGFzhuSX9AoZQ6gx1ir.png?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 05",
    "url": "https://assets.st-note.com/img/1740584628-OrZLxUCKthbGeARmBl6D3021.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 06",
    "url": "https://assets.st-note.com/img/1740632182-VNd6WLEa7ZjI5TUJck32vpGx.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 07",
    "url": "https://assets.st-note.com/img/1740637530-1HRT6Zm4h8p9iIteDSwNayA0.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 08",
    "url": "https://assets.st-note.com/img/1740638393-5M469PhQyuUwzkSFvlOiErJ8.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 09",
    "url": "https://assets.st-note.com/img/1740638725-6RrqLYofDjU1wtAkCOvE0Zu7.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 10",
    "url": "https://assets.st-note.com/img/1740625878-vUsk7lxM28yzidg9P4cobABW.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 11",
    "url": "https://assets.st-note.com/img/1740626664-JVXfO4IE0oPTxYKdm2c6Q7n9.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 12",
    "url": "https://assets.st-note.com/img/1740627839-yLzMaidmA3xDt069qKfbPECB.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 13",
    "url": "https://assets.st-note.com/img/1740628506-z9OenGgPUFJ5H4wANRyc8qBf.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 14",
    "url": "https://assets.st-note.com/img/1740628972-nFv29HNEJx4P6rZ1wWap0RKu.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 15",
    "url": "https://assets.st-note.com/img/1740629043-BoE8jeLX0tFRm96pkubnJzWg.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 16",
    "url": "https://assets.st-note.com/img/1740630226-vB25Cl704u6Y8it3LQTFgOKo.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 17",
    "url": "https://assets.st-note.com/img/1740630906-4beERuSQLUgqlXrZD0927nVp.jpg?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 18",
    "url": "https://assets.st-note.com/img/1740643484-S8DcAna5XlBs4jvQKGk9MtTe.png?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ejemplo de peinado note.com 19",
    "url": "https://assets.st-note.com/img/1740643473-U0nft1CjzFimIr2xVpckBKul.png?width=1200",
    "source": "note.com",
    "sourceUrl": "https://note.com/yukyu_haruka/n/n56ab509496ad",
    "credit": "Artículo de 悠～ゆう～ sobre recogidos y cortes; abrir la fuente para identificar cada variante.",
    "kind": "Recogidos y cortes"
  },
  {
    "title": "Ilustración de peinados 01 · artículo de 12 estilos",
    "url": "https://cdn.michill.jp/v2/w_640,h_640,f_webp,q_90/img/articles/91279/0.jpg",
    "source": "michill.jp",
    "sourceUrl": "https://michill.jp/beauty/91279",
    "credit": "Artículo ilustrado de michill byGMO, localizado desde el pin de Pinterest.",
    "kind": "Peinados cortos y recogidos"
  },
  {
    "title": "Ilustración de peinados 02 · artículo de 12 estilos",
    "url": "https://cdn.michill.jp/v2/w_640,h_640,f_webp,q_90/img/articles/91279/1.jpg",
    "source": "michill.jp",
    "sourceUrl": "https://michill.jp/beauty/91279",
    "credit": "Artículo ilustrado de michill byGMO, localizado desde el pin de Pinterest.",
    "kind": "Peinados cortos y recogidos"
  },
  {
    "title": "Ilustración de peinados 03 · artículo de 12 estilos",
    "url": "https://cdn.michill.jp/v2/w_640,h_640,f_webp,q_90/img/articles/91279/2.jpg",
    "source": "michill.jp",
    "sourceUrl": "https://michill.jp/beauty/91279",
    "credit": "Artículo ilustrado de michill byGMO, localizado desde el pin de Pinterest.",
    "kind": "Peinados cortos y recogidos"
  },
  {
    "title": "Ilustración de peinados 04 · artículo de 12 estilos",
    "url": "https://cdn.michill.jp/v2/w_640,h_640,f_webp,q_90/img/articles/91279/3.jpg",
    "source": "michill.jp",
    "sourceUrl": "https://michill.jp/beauty/91279",
    "credit": "Artículo ilustrado de michill byGMO, localizado desde el pin de Pinterest.",
    "kind": "Peinados cortos y recogidos"
  },
  {
    "title": "Ilustración de peinados 05 · artículo de 12 estilos",
    "url": "https://cdn.michill.jp/v2/w_640,h_640,f_webp,q_90/img/articles/91279/4.jpg",
    "source": "michill.jp",
    "sourceUrl": "https://michill.jp/beauty/91279",
    "credit": "Artículo ilustrado de michill byGMO, localizado desde el pin de Pinterest.",
    "kind": "Peinados cortos y recogidos"
  },
  {
    "title": "Ilustración de peinados 06 · artículo de 12 estilos",
    "url": "https://cdn.michill.jp/v2/w_640,h_640,f_webp,q_90/img/articles/91279/5.jpg",
    "source": "michill.jp",
    "sourceUrl": "https://michill.jp/beauty/91279",
    "credit": "Artículo ilustrado de michill byGMO, localizado desde el pin de Pinterest.",
    "kind": "Peinados cortos y recogidos"
  },
  {
    "title": "Ilustración de peinados 07 · artículo de 12 estilos",
    "url": "https://cdn.michill.jp/v2/w_640,h_640,f_webp,q_90/img/articles/91279/6.jpg",
    "source": "michill.jp",
    "sourceUrl": "https://michill.jp/beauty/91279",
    "credit": "Artículo ilustrado de michill byGMO, localizado desde el pin de Pinterest.",
    "kind": "Peinados cortos y recogidos"
  },
  {
    "title": "Secuencia completa: construcción de una coleta",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_hair_drawing_step_by_step.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Paso 1: cabeza y hombros",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_head_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Paso 2: línea del cabello sobre la cabeza",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_hairline_on_head_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Paso 2: contorno del cabello recogido",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_hairline_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Paso 3: masa principal de pelo y coleta",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_hair_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Guía frontal para el flequillo",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_hair_front_guide_line_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Coleta con línea del cabello",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_with_hairline_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Paso 4: flequillo y mechones frontales",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_forehead_hair_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Contorno de línea terminado",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_line_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Reflejos y brillos",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_hair_highlights_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Sombreado principal",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_hair_drawing_shading.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Sombras de mechones frontales",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_pigtails_hair_shadows_front_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Sombras laterales",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_hair_shadows_sides_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Sombras de la coleta",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_hair_shadows_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  },
  {
    "title": "Resultado final del tutorial",
    "url": "https://www.animeoutline.com/wp-content/uploads/2023/11/anime_ponytail_drawing.png",
    "source": "AnimeOutline",
    "sourceUrl": "https://www.animeoutline.com/how-to-draw-anime-ponytail-hair/",
    "credit": "Tutorial paso a paso publicado por AnimeOutline.",
    "kind": "Construcción de coleta anime"
  }
];
  const root = document.getElementById("hair-reference-library");
  const grid = document.getElementById("hair-reference-grid");
  const search = document.getElementById("hair-reference-search");
  const sourceFilter = document.getElementById("hair-reference-source-filter");
  const status = document.getElementById("hair-reference-status");
  if (!root || !grid || !search || !sourceFilter || !status) return;

  const sources = [...new Set(entries.map(item => item.source))];
  for (const source of sources) {
    const option = document.createElement("option");
    option.value = source;
    option.textContent = source;
    sourceFilter.append(option);
  }
  function render() {
    const query = search.value.trim().toLocaleLowerCase();
    const source = sourceFilter.value;
    const filtered = entries.filter(item =>
      (source === "all" || item.source === source) &&
      (!query || (item.title + " " + item.kind + " " + item.credit + " " + item.source)
        .toLocaleLowerCase().includes(query))
    );
    grid.replaceChildren();
    for (const item of filtered) {
      const card = document.createElement("article");
      card.className = "hair-reference-card";
      const preview = document.createElement("a");
      preview.className = "hair-reference-preview";
      preview.href = item.url;
      preview.target = "_blank";
      preview.rel = "noopener noreferrer";
      preview.title = "Abrir la imagen original en una pestaña nueva";
      const image = document.createElement("img");
      image.loading = "lazy";
      image.decoding = "async";
      image.referrerPolicy = "no-referrer";
      image.alt = item.title;
      image.src = item.url;
      image.addEventListener("error", () => {
        preview.classList.add("is-unavailable");
        image.remove();
        const fallback = document.createElement("span");
        fallback.textContent = "Vista previa bloqueada por la web de origen";
        preview.append(fallback);
      }, { once: true });
      preview.append(image);

      const body = document.createElement("div");
      body.className = "hair-reference-copy";
      const title = document.createElement("strong");
      title.textContent = item.title;
      const type = document.createElement("small");
      type.textContent = item.kind;
      const links = document.createElement("div");
      links.className = "hair-reference-links";
      const sourceLink = document.createElement("a");
      sourceLink.href = item.sourceUrl;
      sourceLink.target = "_blank";
      sourceLink.rel = "noopener noreferrer";
      sourceLink.textContent = "Fuente: " + item.source;
      const directLink = document.createElement("a");
      directLink.href = item.url;
      directLink.target = "_blank";
      directLink.rel = "noopener noreferrer";
      directLink.textContent = "Abrir imagen";
      const credit = document.createElement("p");
      credit.textContent = item.credit;
      body.append(title, type, links, credit);
      links.append(sourceLink, directLink);
      card.append(preview, body);
      grid.append(card);
    }
    status.textContent = filtered.length + " de " + entries.length +
      " imágenes enlazadas. Las vistas previas vienen de sus páginas originales; necesitas Internet. " +
      "No se descargan en el proyecto ni se añaden automáticamente al lienzo.";
  }
  search.addEventListener("input", render);
  sourceFilter.addEventListener("change", render);
  root.addEventListener("toggle", () => { if (root.open && !grid.childElementCount) render(); });
  render();
})();
