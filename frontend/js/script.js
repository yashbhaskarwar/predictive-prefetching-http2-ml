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

  async function logPageView() {
    const sessionId = getSessionId();
    const page = getCurrentPageName();

    console.log("[PP-TRACK] page_view", {
      session_id: sessionId,
      page: page,
      url: window.location.pathname
    });

    try {
      const res = await fetch("/api/event", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          session_id: sessionId,
          current_page: page
        })
      });

      if (!res.ok) {
        console.warn("[PP-TRACK] backend rejected event", res.status);
        return;
      }

      const data = await res.json();
      console.log("[PP-TRACK] backend ack", data);
    } catch (err) {
      console.warn("[PP-TRACK] failed to send event", err);
    }
  }

  window.addEventListener("load", logPageView);
})();
