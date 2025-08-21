#!/bin/bash
echo "📦 Installing drag & drop dependencies..."

cd frontend
npm install @hello-pangea/dnd@^16.3.0

if [ $? -eq 0 ]; then
    echo "✅ Drag & drop dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    echo "Please run manually: cd frontend && npm install @hello-pangea/dnd"
fi

cd ..