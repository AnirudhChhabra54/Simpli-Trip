# 📊 Data Feeding Guide - How to Add Data to Your RAG System

## 🎯 Overview

Your RAG (Retrieval-Augmented Generation) system stores data in a **vector database (ChromaDB)** that the LLM uses to answer questions. This guide shows you exactly where and how to feed data.

---

## 📍 Where Data is Stored

**Location:** `simplitrip/backend/data/chromadb/`

**What's stored:**
- Text chunks (your travel information)
- Vector embeddings (mathematical representations)
- Metadata (destination, category, source, etc.)

**Important:** You don't need to train anything! Data is instantly searchable once added.

---

## 🚀 5 Ways to Feed Data

### **Method 1: Interactive Script (Easiest)**

```bash
cd simplitrip/backend
python scripts/add_data_to_rag.py
```

**Menu options:**
1. Plain text - Type or paste text directly
2. Text file - Upload .txt files
3. CSV file - Bulk upload from spreadsheet
4. JSON file - Structured data upload
5. PDF file - Extract and add PDF content
6. Travel destination - Guided destination info entry

**Example session:**
```
What type of data do you want to add?
> 6 (Travel destination info)

Destination name: Goa
Description: Beautiful beaches, nightlife, Portuguese heritage
Best time to visit: November to February
Attractions: Baga Beach, Fort Aguada, Dudhsagar Falls
Travel tips: Try local seafood, visit beach shacks

✅ Added destination: Goa
```

---

### **Method 2: Python Code (Programmatic)**

**Simple text:**
```python
from services.rag_service import rag_service

rag_service.add_document(
    text="Goa is a beautiful beach destination in India with stunning coastline.",
    metadata={
        "destination": "Goa",
        "category": "beach",
        "best_time": "November-February"
    }
)
```

**From file:**
```python
with open('travel_guide.txt', 'r') as f:
    text = f.read()
    rag_service.add_document(
        text=text,
        metadata={"source": "travel_guide.txt", "type": "guide"}
    )
```

---

### **Method 3: CSV Files**

**Step 1: Create CSV file** (`destinations.csv`)
```csv
destination,description,best_time,category
Goa,Beautiful beaches and nightlife,November-February,beach
Jaipur,Pink city with historical forts,October-March,historical
Kerala,Backwaters and lush greenery,September-March,nature
Ladakh,High altitude desert mountains,May-September,adventure
```

**Step 2: Add to RAG**
```python
from scripts.add_data_to_rag import add_csv_data

add_csv_data(
    csv_path="destinations.csv",
    text_column="description",
    metadata_columns=["destination", "best_time", "category"]
)
```

**Or via command line:**
```bash
python -c "from scripts.add_data_to_rag import add_csv_data; add_csv_data('destinations.csv', 'description', ['destination', 'category'])"
```

---

### **Method 4: JSON Files**

**Step 1: Create JSON file** (`destinations.json`)
```json
[
  {
    "destination": "Goa",
    "description": "Goa is famous for its pristine beaches, vibrant nightlife, and Portuguese colonial architecture. Popular beaches include Baga, Calangute, and Anjuna.",
    "best_time": "November-February",
    "category": "beach",
    "attractions": ["Baga Beach", "Fort Aguada", "Dudhsagar Falls"],
    "budget": "moderate"
  },
  {
    "destination": "Jaipur",
    "description": "The Pink City of India, known for magnificent forts, palaces, and rich Rajasthani culture. Must-visit places include Hawa Mahal and Amber Fort.",
    "best_time": "October-March",
    "category": "historical",
    "attractions": ["Hawa Mahal", "Amber Fort", "City Palace"],
    "budget": "moderate"
  }
]
```

**Step 2: Add to RAG**
```python
from scripts.add_data_to_rag import add_json_data

add_json_data(
    json_path="destinations.json",
    text_field="description",
    metadata_fields=["destination", "best_time", "category", "budget"]
)
```

---

### **Method 5: PDF Files**

**Requirements:**
```bash
pip install PyPDF2
```

**Add PDF:**
```python
from scripts.add_data_to_rag import add_pdf_file

add_pdf_file(
    pdf_path="india_travel_guide.pdf",
    metadata={"type": "guide", "source": "official_tourism"}
)
```

**Note:** PDF text is automatically extracted and added to RAG.

---

## 📂 Recommended Folder Structure

