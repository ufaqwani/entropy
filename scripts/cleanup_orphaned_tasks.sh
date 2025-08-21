#!/bin/bash
echo "🧹 ENTROPY - Data Cleanup for Tomorrow Task Fix"
echo "=============================================="
echo ""
echo "This script will clean up any orphaned tasks that might cause the reappearing bug."
echo ""

read -p "Do you want to run the cleanup? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo "🔄 Running database cleanup..."

# Method 1: Using mongosh (MongoDB 5.0+)
if command -v mongosh >/dev/null 2>&1; then
    echo "Using mongosh..."
    mongosh entropy --eval "
        // Remove orphaned moved tasks that might reappear
        const result1 = db.tasks.deleteMany({
            moved: true,
            date: { \$lt: new Date(new Date().setHours(0,0,0,0)) }
        });
        print('🗑️  Removed ' + result1.deletedCount + ' old moved tasks');
        
        // Clean up any tasks marked as deleted
        const result2 = db.tasks.deleteMany({ deleted: true });
        print('🗑️  Removed ' + result2.deletedCount + ' deleted tasks');
        
        // Show remaining task counts
        const todayStart = new Date();
        todayStart.setHours(0,0,0,0);
        const tomorrow = new Date(todayStart);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        const todayCount = db.tasks.countDocuments({
            date: { \$gte: todayStart, \$lt: tomorrow },
            moved: { \$ne: true },
            deleted: { \$ne: true }
        });
        
        const tomorrowCount = db.tasks.countDocuments({
            date: { \$gte: tomorrow },
            deleted: { \$ne: true }
        });
        
        print('📊 Today tasks: ' + todayCount);
        print('📊 Tomorrow tasks: ' + tomorrowCount);
    "
# Method 2: Using legacy mongo client
elif command -v mongo >/dev/null 2>&1; then
    echo "Using legacy mongo client..."
    mongo entropy --eval "
        var result1 = db.tasks.deleteMany({
            moved: true,
            date: { \$lt: new Date(new Date().setHours(0,0,0,0)) }
        });
        print('🗑️  Removed ' + result1.deletedCount + ' old moved tasks');
        
        var result2 = db.tasks.deleteMany({ deleted: true });
        print('🗑️  Removed ' + result2.deletedCount + ' deleted tasks');
        
        print('📊 Today tasks: ' + db.tasks.count({
            date: { \$gte: new Date(new Date().setHours(0,0,0,0)) },
            moved: { \$ne: true },
            deleted: { \$ne: true }
        }));
    "
else
    echo "❌ MongoDB client not found!"
    echo "Please clean up manually or install mongosh/mongo client"
    exit 1
fi

echo ""
echo "✅ Cleanup complete!"
echo "🚀 Restart your app: ./start.sh"