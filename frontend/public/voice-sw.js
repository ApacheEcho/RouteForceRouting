/**
 * Voice Coding Service Worker
 * Handles offline voice note storage and background sync
 */

const CACHE_NAME = 'voice-coding-v1';
const VOICE_NOTES_STORE = 'voice-notes';
const OFFLINE_QUEUE_STORE = 'offline-queue';

// Cache resources for offline use
const CACHE_URLS = [
  '/',
  '/voice-dashboard',
  '/static/js/voice-recorder.js',
  '/static/css/main.css',
  // Add other critical resources
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(CACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  // Handle voice API requests specially
  if (event.request.url.includes('/api/voice/')) {
    event.respondWith(handleVoiceAPIRequest(event.request));
    return;
  }

  // Handle other requests with cache-first strategy
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
      .catch(() => {
        // Return offline page if available
        if (event.request.mode === 'navigate') {
          return caches.match('/offline.html');
        }
      })
  );
});

// Handle voice API requests with offline capabilities
async function handleVoiceAPIRequest(request) {
  try {
    // Try to make the request online first
    const response = await fetch(request);
    return response;
  } catch (error) {
    // If offline, handle based on request type
    const url = new URL(request.url);
    const method = request.method;

    if (method === 'POST' && url.pathname.includes('/notes')) {
      // Store voice notes offline
      return handleOfflineVoiceNote(request);
    } else if (method === 'POST' && url.pathname.includes('/commit')) {
      // Queue commits for later
      return handleOfflineCommit(request);
    } else if (method === 'GET' && url.pathname.includes('/settings')) {
      // Return cached settings
      return handleOfflineSettings();
    }

    // Return generic offline response
    return new Response(
      JSON.stringify({
        error: 'Offline',
        message: 'This request will be processed when you\'re back online'
      }),
      {
        status: 202,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle offline voice note storage
async function handleOfflineVoiceNote(request) {
  try {
    const body = await request.json();
    const noteId = `offline-${Date.now()}`;
    
    // Store note in IndexedDB
    await storeInIndexedDB(VOICE_NOTES_STORE, {
      id: noteId,
      ...body,
      offline: true,
      timestamp: new Date().toISOString()
    });

    // Queue for sync when online
    await queueForSync({
      type: 'voice-note',
      data: body,
      url: request.url,
      method: request.method
    });

    return new Response(
      JSON.stringify({
        success: true,
        note_id: noteId,
        offline: true,
        message: 'Voice note saved offline, will sync when online'
      }),
      {
        status: 201,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: 'Failed to save offline',
        message: error.message
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle offline commit queuing
async function handleOfflineCommit(request) {
  try {
    const body = await request.json();
    const commitId = `offline-commit-${Date.now()}`;
    
    // Queue commit for later
    await queueForSync({
      type: 'commit',
      data: body,
      url: request.url,
      method: request.method,
      id: commitId
    });

    return new Response(
      JSON.stringify({
        success: true,
        commit_id: commitId,
        offline: true,
        message: 'Commit queued for when you\'re back online'
      }),
      {
        status: 202,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: 'Failed to queue commit',
        message: error.message
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle offline settings retrieval
async function handleOfflineSettings() {
  const defaultSettings = {
    language: 'en-US',
    auto_save: true,
    push_to_talk: false,
    noise_reduction: true,
    offline: true
  };

  try {
    // Try to get cached settings
    const cachedSettings = await getFromIndexedDB('settings', 'voice-settings');
    const settings = cachedSettings || defaultSettings;

    return new Response(
      JSON.stringify({
        success: true,
        data: settings,
        offline: true
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        success: true,
        data: defaultSettings,
        offline: true
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Queue items for background sync
async function queueForSync(item) {
  const queueItem = {
    ...item,
    timestamp: Date.now(),
    retries: 0
  };
  
  await storeInIndexedDB(OFFLINE_QUEUE_STORE, queueItem);
  
  // Register background sync if available
  if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
    try {
      await self.registration.sync.register('voice-sync');
    } catch (error) {
      console.log('Background sync registration failed:', error);
    }
  }
}

// Background sync event
self.addEventListener('sync', (event) => {
  if (event.tag === 'voice-sync') {
    event.waitUntil(processOfflineQueue());
  }
});

// Process offline queue when back online
async function processOfflineQueue() {
  try {
    const queueItems = await getAllFromIndexedDB(OFFLINE_QUEUE_STORE);
    
    for (const item of queueItems) {
      try {
        const response = await fetch(item.url, {
          method: item.method,
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(item.data)
        });

        if (response.ok) {
          // Remove successfully synced item
          await deleteFromIndexedDB(OFFLINE_QUEUE_STORE, item.id);
          
          // Notify client of successful sync
          await notifyClients({
            type: 'sync-success',
            data: item
          });
        } else {
          // Increment retry count
          item.retries = (item.retries || 0) + 1;
          if (item.retries < 3) {
            await storeInIndexedDB(OFFLINE_QUEUE_STORE, item);
          } else {
            // Remove after 3 failed attempts
            await deleteFromIndexedDB(OFFLINE_QUEUE_STORE, item.id);
            await notifyClients({
              type: 'sync-failed',
              data: item
            });
          }
        }
      } catch (error) {
        console.error('Sync error for item:', item, error);
      }
    }
  } catch (error) {
    console.error('Error processing offline queue:', error);
  }
}

// Notify all clients of sync status
async function notifyClients(message) {
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage(message);
  });
}

// IndexedDB helper functions
function openIndexedDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('VoiceCodingDB', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      // Create object stores
      if (!db.objectStoreNames.contains(VOICE_NOTES_STORE)) {
        const notesStore = db.createObjectStore(VOICE_NOTES_STORE, { keyPath: 'id' });
        notesStore.createIndex('timestamp', 'timestamp');
      }
      
      if (!db.objectStoreNames.contains(OFFLINE_QUEUE_STORE)) {
        const queueStore = db.createObjectStore(OFFLINE_QUEUE_STORE, { keyPath: 'id', autoIncrement: true });
        queueStore.createIndex('timestamp', 'timestamp');
      }
      
      if (!db.objectStoreNames.contains('settings')) {
        db.createObjectStore('settings', { keyPath: 'id' });
      }
    };
  });
}

async function storeInIndexedDB(storeName, data) {
  const db = await openIndexedDB();
  const transaction = db.transaction([storeName], 'readwrite');
  const store = transaction.objectStore(storeName);
  
  return new Promise((resolve, reject) => {
    const request = store.put(data);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function getFromIndexedDB(storeName, id) {
  const db = await openIndexedDB();
  const transaction = db.transaction([storeName], 'readonly');
  const store = transaction.objectStore(storeName);
  
  return new Promise((resolve, reject) => {
    const request = store.get(id);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function getAllFromIndexedDB(storeName) {
  const db = await openIndexedDB();
  const transaction = db.transaction([storeName], 'readonly');
  const store = transaction.objectStore(storeName);
  
  return new Promise((resolve, reject) => {
    const request = store.getAll();
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function deleteFromIndexedDB(storeName, id) {
  const db = await openIndexedDB();
  const transaction = db.transaction([storeName], 'readwrite');
  const store = transaction.objectStore(storeName);
  
  return new Promise((resolve, reject) => {
    const request = store.delete(id);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

// Message handling from clients
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
    case 'GET_OFFLINE_NOTES':
      handleGetOfflineNotes(event);
      break;
    case 'CLEAR_OFFLINE_DATA':
      handleClearOfflineData(event);
      break;
  }
});

async function handleGetOfflineNotes(event) {
  try {
    const notes = await getAllFromIndexedDB(VOICE_NOTES_STORE);
    event.ports[0].postMessage({
      success: true,
      data: notes
    });
  } catch (error) {
    event.ports[0].postMessage({
      success: false,
      error: error.message
    });
  }
}

async function handleClearOfflineData(event) {
  try {
    const db = await openIndexedDB();
    const transaction = db.transaction([VOICE_NOTES_STORE, OFFLINE_QUEUE_STORE], 'readwrite');
    
    await Promise.all([
      transaction.objectStore(VOICE_NOTES_STORE).clear(),
      transaction.objectStore(OFFLINE_QUEUE_STORE).clear()
    ]);
    
    event.ports[0].postMessage({
      success: true,
      message: 'Offline data cleared'
    });
  } catch (error) {
    event.ports[0].postMessage({
      success: false,
      error: error.message
    });
  }
}