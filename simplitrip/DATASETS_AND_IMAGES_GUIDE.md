# SimpliTrip - Datasets & Images Guide

This guide explains how to add datasets for training ML models and images for displaying destinations.

---

## Part 1: Adding Datasets for Training

### Option A: Using Kaggle Datasets (Recommended)

#### Step 1: Set Up Kaggle API

1. **Create Kaggle Account**
   - Go to https://www.kaggle.com
   - Sign up or log in

2. **Get API Credentials**
   - Go to https://www.kaggle.com/settings
   - Scroll to "API" section
   - Click "Create New API Token"
   - This downloads `kaggle.json`

3. **Install Kaggle Credentials**
   ```bash
   # Create .kaggle directory
   mkdir -p ~/.kaggle
   
   # Move the downloaded file
   mv ~/Downloads/kaggle.json ~/.kaggle/
   
   # Set permissions
   chmod 600 ~/.kaggle/kaggle.json
   ```

4. **Verify Installation**
   ```bash
   kaggle datasets list
   ```

#### Step 2: Download Datasets Automatically

The backend has a built-in script to download all required datasets:

```bash
cd simplitrip/backend
source venv/bin/activate
python scripts/download_datasets.py
```

This will download:
1. **Explore India Tourist Destinations** (156 destinations)
2. **Famous Indian Tourist Places** (325 places)
3. **Airline Ticket Prices** (5M+ flight records)
4. **TripAdvisor Hotel Reviews** (11,800 reviews)
5. **Travel Tales India** (3,300+ travelogues)

**Download Location**: `simplitrip/backend/data/downloads/`

#### Step 3: Process Datasets

After downloading, process the raw data:

```bash
cd simplitrip/backend
python -c "from utils.data_loader import DataLoader; loader = DataLoader(); loader.load_all_datasets()"
```

**Processed Location**: `simplitrip/backend/data/processed/`

---

### Option B: Manual Dataset Addition

If you have your own datasets or want to add custom data:

#### 1. Create CSV Files

**Destinations Dataset** (`destinations.csv`):
```csv
destination_name,state,category,rating,best_time_to_visit,description,latitude,longitude
Goa,Goa,Beach,4.5,November-February,Beautiful beaches and nightlife,15.2993,74.1240
Manali,Himachal Pradesh,Mountain,4.7,October-June,Scenic hill station,32.2396,77.1887
Jaipur,Rajasthan,Historical,4.6,October-March,Pink city with forts,26.9124,75.7873
```

**Places Dataset** (`places.csv`):
```csv
place_name,destination,category,visit_duration,rating,description
Baga Beach,Goa,Beach,3,4.5,Popular beach with water sports
Calangute Beach,Goa,Beach,2,4.3,Largest beach in North Goa
Fort Aguada,Goa,Historical,2,4.4,17th century Portuguese fort
```

**Flight Prices Dataset** (`flight_prices.csv`):
```csv
date,from,to,airline,base_price,departure_time,arrival_time
2024-06-15,Mumbai,Goa,IndiGo,3500,08:00,09:30
2024-06-15,Delhi,Goa,Air India,5200,10:00,12:45
```

#### 2. Place Files in Data Directory

```bash
# Create directories if they don't exist
mkdir -p simplitrip/backend/data/raw

# Copy your CSV files
cp destinations.csv simplitrip/backend/data/raw/
cp places.csv simplitrip/backend/data/raw/
cp flight_prices.csv simplitrip/backend/data/raw/
```

#### 3. Update Data Loader

The data loader will automatically detect and use these files.

---

### Option C: Using Database

For production, you can use a database instead of CSV files:

#### 1. Set Up PostgreSQL

```bash
# Install PostgreSQL
brew install postgresql  # macOS
# or
sudo apt-get install postgresql  # Linux

# Start PostgreSQL
brew services start postgresql  # macOS
# or
sudo service postgresql start  # Linux
```

#### 2. Create Database

