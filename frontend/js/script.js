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

    if (Array.isArray(data.predicted_pages)) {
      console.log("[PP-TRACK] predicted next pages:", data.predicted_pages);
    }
  } catch (err) {
    console.warn("[PP-TRACK] failed to send event", err);
  }
}
