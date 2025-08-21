#!/bin/bash
echo "📊 Installing Chart.js dependencies..."

cd frontend
npm install chart.js@^4.4.0 react-chartjs-2@^5.2.0

if [ $? -eq 0 ]; then
    echo "✅ Chart.js dependencies installed successfully"
else
    echo "❌ Failed to install Chart.js dependencies"
    echo "Please run manually: cd frontend && npm install chart.js react-chartjs-2"
fi

cd ..