const CACHE_NAME = 'pat-bray-memorial-v1';
const ASSETS = [
  'index.html',
  'expanded_data.js',
  'patrick_bray_slideshow_workplan.html',
  'icon-192.png',
  'icon-512.png',
  'cover_photo.jpg',
  'soundtrack.mp3'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      );
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request).then(fetchRes => {
          return caches.open(CACHE_NAME).then(cache => {
            // Only cache images and other assets we want to persist
            if (event.request.url.match(/\.(jpg|jpeg|png|gif|mp3|html|js)$/)) {
              cache.put(event.request.url, fetchRes.clone());
            }
            return fetchRes;
          });
        });
      }).catch(() => {
        if (event.request.url.indexOf('.html') > -1) {
          return caches.match('index.html');
        }
      })
  );
});
