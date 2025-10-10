#!/bin/bash

# SimpliTrip - Image Setup Script
# This script helps you download and organize destination images

echo "🖼️  SimpliTrip Image Setup"
echo "=========================="
echo ""

# Create directories
echo "📁 Creating image directories..."
mkdir -p simplitrip/public/images/destinations
mkdir -p simplitrip/public/images/places
mkdir -p simplitrip/public/images/temp

echo "✅ Directories created!"
echo ""

# Popular Indian destinations
destinations=(
    "goa-beach"
    "manali-himachal"
    "jaipur-rajasthan"
    "kerala-backwaters"
    "ladakh-mountains"
    "udaipur-palace"
    "varanasi-ganges"
    "rishikesh-yoga"
    "agra-taj-mahal"
    "mumbai-gateway"
    "delhi-india-gate"
    "bangalore-garden-city"
    "kolkata-victoria"
    "chennai-marina-beach"
    "hyderabad-charminar"
)

echo "🌍 Downloading images for ${#destinations[@]} destinations..."
echo ""

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "⚠️  ImageMagick not found. Images won't be optimized."
    echo "   Install with: brew install imagemagick (macOS)"
    echo ""
    OPTIMIZE=false
else
    OPTIMIZE=true
    echo "✅ ImageMagick found - images will be optimized"
    echo ""
fi

# Download counter
count=0

# Download images
for dest in "${destinations[@]}"; do
    count=$((count + 1))
    filename=$(echo "$dest" | cut -d'-' -f1)
    
    echo "[$count/${#destinations[@]}] Downloading $filename..."
    
    # Download from Unsplash
    curl -s -o "simplitrip/public/images/temp/$filename.jpg" \
        "https://source.unsplash.com/800x600/?$dest,india,travel"
    
    if [ $? -eq 0 ]; then
        if [ "$OPTIMIZE" = true ]; then
            # Optimize image
            convert "simplitrip/public/images/temp/$filename.jpg" \
                -resize 800x600 \
                -quality 85 \
                "simplitrip/public/images/destinations/$filename.jpg"
            echo "   ✅ Downloaded and optimized: $filename.jpg"
        else
            # Just move without optimization
            mv "simplitrip/public/images/temp/$filename.jpg" \
                "simplitrip/public/images/destinations/$filename.jpg"
            echo "   ✅ Downloaded: $filename.jpg"
        fi
    else
        echo "   ❌ Failed to download: $filename"
    fi
    
    # Small delay to avoid rate limiting
    sleep 1
done

# Clean up temp directory
rm -rf simplitrip/public/images/temp

echo ""
echo "🎉 Image setup complete!"
echo ""
echo "📊 Summary:"
echo "   - Destination images: $(ls simplitrip/public/images/destinations/*.jpg 2>/dev/null | wc -l)"
echo "   - Location: simplitrip/public/images/destinations/"
echo ""
echo "📝 Next steps:"
echo "   1. Review images in: simplitrip/public/images/destinations/"
echo "   2. Update your dataset CSV with image paths"
echo "   3. Restart the backend to load new data"
echo ""
echo "💡 Tip: You can replace any image with your own photos!"
echo "   Just name them: goa.jpg, manali.jpg, etc."
echo ""
