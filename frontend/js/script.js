// Tracks user navigation and sends page events to the backend for prediction

  async function logPageView() {
  const sessionId = getSessionId();
  const page = getCurrentPageName();

  console.log("[PrefetchDemo] page_view", {
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
      console.warn("[PrefetchDemo] backend rejected event", res.status);
      return;
    }

    const data = await res.json();
    console.log("[PrefetchDemo] backend ack", data);

    if (Array.isArray(data.predicted_pages)) {
      console.log("[PrefetchDemo] predicted next pages:", data.predicted_pages);

      window.PP_PREFETCH = {
        lastPage: page,
        predictedPages: data.predicted_pages
      };
    }
  } catch (err) {
    console.warn("[PP-TRACK] failed to send event", err);
  }
}
