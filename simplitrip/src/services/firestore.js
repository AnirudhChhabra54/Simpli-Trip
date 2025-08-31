import { collection, addDoc, getDocs, doc, updateDoc, deleteDoc, query, where } from "firebase/firestore";
import { db } from "./firebase";

const tripsCollectionRef = collection(db, "trips");

export const addTrip = (tripData) => {
  return addDoc(tripsCollectionRef, tripData);
};

export const getTripsByUserId = async (userId) => {
  const q = query(tripsCollectionRef, where("userId", "==", userId));
  const querySnapshot = await getDocs(q);
  const trips = [];
  querySnapshot.forEach((doc) => {
    trips.push({ id: doc.id, ...doc.data() });
  });
  return trips;
};

export const updateTrip = (id, updatedData) => {
  const tripDoc = doc(db, "trips", id);
  return updateDoc(tripDoc, updatedData);
};

export const deleteTrip = (id) => {
  const tripDoc = doc(db, "trips", id);
  return deleteDoc(tripDoc);
};

// New function to make a trip shareable
export const toggleTripSharing = (id, isShared) => {
  const tripDoc = doc(db, "trips", id);
  return updateDoc(tripDoc, { isShared });
};