```sql
CREATE DATABASE simplitrip;

CREATE TABLE destinations (
    id SERIAL PRIMARY KEY,
    destination_name VARCHAR(255),
    state VARCHAR(100),
    category VARCHAR(50),
    rating DECIMAL(2,1),
    best_time_to_visit VARCHAR(100),
    description TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    image_url TEXT
);

CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    place_name VARCHAR(255),
    destination VARCHAR(255),
    category VARCHAR(50),
    visit_duration INTEGER,
    rating DECIMAL(2,1),
    description TEXT,
    image_url TEXT
);
```

#### 3. Import Data

```bash
# Import CSV to PostgreSQL
psql -d simplitrip -c "\COPY destinations FROM 'destinations.csv' CSV HEADER"
psql -d simplitrip -c "\COPY places FROM 'places.csv' CSV HEADER"
```

#### 4. Update Backend Configuration

Edit `simplitrip/backend/config/settings.py`:

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/simplitrip"
```

---

## Part 2: Adding Images for Destinations

### Option A: Using Unsplash API (Current Implementation)

The app currently uses Unsplash's free image service:

```javascript
// In DestinationCard.js
const imageUrl = image_url || `https://source.unsplash.com/800x600/?${destination_name},india,travel`;
```

**Pros**: 
- Free
- No setup required
- High-quality images
- Automatic based on destination name

**Cons**:
- Requires internet
- Random images (may not be exact location)

---

### Option B: Local Image Storage

#### 1. Create Images Directory

```bash
mkdir -p simplitrip/public/images/destinations
mkdir -p simplitrip/public/images/places
```

#### 2. Add Images

Download or add images with naming convention:

```
simplitrip/public/images/destinations/
├── goa.jpg
├── manali.jpg
├── jaipur.jpg
├── kerala.jpg
└── ...

simplitrip/public/images/places/
├── baga-beach.jpg
├── taj-mahal.jpg
├── gateway-of-india.jpg
└── ...
```

**Image Requirements**:
- Format: JPG, PNG, or WebP
- Size: 800x600px (recommended)
- File size: < 500KB (optimized)
- Naming: lowercase, hyphen-separated

#### 3. Update Dataset with Image Paths

Add `image_url` column to your CSV:

```csv
destination_name,state,category,rating,image_url
Goa,Goa,Beach,4.5,/images/destinations/goa.jpg
Manali,Himachal Pradesh,Mountain,4.7,/images/destinations/manali.jpg
```

#### 4. Update Component

The `DestinationCard` component will automatically use local images if provided:

```javascript
// Already implemented in DestinationCard.js
const imageUrl = image_url || `https://source.unsplash.com/800x600/?${destination_name},india,travel`;
```

---

### Option C: Cloud Storage (Firebase Storage)

#### 1. Set Up Firebase Storage

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase Storage
firebase init storage
```

#### 2. Upload Images

```bash
# Upload images to Firebase Storage
firebase deploy --only storage
```

Or use the Firebase Console:
1. Go to https://console.firebase.google.com
2. Select your project
3. Go to Storage
4. Create folder: `destinations/`
5. Upload images

#### 3. Get Image URLs

After uploading, get the download URLs:

```javascript
import { getStorage, ref, getDownloadURL } from 'firebase/storage';

const storage = getStorage();
const imageRef = ref(storage, 'destinations/goa.jpg');
const url = await getDownloadURL(imageRef);
```

#### 4. Update Dataset

Add Firebase URLs to your dataset:

```csv
destination_name,image_url
Goa,https://firebasestorage.googleapis.com/v0/b/simplitrip.appspot.com/o/destinations%2Fgoa.jpg?alt=media
```

---

### Option D: CDN (Cloudinary)

#### 1. Create Cloudinary Account

- Go to https://cloudinary.com
- Sign up for free account
- Get your cloud name, API key, and secret

#### 2. Upload Images

Using Cloudinary Dashboard:
1. Go to Media Library
2. Upload images
3. Organize in folders: `simplitrip/destinations/`

#### 3. Get Image URLs

Cloudinary provides optimized URLs:

```
https://res.cloudinary.com/your-cloud-name/image/upload/v1234567890/simplitrip/destinations/goa.jpg
```

#### 4. Add to Dataset

```csv
destination_name,image_url
Goa,https://res.cloudinary.com/your-cloud-name/image/upload/simplitrip/destinations/goa.jpg
```

**Benefits**:
- Automatic optimization
- Responsive images
- Transformations (resize, crop, etc.)
- CDN delivery

---

## Part 3: Training ML Models

### Step 1: Prepare Training Data

Ensure datasets are in `simplitrip/backend/data/processed/`:

```bash
ls simplitrip/backend/data/processed/
# Should show:
# - destinations.csv
# - places.csv
# - flight_prices.csv
# - hotel_reviews.csv
# - travelogues.csv
```

### Step 2: Train Models

```bash
cd simplitrip/backend
source venv/bin/activate
python scripts/train_models.py
```

This will:
1. Load processed datasets
2. Train recommendation model
3. Train cost prediction model
4. Train itinerary optimizer
5. Save models to `backend/models/saved_models/`

### Step 3: Verify Training

Check the logs:

```bash
tail -f simplitrip/backend/logs/app.log
```

Look for:
- "Training recommendation model..."
- "Training cost prediction model..."
- "Models saved successfully"

### Step 4: Test Models

```bash
# Test recommendation model
curl -X POST http://localhost:8000/api/v1/recommendations/destinations \
  -H "Content-Type: application/json" \
  -d '{"preferences": {"budget": 50000, "categories": ["Beach"]}, "top_n": 5}'

# Test cost prediction
curl -X POST http://localhost:8000/api/v1/predictions/total-cost \
  -H "Content-Type: application/json" \
  -d '{"destination": "Goa", "travelers": 2, "days": 5}'
```

---

## Part 4: Image Optimization Tips

### 1. Compress Images

```bash
# Install ImageMagick
brew install imagemagick  # macOS

# Compress images
mogrify -resize 800x600 -quality 85 *.jpg
```

### 2. Convert to WebP

```bash
# Convert to WebP (better compression)
for img in *.jpg; do
  cwebp -q 80 "$img" -o "${img%.jpg}.webp"
done
```

### 3. Lazy Loading

Already implemented in `DestinationCard.js`:

```javascript
<motion.img
  src={imageUrl}
  alt={destination_name}
  loading="lazy"  // Lazy load images
  className="w-full h-full object-cover"
/>
```

---

## Part 5: Complete Example Workflow

### Example: Adding Goa with Images

#### 1. Download Goa Image

```bash
# Download from Unsplash
curl -o goa.jpg "https://source.unsplash.com/800x600/?goa,beach,india"

# Or use your own image
```

#### 2. Optimize Image

```bash
# Resize and compress
convert goa.jpg -resize 800x600 -quality 85 goa-optimized.jpg

# Move to public directory
mv goa-optimized.jpg simplitrip/public/images/destinations/goa.jpg
```

#### 3. Add to Dataset

Create/update `destinations.csv`:

```csv
destination_name,state,category,rating,best_time_to_visit,description,image_url
Goa,Goa,Beach,4.5,November-February,Beautiful beaches and Portuguese heritage,/images/destinations/goa.jpg
```

#### 4. Add Places for Goa

Create/update `places.csv`:

```csv
place_name,destination,category,visit_duration,rating,description,image_url
Baga Beach,Goa,Beach,3,4.5,Popular beach with water sports,/images/places/baga-beach.jpg
Calangute Beach,Goa,Beach,2,4.3,Largest beach in North Goa,/images/places/calangute-beach.jpg
Fort Aguada,Goa,Historical,2,4.4,17th century Portuguese fort,/images/places/fort-aguada.jpg
```

#### 5. Load Data

```bash
cd simplitrip/backend
python -c "from utils.data_loader import DataLoader; loader = DataLoader(); loader.load_all_datasets()"
```

#### 6. Train Models

```bash
python scripts/train_models.py
```

