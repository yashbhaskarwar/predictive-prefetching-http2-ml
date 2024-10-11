(function () {
  function getSessionId() {
    let id = localStorage.getItem("pp_session_id");
    if (!id) {
      id = "sess_" + Math.random().toString(36).slice(2);
      localStorage.setItem("pp_session_id", id);
    }
    return id;
  }

  function getCurrentPageName() {
    const path = window.location.pathname;

    if (path.endsWith("product.html")) return "product";
    if (path.endsWith("cart.html")) return "cart";
    if (path.endsWith("login.html")) return "login";
    if (path.endsWith("checkout.html")) return "checkout";
    if (path.endsWith("logout.html")) return "logout";

    return "index";
  }

  function logPageView() {
    const sessionId = getSessionId();
    const page = getCurrentPageName();

    console.log("[PP-TRACK]", {
      session_id: sessionId,
      page: page,
      url: window.location.pathname
    });

    // Backend logging and ML prediction will be added in later steps
  }

  window.addEventListener("load", logPageView);
})();
