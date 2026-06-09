import { useState, useEffect } from 'react';
import { getToken, onMessage } from 'firebase/messaging';
import { messaging } from '../firebase';
import { api } from '../api/client';

export const usePushNotifications = (onMessageReceived?: (payload: any) => void) => {
    const [token, setToken] = useState<string | null>(null);
    const [permissionStatus, setPermissionStatus] = useState<NotificationPermission>(
        typeof Notification !== 'undefined' ? Notification.permission : 'default'
    );

    // Request permission and get token
    const requestPermissionAndRegister = async () => {
        if (!messaging) {
            console.warn("Push notifications are not supported by this browser.");
            return false;
        }

        try {
            const permission = await Notification.requestPermission();
            setPermissionStatus(permission);

            if (permission === 'granted') {
                // If the user doesn't have a VAPID key configured, we can still try to get a token, 
                // but some environments require a vapidKey. We will pass nothing and let Firebase handle it.
                // For production, you should generate a Web Push certificate in Firebase Console 
                // and pass it as: { vapidKey: 'YOUR_PUBLIC_VAPID_KEY_HERE' }
                const currentToken = await getToken(messaging, {
                    // vapidKey: 'YOUR_VAPID_KEY'
                });

                if (currentToken) {
                    console.log("FCM Token generated:", currentToken);
                    setToken(currentToken);
                    
                    // Register the token with our backend
                    await registerTokenWithBackend(currentToken);
                    return true;
                } else {
                    console.warn('No registration token available. Request permission to generate one.');
                    return false;
                }
            } else {
                console.warn('Notification permission not granted.');
                return false;
            }
        } catch (error) {
            console.error('An error occurred while retrieving token. ', error);
            return false;
        }
    };

    const registerTokenWithBackend = async (fcmToken: string) => {
        try {
            await api.post('/notifications/fcm/register-token', {
                token: fcmToken,
                device_type: 'web',
                // Can capture browser info using navigator.userAgent if desired
                browser_name: navigator.userAgent.substring(0, 50)
            });
            console.log("Token successfully registered with backend");
        } catch (error) {
            console.error("Failed to register token with backend", error);
        }
    };

    // Listen for foreground messages
    useEffect(() => {
        if (!messaging) return;

        const unsubscribe = onMessage(messaging, (payload) => {
            console.log('Received foreground message: ', payload);
            
            // In the foreground, we can show an in-app toast or manually trigger a notification
            const title = payload.notification?.title || 'New Notification';
            const body = payload.notification?.body || '';
            
            // We can leverage the browser's Notification API if we want to show it natively even in foreground
            if (Notification.permission === 'granted') {
                if ('serviceWorker' in navigator) {
                    navigator.serviceWorker.ready.then(registration => {
                        registration.showNotification(title, {
                            body: body,
                            icon: '/logo.png',
                            data: payload.data
                        });
                    }).catch(() => {
                        new Notification(title, { body: body, icon: '/logo.png', data: payload.data });
                    });
                } else {
                    new Notification(title, { body: body, icon: '/logo.png', data: payload.data });
                }
            }

            // Call the callback to trigger UI updates
            if (onMessageReceived) {
                onMessageReceived(payload);
            }
        });

        return () => {
            unsubscribe();
        };
    }, []);

    return {
        token,
        permissionStatus,
        requestPermissionAndRegister
    };
};
