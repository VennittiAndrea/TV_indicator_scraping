import os 
import logging
from dataclasses import dataclass


from src.TV.src.tradingview import TradingView
from src.utils.src import config_read, log_setup, sys_env_read

asset = 'OANDA:EURUSD'

# Set parameters as immutable
@dataclass(frozen=True)
class Params:
    adv_url: str
    indicator_name: list

def run(headless=False):
    # Create a directory for logs, if it doesn't exist
    current_dir = os.path.dirname(os.path.abspath(__file__)) # execution independent execution directory, reference is the main
    #
    # Read environment variables
    sys_env_read.load_dotenv(os.path.join(current_dir, 'config', '.env'))
    #
    # Setup logging 
    log_setup.setupLogging(current_dir)
    logger = logging.getLogger(__name__)
    logger.info('----- New start -----')
    #
    # Read configuration parameters
    config_dict = config_read.read_config(current_dir)
    info = Params(**config_dict['INFO'])
    # 
    #
    #
    tv = TradingView(username = os.getenv('USERNAME'), password = os.getenv('PASSWORD'), adv_url = info.adv_url)
    tv.load_chart_with_cookies()
    tv.get_layout(info.adv_url)
    tv.get_multi_components(info.indicators_name)
    print(tv.data_dict)
    tv.end()


if __name__ == "__main__": 
    run()