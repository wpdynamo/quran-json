#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Run the generation script
python3 generate_quran_bundle_with_indexes.py

# Copy generated files to public directory
mkdir -p public/assets/quran
cp -R assets/quran/* public/assets/quran/

echo "Build completed successfully!"