```
simplitrip/backend/data/
├── raw/                          # Your original data files
│   ├── destinations.csv          # Destination database
│   ├── travel_guides/            # PDF guides
│   │   ├── goa_guide.pdf
│   │   ├── rajasthan_guide.pdf
│   │   └── kerala_guide.pdf
│   ├── tips.json                 # Travel tips
│   └── attractions.txt           # Attraction descriptions
│
├── processed/                    # Cleaned/processed data (optional)
│   └── cleaned_destinations.csv
│
└── chromadb/                     # Vector database (auto-created)
    └── [ChromaDB files]
```

---

## 💡 Practical Examples

### **Example 1: Add Single Destination**

```python
from scripts.add_data_to_rag import add_travel_destination

add_travel_destination(
    destination="Goa",
    description="Goa is India's smallest state, famous for its stunning beaches, vibrant nightlife, Portuguese heritage, and water sports. The state offers a perfect blend of relaxation and adventure.",
    best_time="November to February (winter season)",
    attractions=[
        "Baga Beach - Popular for water sports",
        "Fort Aguada - 17th century Portuguese fort",
        "Dudhsagar Falls - Majestic four-tiered waterfall",
        "Old Goa Churches - UNESCO World Heritage Sites",
        "Anjuna Flea Market - Shopping and local culture"
    ],
    tips="Try Goan seafood, visit beach shacks, rent a scooter for exploring, book accommodations in advance during peak season"
)
```

### **Example 2: Bulk Add Multiple Destinations**

```python
from scripts.add_data_to_rag import add_bulk_destinations

destinations = [
    {
        "name": "Goa",
        "description": "Beach paradise with Portuguese heritage...",
        "best_time": "November-February",
        "attractions": ["Baga Beach", "Fort Aguada"],
        "tips": "Try local seafood"
    },
    {
        "name": "Jaipur",
        "description": "Pink city with magnificent forts...",
        "best_time": "October-March",
        "attractions": ["Hawa Mahal", "Amber Fort"],
        "tips": "Visit early morning to avoid crowds"
    },
    {
        "name": "Kerala",
        "description": "God's own country with backwaters...",
        "best_time": "September-March",
        "attractions": ["Alleppey Backwaters", "Munnar Tea Gardens"],
        "tips": "Book houseboat in advance"
    }
]

add_bulk_destinations(destinations)
```

### **Example 3: Add from Text File**

**Create file:** `delhi_info.txt`
```
Delhi - The Capital of India

Delhi is a vibrant metropolis that seamlessly blends ancient history with modern development. The city is home to numerous UNESCO World Heritage Sites including the Red Fort, Qutub Minar, and Humayun's Tomb.

Best Time to Visit: October to March

Top Attractions:
- Red Fort: Iconic Mughal fortress
- India Gate: War memorial and popular picnic spot
- Qutub Minar: 73-meter tall victory tower
- Lotus Temple: Architectural marvel
- Chandni Chowk: Historic market for shopping and street food

Travel Tips:
- Use Delhi Metro for convenient travel
- Try street food in Old Delhi
- Book tickets online for monuments
- Carry water and sunscreen
```

**Add to RAG:**
```python
from scripts.add_data_to_rag import add_text_file

add_text_file(
    file_path="delhi_info.txt",
    metadata={
        "destination": "Delhi",
        "category": "historical",
        "type": "destination_guide"
    }
)
```

---

## 🔍 How RAG Uses Your Data

```
┌─────────────────┐
│  You Add Data   │
│  (Text/CSV/PDF) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Chunking   │
│ (500-1000 chars)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create Embeddings│
│ (Vector numbers) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Store in ChromaDB│
│ (Vector database)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User Asks Query │
│ "Best beaches?" │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Search Similar  │
│ (Vector search) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Retrieve Chunks │
│ (Top 5 matches) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Generates   │
│ Answer with     │
│ Retrieved Context│
└─────────────────┘
```

---

## 📊 Check Your Data

### **View Statistics**

```python
from services.rag_service import rag_service

stats = rag_service.get_collection_stats()
print(f"Total documents: {stats['count']}")
```

### **Search Your Data**

```python
# Search for beaches
results = rag_service.search("beaches in India", top_k=5)

for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result['score']:.2f}")
    print(f"   Text: {result['text'][:100]}...")
    print(f"   Metadata: {result['metadata']}")
```

### **Test with LLM**

