#!/bin/bash

# Install Python dependencies and generate Quran data
pip install -r requirements.txt
python3 generate_quran_bundle_with_indexes.py

# Copy generated files to public directory (for Astro)
mkdir -p public/assets/quran
cp -R assets/quran/* public/assets/quran/

# Build Astro site
npm run build

echo "Build completed successfully!"
