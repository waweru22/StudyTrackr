import { initializeApp } from "firebase/app";
import { getMessaging } from "firebase/messaging";

const firebaseConfig = {
  apiKey: "AIzaSyByII6mgOYpW1TGTTTqjnMKhF1v-Es8ZA4",
  authDomain: "studytrackr-216e9.firebaseapp.com",
  projectId: "studytrackr-216e9",
  storageBucket: "studytrackr-216e9.firebasestorage.app",
  messagingSenderId: "306871233412",
  appId: "1:306871233412:web:0bf75e338284871e62cbd1",
  measurementId: "G-RCMQTJBNEH"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Cloud Messaging and get a reference to the service
// We use a try-catch because messaging() may throw if the browser doesn't support it
let messaging: any = null;
try {
    messaging = getMessaging(app);
} catch (error) {
    console.warn("Firebase Messaging is not supported in this browser:", error);
}

export { app, messaging };
