from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import atexit
import requests  # Make sure to import requests

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Dummy self_ping function
def self_ping():
    """
    Function to send a GET request to self-ping the server.
    Adjust the URL to your actual endpoint.
    """
    try:
        response = requests.get('https://codespikestudio.onrender.com/')  # Replace with your actual URL
        if response.status_code == 200:
            logger.info("Self-ping successful!")
        else:
            logger.warning(f"Self-ping failed with status code {response.status_code}")
    except Exception as e:
        logger.error(f"Error during self-ping: {e}")

# Function to start the scheduler
def start():
    scheduler = BackgroundScheduler()

    # Add self-ping to the scheduler, for example, every 15 seconds
    # scheduler.add_job(self_ping, IntervalTrigger(seconds=15))  # Self-ping every 15 seconds
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started.")

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

# Call start() to run the scheduler
if __name__ == "__main__":
    start()
