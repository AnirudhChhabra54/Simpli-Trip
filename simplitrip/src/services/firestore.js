




import { collection, addDoc, getDocs, doc, getDoc, updateDoc, deleteDoc, query, where } from "firebase/firestore";
import { db } from "./firebase";

const tripsCollectionRef = collection(db, "trips");

export const addTrip = (tripData) => {
  return addDoc(tripsCollectionRef, tripData);
};

export const getTripById = async (id) => {
  try {
    const tripDoc = doc(db, "trips", id);
    const docSnap = await getDoc(tripDoc);
    if (docSnap.exists()) {
      return { id: docSnap.id, ...docSnap.data() };
    }
    return null;
  } catch (error) {
    console.error("Error getting trip:", error);
    throw error;
  }
};

export const getTripsByUserId = async (userId) => {
  try {
    const q = query(tripsCollectionRef, where("userId", "==", userId));
    const querySnapshot = await getDocs(q);
    const trips = [];
    querySnapshot.forEach((doc) => {
      trips.push({ id: doc.id, ...doc.data() });
    });
    return trips;
  } catch (error) {
    console.error("Error getting trips:", error);
    throw error;
  }
};

export const updateTrip = (id, updatedData) => {
  const tripDoc = doc(db, "trips", id);
  return updateDoc(tripDoc, updatedData);
};

export const deleteTrip = (id) => {
  const tripDoc = doc(db, "trips", id);
  return deleteDoc(tripDoc);
};

export const toggleTripSharing = (id, isShared) => {
  const tripDoc = doc(db, "trips", id);
  return updateDoc(tripDoc, { shared: isShared });
};