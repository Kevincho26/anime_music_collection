(async function () {
  function getPrefix() {
    // 1) intenta usar <base href="...">
    const baseAttr = document.querySelector("base")?.getAttribute("href");
    if (baseAttr) {
      try {
        const u = new URL(baseAttr, location.origin);
        return u.pathname.endsWith("/") ? u.pathname : u.pathname + "/";
      } catch {}
    }

    // 2) fallback: deduce desde la URL actual
    // Si estamos en /anime_music_collection/... -> prefix = /anime_music_collection/
    const seg = location.pathname.split("/").filter(Boolean);
    if (seg.length === 0) return "/";
    if (["series", "assets", "javascripts", "stylesheets"].includes(seg[0])) return "/";
    return `/${seg[0]}/`;
  }

  const prefix = getPrefix();
  const origin = location.origin;

  // Carga mapa URL -> {title, thumb}
  let map = {};
  try {
    const jsonUrl = origin + prefix + "assets/search_thumbs.json";
    const res = await fetch(jsonUrl, { cache: "no-store" });
    if (res.ok) map = await res.json();
  } catch {
    map = {};
  }

  function normalizeKeyFromHref(href) {
    const u = new URL(href, origin);
    let path = u.pathname;

    // quita prefix (/anime_music_collection/) para comparar con keys del JSON: "series/A/xxx/"
    if (prefix !== "/" && path.startsWith(prefix)) path = path.slice(prefix.length);

    path = path.replace(/^\//, "");
    path = path.replace(/index\.html?$/i, "");
    if (!path.endsWith("/")) path += "/";
    return decodeURIComponent(path);
  }

  function fixHrefIfNeeded(href) {
    // Si viene absoluto a raíz "/series/..." lo convertimos a "/anime_music_collection/series/..."
    if (href.startsWith("/") && prefix !== "/" && !href.startsWith(prefix)) {
      return prefix.replace(/\/$/, "") + href;
    }
    return href;
  }

  function enhance() {
    const items = document.querySelectorAll(".md-search-result__item");
    items.forEach((item) => {
      if (item.dataset.thumbified === "1") return;

      const a = item.querySelector("a");
      if (!a) return;

      const rawHref = a.getAttribute("href") || "";
      const fixedHref = fixHrefIfNeeded(rawHref);
      if (fixedHref !== rawHref) a.setAttribute("href", fixedHref);

      const key = normalizeKeyFromHref(a.getAttribute("href") || "");
      const meta = map[key];

      // si es algo de series pero no está en el mapa, lo ocultamos (evita “catálogos”)
      if (!meta && key.startsWith("series/")) {
        item.style.display = "none";
        item.dataset.thumbified = "1";
        return;
      }

      if (!meta) return;

      // render limpio: solo thumb + título
      const clean = document.createElement("a");
      clean.className = "search-card";
      clean.href = a.href;

      const img = document.createElement("img");
      img.className = "search-thumb";
      img.src = origin + prefix + meta.thumb;
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