#### 7. Restart Backend

```bash
# Stop current backend (Ctrl+C)
# Restart
python main.py
```

#### 8. Test in Frontend

1. Open http://localhost:3000
2. Login
3. Click "AI Trip Planner"
4. Enter: "Plan a beach vacation to Goa"
5. See Goa with your custom image!

---

## Part 6: Bulk Image Addition

### Script to Download Multiple Images

Create `download_images.sh`:

```bash
#!/bin/bash

# List of destinations
destinations=(
  "goa"
  "manali"
  "jaipur"
  "kerala"
  "ladakh"
  "udaipur"
  "varanasi"
  "rishikesh"
)

# Download images
for dest in "${destinations[@]}"; do
  echo "Downloading image for $dest..."
  curl -o "$dest.jpg" "https://source.unsplash.com/800x600/?$dest,india,travel"
  
  # Optimize
  convert "$dest.jpg" -resize 800x600 -quality 85 "optimized/$dest.jpg"
done

echo "Done! Images saved to optimized/"
```

Run:

```bash
chmod +x download_images.sh
./download_images.sh
```

---

## Part 7: Database Schema with Images

### Complete Schema

```sql
CREATE TABLE destinations (
    id SERIAL PRIMARY KEY,
    destination_name VARCHAR(255) NOT NULL,
    state VARCHAR(100),
    category VARCHAR(50),
    rating DECIMAL(2,1),
    best_time_to_visit VARCHAR(100),
    description TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    image_url TEXT,
    thumbnail_url TEXT,
    gallery_urls TEXT[],  -- Array of image URLs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    place_name VARCHAR(255) NOT NULL,
    destination_id INTEGER REFERENCES destinations(id),
    category VARCHAR(50),
    visit_duration INTEGER,
    rating DECIMAL(2,1),
    description TEXT,
    image_url TEXT,
    thumbnail_url TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX idx_destinations_category ON destinations(category);
CREATE INDEX idx_destinations_state ON destinations(state);
CREATE INDEX idx_places_destination ON places(destination_id);
```

---

## Summary

### Quick Start Checklist

**For Datasets:**
- [ ] Set up Kaggle API credentials
- [ ] Run `python scripts/download_datasets.py`
- [ ] Verify data in `backend/data/downloads/`
- [ ] Train models with `python scripts/train_models.py`

**For Images:**
- [ ] Choose storage method (Unsplash/Local/Firebase/Cloudinary)
- [ ] Create `public/images/destinations/` directory
- [ ] Add images with proper naming
- [ ] Update dataset with image URLs
- [ ] Restart backend to load new data

**Testing:**
- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:3000
- [ ] Test API endpoints
- [ ] Verify images display correctly
- [ ] Check recommendations work

---

## Troubleshooting

### Issue: Images Not Loading

**Solution 1**: Check image path
```javascript
// Correct
image_url: "/images/destinations/goa.jpg"

// Incorrect
image_url: "images/destinations/goa.jpg"  // Missing leading slash
```

**Solution 2**: Verify file exists
```bash
ls simplitrip/public/images/destinations/
```

**Solution 3**: Check browser console for 404 errors

### Issue: Datasets Not Loading

**Solution 1**: Check file format
```bash
# Verify CSV format
head -n 5 simplitrip/backend/data/raw/destinations.csv
```

**Solution 2**: Check logs
```bash
tail -f simplitrip/backend/logs/app.log
```

**Solution 3**: Verify data loader
```bash
cd simplitrip/backend
python -c "from utils.data_loader import DataLoader; loader = DataLoader(); print(loader.destinations.head())"
```

---

## Resources

- **Kaggle Datasets**: https://www.kaggle.com/datasets
- **Unsplash API**: https://unsplash.com/developers
- **Firebase Storage**: https://firebase.google.com/docs/storage
- **Cloudinary**: https://cloudinary.com/documentation
- **Image Optimization**: https://imagemagick.org

---

**Need Help?** Check the logs or create an issue on GitHub!
