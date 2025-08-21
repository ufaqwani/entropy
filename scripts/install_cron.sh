#!/bin/bash
echo "📦 Installing node-cron dependency..."

cd backend
npm install node-cron@^3.0.3

if [ $? -eq 0 ]; then
    echo "✅ node-cron installed successfully"
else
    echo "❌ Failed to install node-cron"
    echo "Please run manually: cd backend && npm install node-cron"
fi

cd ..