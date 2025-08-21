#!/bin/bash
set -e

echo "🚀 Starting ENTROPY - Task Management App"
echo "========================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required dependencies
echo "📋 Checking system dependencies..."

if ! command_exists node; then
    echo "❌ Node.js is not installed. Installing via package manager..."
    if command_exists apt; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif command_exists yum; then
        curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
        sudo yum install -y nodejs
    elif command_exists pacman; then
        sudo pacman -S nodejs npm
    else
        echo "Please install Node.js 18+ manually from https://nodejs.org/"
        exit 1
    fi
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt "16" ]; then
    echo "❌ Node.js version 16+ is required. Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js $(node --version) found"
echo "✅ npm $(npm --version) found"

# MongoDB setup for Linux
if command_exists mongod; then
    echo "✅ MongoDB found"
    if ! pgrep -x "mongod" > /dev/null; then
        echo "🔄 Starting MongoDB..."
        sudo systemctl start mongod || mongod --fork --logpath /var/log/mongodb.log
    else
        echo "✅ MongoDB is already running"
    fi
else
    echo "⚠️  MongoDB not found. Installing..."
    if command_exists apt; then
        wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
        echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
        sudo apt update
        sudo apt install -y mongodb-org
        sudo systemctl start mongod
        sudo systemctl enable mongod
    else
        echo "Please install MongoDB manually or use MongoDB Atlas cloud service"
        echo "Update MONGODB_URI in backend/.env if using cloud service"
    fi
fi

echo ""
echo "📦 Installing dependencies..."

# Install backend dependencies
echo "🔧 Installing backend dependencies..."
cd backend
npm install

# Install frontend dependencies
echo "🔧 Installing frontend dependencies..."
cd ../frontend
npm install

cd ..

echo ""
echo "🚀 Starting the application..."

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down Entropy..."
    pkill -f "node.*server.js" || true
    pkill -f "react-scripts" || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend server in background
echo "🔥 Starting backend server on http://localhost:5000"
cd backend
npm run dev &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend server on http://localhost:3000"
cd ../frontend
PORT=3000 npm start &
FRONTEND_PID=$!

# Wait and try to open browser
sleep 5
if command_exists xdg-open; then
    xdg-open http://localhost:3000 >/dev/null 2>&1 &
fi

echo ""
echo "🎉 ENTROPY is now running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:5000"
echo "🏥 Health:   http://localhost:5000/health"
echo ""
echo "Press Ctrl+C to stop the servers"
echo ""

# Wait for background processes
wait