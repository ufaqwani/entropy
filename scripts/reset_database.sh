#!/bin/bash
echo "🗃️  Resetting ENTROPY Database..."
echo "⚠️  This will delete ALL tasks and progress data!"
echo ""

read -p "Are you sure? Type 'yes' to continue: " confirm
if [ "$confirm" != "yes" ]; then
    echo "Reset cancelled."
    exit 0
fi

echo "🔄 Clearing MongoDB collections..."

# Method 1: Using mongosh (MongoDB 5.0+)
if command -v mongosh >/dev/null 2>&1; then
    echo "Using mongosh..."
    mongosh entropy --eval "
        db.tasks.deleteMany({});
        db.progresses.deleteMany({});
        print('✅ All tasks and progress deleted');
        print('📊 Remaining tasks: ' + db.tasks.countDocuments());
        print('📊 Remaining progress: ' + db.progresses.countDocuments());
    "
# Method 2: Using legacy mongo client
elif command -v mongo >/dev/null 2>&1; then
    echo "Using legacy mongo client..."
    mongo entropy --eval "
        db.tasks.deleteMany({});
        db.progresses.deleteMany({});
        print('✅ All tasks and progress deleted');
        print('📊 Remaining tasks: ' + db.tasks.count());
        print('📊 Remaining progress: ' + db.progresses.count());
    "
else
    echo "❌ MongoDB client not found!"
    echo "Please install mongosh or legacy mongo client"
    echo "Or manually delete collections in MongoDB Compass"
    exit 1
fi

echo ""
echo "✅ Database reset complete!"
echo "🚀 Restart your app to begin fresh: ./start.sh"