const cron = require('node-cron');
const axios = require('axios');

class TemplateScheduler {
    constructor() {
        this.isRunning = false;
    }
    
    start() {
        if (this.isRunning) {
            console.log('⏰ Template scheduler already running');
            return;
        }
        
        // Run every hour to check for pending templates
        this.job = cron.schedule('0 * * * *', async () => {
            try {
                console.log('⏰ Checking for pending templates...');
                
                const response = await axios.post('http://localhost:5000/api/templates/process-pending');
                
                if (response.data.processedCount > 0) {
                    console.log(`✅ Processed ${response.data.processedCount} template${response.data.processedCount !== 1 ? 's' : ''}`);
                    response.data.results.forEach(result => {
                        console.log(`   - ${result.template}: ${result.status}`);
                    });
                } else {
                    console.log('📋 No pending templates to process');
                }
                
            } catch (error) {
                console.error('❌ Error processing templates:', error.message);
            }
        });
        
        // Also run immediately at startup
        setTimeout(async () => {
            try {
                console.log('🚀 Processing templates at startup...');
                const response = await axios.post('http://localhost:5000/api/templates/process-pending');
                console.log(`✅ Startup processing complete: ${response.data.processedCount} template${response.data.processedCount !== 1 ? 's' : ''} processed`);
            } catch (error) {
                console.error('❌ Startup template processing failed:', error.message);
            }
        }, 5000); // Wait 5 seconds for server to be ready
        
        this.isRunning = true;
        console.log('⏰ Template scheduler started - checking every hour');
    }
    
    stop() {
        if (this.job) {
            this.job.stop();
            this.isRunning = false;
            console.log('⏰ Template scheduler stopped');
        }
    }
}

module.exports = new TemplateScheduler();