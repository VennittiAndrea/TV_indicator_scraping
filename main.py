import os 
import ast
import time
import logging
from dataclasses import dataclass


from src.TV.src.tradingview import TradingView
from src.utils.src import config_read, log_setup, sys_env_read

asset = 'OANDA:EURUSD'

def run(headless=False):
    # Create a directory for logs, if it doesn't exist
    current_dir = os.path.dirname(os.path.abspath(__file__)) # execution independent execution directory, reference is the main
    #
    # Read environment variables
    sys_env_read.load_dotenv(os.path.join(current_dir, 'config', '.env'))
    try: 
        log_level = os.getenv('LOG_LEVEL')
    except:
        log_level = 'INFO'
    #
    # Setup logging 
    log_setup.setupLogging(current_dir, log_level)
    logger = logging.getLogger(__name__)
    logger.info('----- New start -----')
    #
    # Read configuration parameters
    config_dict = config_read.read_config(current_dir)
    [asset, adv_url, indicators_name, thread_time] = config_dict['PARAMS'].values()
    indicators_name = ast.literal_eval(indicators_name)    
    print('ok') # while waiting tv data reading threaad
    # 
    #
    #
    tv = TradingView(username = os.getenv('USERNAME'), password = os.getenv('PASSWORD'), adv_url = adv_url, asset = asset)
    tv.run(adv_url, indicators_name, int(thread_time))



if __name__ == "__main__": 
    run()