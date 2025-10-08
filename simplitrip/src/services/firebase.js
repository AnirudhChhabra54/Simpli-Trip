// src/services/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// IMPORTANT: Your web app's Firebase configuration
// It's highly recommended to move this configuration into environment variables
// to avoid exposing your API keys and other sensitive information in the source code.
// For example, you can use a .env file and process.env.REACT_APP_API_KEY.
const firebaseConfig = {
  apiKey: "AIzaSyCgnRNIkfU92dr6JdxrPlU5B2NcNPrVzSc",
  authDomain: "simplitrip.firebaseapp.com",
  projectId: "simplitrip",
  storageBucket: "simplitrip.firebasestorage.app",
  messagingSenderId: "1075212835917",
  appId: "1:1075212835917:web:75bb356b917ec750dbd004"
};

// Initialize Firebase app and services
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);