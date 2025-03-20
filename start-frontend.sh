#!/bin/bash

cd /home/humura/NexaSec/frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    npm install
fi

# Start the development server
npm run dev 