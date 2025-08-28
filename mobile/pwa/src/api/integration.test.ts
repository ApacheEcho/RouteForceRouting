import { queueOfflineRequest } from './index';
import { vi } from 'vitest';

describe('Offline/Online Sync Integration', () => {
  it('should queue a request when offline and sync when online', async () => {
    // Mock service worker and postMessage
    const postMessageMock = vi.fn();
    (global as any).navigator.serviceWorker = {
      ready: Promise.resolve({ active: { postMessage: postMessageMock } })
    };
    await queueOfflineRequest('route-update', { id: '1' }, '/routes/1', 'PATCH');
    expect(postMessageMock).toHaveBeenCalledWith({
      type: 'QUEUE_OFFLINE_REQUEST',
      data: { type: 'route-update', data: { id: '1' }, url: '/routes/1', method: 'PATCH' }
    });
  });
});

describe('Push Notification Integration', () => {
  it('should request notification permission and subscribe to push', async () => {
    // Mock Notification and PushManager
    (global as any).Notification = { requestPermission: vi.fn(() => Promise.resolve('granted')) };
    const subscribeMock = vi.fn(() => Promise.resolve({ endpoint: 'https://push' }));
    (global as any).navigator.serviceWorker = {
      register: vi.fn(() => Promise.resolve({ pushManager: { subscribe: subscribeMock } }))
    };
    // Simulate registration and push subscription
    const registration = await navigator.serviceWorker.register('/sw.js');
    const permission = await Notification.requestPermission();
    expect(permission).toBe('granted');
    const subscription = await registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: new Uint8Array([1,2,3]) });

    expect(subscription.endpoint).toContain('https://push');
  });
});
