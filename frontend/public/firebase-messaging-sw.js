// Import and configure the Firebase SDK
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js');

// Initialize the Firebase app in the service worker
firebase.initializeApp({
  apiKey: "AIzaSyByII6mgOYpW1TGTTTqjnMKhF1v-Es8ZA4",
  authDomain: "studytrackr-216e9.firebaseapp.com",
  projectId: "studytrackr-216e9",
  storageBucket: "studytrackr-216e9.firebasestorage.app",
  messagingSenderId: "306871233412",
  appId: "1:306871233412:web:0bf75e338284871e62cbd1",
  measurementId: "G-RCMQTJBNEH"
});

// Retrieve an instance of Firebase Messaging so that it can handle background messages.
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  
  const notificationTitle = payload.notification?.title || 'StudyTrackr Update';
  const notificationOptions = {
    body: payload.notification?.body || '',
    icon: '/logo.png', // Assuming logo.png is in the public folder
    data: payload.data
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
