(function () {
  function openNearestDetails() {
    const hash = decodeURIComponent(location.hash || "");
    if (!hash) return;

    const el = document.querySelector(hash);
    if (!el) return;

    // En tu estructura: el H2 (#az-a) está arriba del <details>, así que buscamos el siguiente details
    let next = el.nextElementSibling;
    while (next && next.tagName !== "DETAILS") next = next.nextElementSibling;

    if (next && next.tagName === "DETAILS") {
      next.open = true;
    }
  }

  window.addEventListener("hashchange", openNearestDetails);
  window.addEventListener("DOMContentLoaded", openNearestDetails);
})();