```python
from services.model_service import model_service

answer = model_service.answer_with_rag("What are the best beaches in Goa?")
print(answer)
```

---

## 🎯 Best Practices

### **1. Add Metadata**
Always include relevant metadata:
```python
metadata = {
    "destination": "Goa",
    "category": "beach",
    "best_time": "November-February",
    "budget": "moderate",
    "source": "official_tourism_board"
}
```

### **2. Clean Your Text**
- Remove extra spaces and special characters
- Fix typos and formatting issues
- Use consistent naming (e.g., "Goa" not "GOA" or "goa")

### **3. Optimal Chunk Size**
- Keep text chunks between 500-1000 characters
- Each chunk should be self-contained
- Include context in each chunk

### **4. Update Regularly**
```python
# Add new destinations as they become popular
# Update seasonal information
# Add user-generated tips and reviews
```

### **5. Test Searches**
```python
# Always test that your data is retrievable
results = rag_service.search("your search query", top_k=3)
assert len(results) > 0, "Data not found!"
```

---

## 🛠️ Complete Workflow Example

```bash
# Step 1: Navigate to backend
cd simplitrip/backend

# Step 2: Create your data file
cat > my_destinations.csv << 'EOF'
destination,description,category,best_time
Goa,Beautiful beaches and nightlife,beach,November-February
Jaipur,Pink city with historical forts,historical,October-March
Kerala,Backwaters and lush nature,nature,September-March
Ladakh,High altitude mountain desert,adventure,May-September
EOF

# Step 3: Add to RAG
python << 'PYTHON'
from scripts.add_data_to_rag import add_csv_data
add_csv_data(
    'my_destinations.csv',
    'description',
    ['destination', 'category', 'best_time']
)
PYTHON

# Step 4: Verify data was added
python << 'PYTHON'
from services.rag_service import rag_service
stats = rag_service.get_collection_stats()
print(f"✅ Total documents: {stats['count']}")

# Test search
results = rag_service.search("beach destinations", top_k=3)
print(f"\n✅ Found {len(results)} results for 'beach destinations'")
for r in results:
    print(f"  - {r['metadata'].get('destination')}: {r['text'][:60]}...")
PYTHON

# Step 5: Test with LLM
python << 'PYTHON'
from services.model_service import model_service
answer = model_service.answer_with_rag("What are good beach destinations?")
print(f"\n✅ LLM Answer:\n{answer}")
PYTHON
```

---

## 📝 Quick Reference

| Task | Command |
|------|---------|
| **Interactive mode** | `python scripts/add_data_to_rag.py` |
| **Add text** | `rag_service.add_document(text, metadata)` |
| **Add CSV** | `add_csv_data('file.csv', 'text_col', ['meta_cols'])` |
| **Add JSON** | `add_json_data('file.json', 'text_field', ['meta_fields'])` |
| **Add PDF** | `add_pdf_file('file.pdf', metadata)` |
| **Check stats** | `rag_service.get_collection_stats()` |
| **Search** | `rag_service.search('query', top_k=5)` |
| **Ask LLM** | `model_service.answer_with_rag('question')` |

---

## 🚨 Troubleshooting

### **Issue: "Collection not found"**
```python
# Initialize RAG service first
from services.rag_service import rag_service
# It auto-initializes on import
```

### **Issue: "No results found"**
```python
# Check if data was added
stats = rag_service.get_collection_stats()
print(stats)  # Should show count > 0

# Try broader search
results = rag_service.search("India", top_k=10)
```

### **Issue: "PDF extraction failed"**
```bash
# Install PDF library
pip install PyPDF2

# Or use alternative
pip install pdfplumber
```

---

## ✨ Summary

**Where to feed data:**
- Interactive: `python scripts/add_data_to_rag.py`
- Code: `rag_service.add_document(text, metadata)`
- Files: CSV, JSON, PDF, TXT all supported

**Data location:**
- Stored in: `backend/data/chromadb/`
- No training needed!
- Instantly searchable

**Supported formats:**
- ✅ Plain text
- ✅ Text files (.txt)
- ✅ CSV files
- ✅ JSON files
- ✅ PDF files

**Next steps:**
1. Run: `cd simplitrip/backend && python scripts/add_data_to_rag.py`
2. Choose option 6 to add destination info
3. Test: `python test_ollama_rag.py`

Your RAG system is ready! Add your travel data and start asking questions. 🎉
