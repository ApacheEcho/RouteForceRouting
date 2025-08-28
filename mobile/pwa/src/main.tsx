import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';


// Register service worker for PWA and handle push notifications
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(async (registration) => {
        console.log('SW registered: ', registration);
        // Request notification permission and subscribe to push
        if ('PushManager' in window) {
          const permission = await Notification.requestPermission();
          if (permission === 'granted') {
            try {
              const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array('<YOUR_PUBLIC_VAPID_KEY>') // Replace with your VAPID key
              });
              // Send subscription to backend (e.g., as part of device registration)
              // You can import and call registerDevice here if needed
              console.log('Push subscription:', subscription);
              // TODO: Send subscription to backend
            } catch (err) {
              console.error('Push subscription failed:', err);
            }
          }
        }
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Helper to convert VAPID key
function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
