import { collection, addDoc, getDocs, doc, getDoc, updateDoc, deleteDoc, query, where } from "firebase/firestore";
import { db } from "./firebase";

const LOCAL_STORAGE_KEY = 'simplitrip_saved_trips';

const getLocalTrips = () => {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
};

const setLocalTrips = (trips) => {
  try {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(trips));
  } catch (e) {
    console.error('LocalStorage write error:', e);
  }
};

export const addTrip = async (tripData) => {
  // Always save locally first for instant availability
  const localId = `trip_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
  const tripToStore = {
    ...tripData,
    id: localId,
    createdAt: new Date().toISOString(),
  };

  const currentLocal = getLocalTrips();
  setLocalTrips([tripToStore, ...currentLocal]);

  try {
    if (db) {
      const tripsCollectionRef = collection(db, "trips");
      const docRef = await addDoc(tripsCollectionRef, tripData);
      return { id: docRef.id, ...tripData };
    }
  } catch (err) {
    console.warn("Firestore save failed, used offline local storage:", err);
  }

  return tripToStore;
};

export const getTripById = async (id) => {
  try {
    if (db) {
      const tripDoc = doc(db, "trips", id);
      const docSnap = await getDoc(tripDoc);
      if (docSnap.exists()) {
        return { id: docSnap.id, ...docSnap.data() };
      }
    }
  } catch (error) {
    console.warn("Firestore getTripById failed, checking local cache:", error);
  }

  // Fallback to local storage
  const localTrips = getLocalTrips();
  return localTrips.find((t) => t.id === id) || null;
};

export const getTripsByUserId = async (userId) => {
  let firestoreTrips = [];
  try {
    if (db && userId && !userId.startsWith('guest_')) {
      const tripsCollectionRef = collection(db, "trips");
      const q = query(tripsCollectionRef, where("userId", "==", userId));
      const querySnapshot = await getDocs(q);
      querySnapshot.forEach((doc) => {
        firestoreTrips.push({ id: doc.id, ...doc.data() });
      });
    }
  } catch (error) {
    console.warn("Firestore getTripsByUserId failed, falling back to local:", error);
  }

  const localTrips = getLocalTrips().filter((t) => !userId || t.userId === userId || userId.startsWith('guest_'));
  
  // Merge unique trips
  const combined = [...firestoreTrips];
  localTrips.forEach((lt) => {
    if (!combined.some((ft) => ft.id === lt.id || (ft.name === lt.name && ft.destination === lt.destination))) {
      combined.push(lt);
    }
  });

  return combined;
};

export const updateTrip = async (id, updatedData) => {
  // Update local storage
  const currentLocal = getLocalTrips();
  const updated = currentLocal.map((t) => (t.id === id ? { ...t, ...updatedData } : t));
  setLocalTrips(updated);

  try {
    if (db) {
      const tripDoc = doc(db, "trips", id);
      return await updateDoc(tripDoc, updatedData);
    }
  } catch (err) {
    console.warn("Firestore update failed, updated locally:", err);
  }
};

export const deleteTrip = async (id) => {
  // Remove from local storage
  const currentLocal = getLocalTrips();
  const filtered = currentLocal.filter((t) => t.id !== id);
  setLocalTrips(filtered);

  try {
    if (db) {
      const tripDoc = doc(db, "trips", id);
      return await deleteDoc(tripDoc);
    }
  } catch (err) {
    console.warn("Firestore delete failed, deleted locally:", err);
  }
};

export const toggleTripSharing = async (id, isShared) => {
  return updateTrip(id, { shared: isShared });
};