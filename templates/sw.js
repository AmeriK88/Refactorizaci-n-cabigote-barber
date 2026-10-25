// sw.js — Cabigote PWA
// feat(pwa,offline,ux): stable offline navigation, safe updates, and auth-safe routing

// 🔁 Bump this on every deploy that changes SW logic or offline.html
const SW_VERSION = "v4.2.1";
const CACHE_NAME = `cabigote-offline-${SW_VERSION}`;

// Offline fallback page (same-origin, predictable scope)
const OFFLINE_URL = new URL("/offline.html", self.location.origin).pathname;

// 🚫 Routes the SW must NEVER intercept
const IGNORE_PATHS = [
  "/accounts/", // allauth
  "/users/",    // custom auth
  "/admin/",    // Django admin
];

// ─────────────────────────────────────────────────────────────
// INSTALL: precache offline page (never fail install)
// ─────────────────────────────────────────────────────────────
self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      try {
        const cache = await caches.open(CACHE_NAME);
        const req = new Request(OFFLINE_URL, { cache: "reload" });
        const res = await fetch(req);

        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
        await cache.put(req, res.clone());

        console.info("[SW] Offline page cached");
      } catch (err) {
        console.warn("[SW] Offline cache failed:", err);
      }

      // 🚀 Activate ASAP
      self.skipWaiting();
    })()
  );
});

// ─────────────────────────────────────────────────────────────
// ACTIVATE: clean old caches & take control immediately
// ─────────────────────────────────────────────────────────────
self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();

      await Promise.all(
        keys.map((key) =>
          key.startsWith("cabigote-offline-") && key !== CACHE_NAME
            ? caches.delete(key)
            : Promise.resolve()
        )
      );

      // 🎯 Control existing tabs
      await self.clients.claim();
      console.info("[SW] Activated & controlling clients");
    })()
  );
});

// ─────────────────────────────────────────────────────────────
// FETCH: HTML navigation only → network-first + offline fallback
// ─────────────────────────────────────────────────────────────
self.addEventListener("fetch", (event) => {
  const req = event.request;

  // Only handle top-level HTML navigations
  if (
    req.method !== "GET" ||
    req.mode !== "navigate" ||
    !req.url.startsWith(self.location.origin)
  ) {
    return;
  }

  const url = new URL(req.url);

  // Never touch auth/admin routes
  if (IGNORE_PATHS.some((p) => url.pathname.startsWith(p))) {
    return;
  }

  event.respondWith(
    (async () => {
      try {
        // 🌐 Always try network first (fresh content)
        return await fetch(req);
      } catch {
        // 📴 Offline fallback
        const cached = await caches.match(OFFLINE_URL);
        return cached || Response.error();
      }
    })()
  );
});

// ─────────────────────────────────────────────────────────────
// MESSAGE: allow instant activation from frontend
// ─────────────────────────────────────────────────────────────
self.addEventListener("message", (event) => {
  if (event.data?.type === "SKIP_WAITING") self.skipWaiting();

});
