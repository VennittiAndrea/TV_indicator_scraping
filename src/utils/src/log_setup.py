import os
import logging 

logger = logging.getLogger(__name__)

# Set up logging unit
def setupLogging(current_dir: str, log_level : str = 'DEBUG') -> None: 
    # Define logging file path
    log_dir = os.path.join(current_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file_path = os.path.join(log_dir, "ms.log")

    logging.basicConfig(
        filename= log_file_path,
        level= log_level.upper(),
        format='%(asctime)s - %(levelname)s - %(name)s - [%(funcName)s] --> %(message)s'
    )

