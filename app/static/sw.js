/* Service Worker — Monitoring Kontrak PWA */
const CACHE_NAME = 'monkontrak-v1';
const STATIC_ASSETS = [
  '/static/css/main.css',
  '/static/js/pwa.js',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// Install — cache static assets
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(c => c.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate — hapus cache lama
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// Fetch — network-first, fallback ke cache
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Jangan cache API & non-GET
  if (e.request.method !== 'GET' || url.pathname.startsWith('/api/')) {
    return;
  }

  e.respondWith(
    fetch(e.request)
      .then(res => {
        // Simpan response valid ke cache
        if (res && res.status === 200 && res.type === 'basic') {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
        }
        return res;
      })
      .catch(() => {
        // Offline: ambil dari cache
        return caches.match(e.request).then(cached => {
          if (cached) return cached;
          // Halaman navigasi → offline fallback
          if (e.request.mode === 'navigate') {
            return caches.match('/static/offline.html');
          }
        });
      })
  );
});