// src/services/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
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