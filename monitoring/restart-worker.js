export default {
  async scheduled(event, env, ctx) {
    const SERVICE_URL = "https://th.xurtxinh.id.vn";
    const RESTART_TOKEN = env.RESTART_TOKEN; // Get from Cloudflare Secrets

    console.log(`[${new Date().toISOString()}] Checking health: ${SERVICE_URL}/health`);

    try {
      const response = await fetch(`${SERVICE_URL}/health`, {
        method: "GET",
        headers: { "Accept": "application/json" },
        signal: AbortSignal.timeout(5000) // 5s timeout
      });

      if (response.ok) {
        console.log("Status: OK");
        return;
      }

      console.warn(`Status: FAILED (Code ${response.status}). Triggering restart...`);
      await triggerRestart(SERVICE_URL, RESTART_TOKEN);

    } catch (error) {
      console.error(`Status: DOWN (Error: ${error.message}). Triggering restart...`);
      await triggerRestart(SERVICE_URL, RESTART_TOKEN);
    }
  },

  // Manual trigger via HTTP for testing
  async fetch(request, env, ctx) {
    await this.scheduled(null, env, ctx);
    return new Response("Health check manual trigger completed. Check logs.");
  }
};

async function triggerRestart(url, token) {
  try {
    const res = await fetch(`${url}/api/restart`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });

    if (res.ok) {
      console.log("Restart status: RESTARTED (Request sent successfully)");
    } else {
      const text = await res.text();
      console.error(`Restart status: FAILED (Code ${res.status}: ${text})`);
    }
  } catch (err) {
    console.error(`Restart status: CRITICAL_ERROR (Could not reach restart endpoint: ${err.message})`);
  }
}
