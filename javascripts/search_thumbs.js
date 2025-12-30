(async function () {
  const siteRoot = new URL(document.querySelector("base")?.href || "/", location.origin);

  // Carga el mapa URL -> {title, thumb}
  let map = {};
  try {
    const res = await fetch(new URL("assets/search_thumbs.json", siteRoot).toString(), { cache: "no-store" });
    if (res.ok) map = await res.json();
  } catch {
    map = {};
  }

  function normalizeKey(href) {
    const u = new URL(href, siteRoot);
    let path = u.pathname;

    const basePath = siteRoot.pathname; // "/" o "/anime_music_collection/"
    if (basePath !== "/" && path.startsWith(basePath)) path = path.slice(basePath.length);

    path = path.replace(/^\//, "");
    path = path.replace(/index\.html?$/i, "");
    if (!path.endsWith("/")) path += "/";
    return decodeURIComponent(path);
  }

  function isSeriesPath(href) {
    try {
      const u = new URL(href, siteRoot);
      return u.pathname.includes("/series/");
    } catch {
      return (href || "").includes("/series/");
    }
  }

  function enhance() {
    const items = document.querySelectorAll(".md-search-result__item");
    items.forEach((item) => {
      // ya procesado
      if (item.dataset.thumbified === "1") return;

      const a = item.querySelector("a");
      if (!a) return;

      const href = a.getAttribute("href") || "";
      const key = normalizeKey(href);
      const meta = map[key];

      // Si es algo de /series/ pero no es una serie real (no está en el mapa), lo ocultamos
      if (!meta && isSeriesPath(href)) {
        item.style.display = "none";
        item.dataset.thumbified = "1";
        return;
      }

      // Solo re-renderizamos los que tengan thumbnail
      if (!meta) return;

      // Render limpio: SOLO thumb + título
      const clean = document.createElement("a");
      clean.className = "search-card";
      clean.href = a.href;

      const img = document.createElement("img");
      img.className = "search-thumb";
      img.src = new URL(meta.thumb, siteRoot).toString();
      img.alt = meta.title;

      const span = document.createElement("span");
      span.className = "search-title";
      span.textContent = meta.title;

      clean.appendChild(img);
      clean.appendChild(span);

      item.innerHTML = "";
      item.appendChild(clean);
      item.dataset.thumbified = "1";
    });
  }

  const obs = new MutationObserver(enhance);
  obs.observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener("DOMContentLoaded", enhance);
})();
