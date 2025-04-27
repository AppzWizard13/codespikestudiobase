from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import atexit
import requests  # Make sure to import requests

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Updated self_ping function to ping multiple URLs
def self_ping():
    """
    Function to send GET requests to self-ping multiple server endpoints.
    """
    ping_urls = [
        'https://xxsapequipments.onrender.com/',
        'https://aspinxp.onrender.com/'
    ]
    
    for url in ping_urls:
        try:
            response = requests.get(url)
            print(f"Pinging URL: {url}")
            if response.status_code == 200:
                logger.info(f"Self-ping successful! URL: {url}")
            else:
                logger.warning(f"Self-ping failed for {url} with status code {response.status_code}")
        except Exception as e:
            logger.error(f"Error during self-ping to {url}: {e}")

# Function to start the scheduler
def start():
    scheduler = BackgroundScheduler()

    # Add self-ping to the scheduler, for example, every 15 seconds
    scheduler.add_job(self_ping, IntervalTrigger(seconds=15))  # Self-ping every 15 seconds
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started.")

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

# Call start() to run the scheduler
if __name__ == "__main__":
    start()




