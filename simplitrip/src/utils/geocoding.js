export const resolveCoordinates = async (placeName) => {
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(placeName)}&limit=1`);
        if (!response.ok) throw new Error("Nominatim fetch failed");
        const data = await response.json();
        if (data && data.length > 0) {
            return {
                lat: parseFloat(data[0].lat),
                lon: parseFloat(data[0].lon)
            };
        }
    } catch (error) {
        console.error("Error geocoding location:", error);
    }
    return null;
};
