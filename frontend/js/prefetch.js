// Reads predicted pages and injects <link rel="prefetch"> to load them early

(function () {
  function pageToUrl(page) {
    switch (page) {
      case "index":
        return "/index.html";
      case "product":
        return "/product.html";
      case "cart":
        return "/cart.html";
      case "login":
        return "/login.html";
      case "checkout":
        return "/checkout.html";
      case "logout":
        return "/logout.html";
      default:
        return null;
    }
  }

  function injectPrefetch(url) {
    if (!url) return;

    // Avoid duplicates
    const existing = document.querySelector(
      'link[rel="prefetch"][data-pp-prefetch="' + url + '"]'
    );
    if (existing) return;

    const link = document.createElement("link");
    link.rel = "prefetch";
    link.href = url;
    link.setAttribute("data-pp-prefetch", url);
    document.head.appendChild(link);

    console.log("[PP-PREFETCH] added prefetch for", url);
  }

  function initPrefetch() {
    console.log("[PP-PREFETCH] Prefetch system initialized");

    const state = window.PP_PREFETCH;
    if (!state || !Array.isArray(state.predictedPages)) {
      console.log("[PP-PREFETCH] no predictions available yet");
      return;
    }

    state.predictedPages.forEach(function (page) {
      const url = pageToUrl(page);
      injectPrefetch(url);
    });
  }

  window.addEventListener("load", initPrefetch);
})();
