// Connect to MongoDB and cleanup ghost tasks
const { MongoClient } = require('mongodb');

async function cleanupGhostTasks() {
    const client = new MongoClient('mongodb://localhost:27017');
    
    try {
        await client.connect();
        const db = client.db('entropy');
        
        // Delete all moved tasks (ghosts)
        const result = await db.collection('tasks').deleteMany({ moved: true });
        
        console.log(`✅ Cleaned up ${result.deletedCount} ghost tasks`);
        
    } catch (error) {
        console.error('❌ Error cleaning up:', error.message);
    } finally {
        await client.close();
    }
}

cleanupGhostTasks();
