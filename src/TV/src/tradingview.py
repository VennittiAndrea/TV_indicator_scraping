'''NOTES
- Thread creation: take code from old data reading in discord app with websocket and threading
- Improve data manipulation and storing
- Devo vedere con che velocità posso andare ad estrarre i dati.
- Logging must be added
'''
import os 
import time 
import pickle 
import logging 
import threading

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pickle
import time
import os

LONG = 1.5
EXLONG = 3 # Extra long 
SHORT = 0.25
LOAD = 5


class TradingView:

    def __init__(self, options= None, headless: bool = False, username : str = None, password: str = None, adv_url: str = 'https://it.tradingview.com/chart/4FNrxQbz/?symbol=OANDA%3AEURUSD', asset : str = 'OANDA:EURUSD', dwnl_path : str = '../data/'):
        if username is None or password is None:
            print('No username or password')
            raise ImportError('No username or password')
        self.bsc_url = "https://tradingview.com"
        self.asset = asset
        self.adv_url = adv_url + asset
        self.username = username
        self.password = password
        self.data : dict = {}

        self.options = options
        self.headless = headless
        self.options_manager(dwnl_path)

    def options_manager(self, dwnl_path) -> None:
        # Initialize Chrome options
        chrome_options = webdriver.ChromeOptions()
        #
        if self.options is not None:
            chrome_options = self.options
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("detach", True)
        # Set download folder 
        prefs = {"download.default_directory": dwnl_path}
        chrome_options.add_experimental_option("prefs", prefs)
        #
        print('Initializing Chrome browser...')
        # Start Chrome browser
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def load_chart_with_cookies(self) -> None:
        self.driver.maximize_window()
        # First, navigate to the domain to set the cookies for the domain
        self.driver.get(self.bsc_url)

        time.sleep(LONG)
        # Load cookies from the saved file and add them to the WebDriver
        if os.path.exists("cookies.pkl"):
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)

        time.sleep(LONG)
        # Now navigate to the specific authenticated page
        self.driver.get(self.adv_url)
        time.sleep(SHORT)
        problems_field = self.driver.find_elements('xpath', "//div[@class='tv-http-error-page__wrapper']//p[contains(text(), 'autore')]") #browser language dependent
        if len(problems_field) > 0:
            print('Cookies not valid anymore. Standard login reuqired.')
            self.sign_in()
        else: 
            print('Cookies valid. Got in the right chart.')


    def save_cookies(self) -> None:
        # Save cookies to a file
        with open("cookies.pkl", "wb") as f:
            pickle.dump(self.driver.get_cookies(), f)


    def sign_in(self) -> None:
        """Sign into Tradingview"""
        # Reference url
        self.driver.get(self.bsc_url)
        time.sleep(EXLONG)
        # Perform sign in
        self.driver.find_element('xpath' , "//button[@aria-label='Open user menu']").click() # slower option because the DOM must be reversed # faster: "//*[@class='tv-header__user-menu-button tv-header__user-menu-button--anonymous js-header-user-menu-button']"
        time.sleep(LONG) # time for uploading the element
        self.driver.find_element('xpath', "//button[@data-name='header-user-menu-sign-in']").click() # faster: @class='item-jFqVJoPk item-mDJVFqQ3'
        time.sleep(LONG)
        self.driver.find_element('xpath', "//button[@name='Email']").click() # faster: @class='emailButton-nKAw8Hvt light-button-bYDQcOkp with-start-icon-bYDQcOkp variant-secondary-bYDQcOkp color-gray-bYDQcOkp size-medium-bYDQcOkp typography-regular16px-bYDQcOkp'
        time.sleep(SHORT)
        self.driver.find_element('xpath', "//input[@id='id_username']").send_keys(self.username)
        time.sleep(LONG)
        self.driver.find_element('xpath', "//input[@id='id_password']").send_keys(self.password)
        time.sleep(LONG)
        self.driver.find_element('xpath', "//button/span/span[text()= 'Sign in']").click() #dependent from the region of access for the language. I could you internation proxy for international language
        time.sleep(EXLONG)
        # Check for presence of html element for errors handling
        problems_field = self.driver.find_elements('xpath', "//div[contains(@class,'mainProblem-')]/div/span")
        if len(problems_field) > 0:
            print('Some errors to handles')
            if 'not a robot' in problems_field[0].text:
                print('Please, solve the CAPTCHA...')
            elif 'password is incorrect' in problems_field[0].text:
                print('Incorrect password')
                self.driver.quit()
            else: 
                print('Unknown error')
                self.driver.quit()
        time.sleep(LONG)
        try: 
            element = WebDriverWait(self.driver, 300).until(EC.presence_of_element_located(('xpath', "//span[@class='tv-header__offer-button-title'][text()='Upgrade plan']"))) #devo cambiare questo # //button[@aria-label='Search']
        except Exception as e:
            print('Not possible to log in')
            self.driver.quit()
        self.save_cookies()
        print('Cookies saved.') 
            
        # except ValueError as e:
        #     print('Not possible to log in')
        #     self.driver.quit()
        #     raise e
        

    def get_layout(self, asset: str = 'OANDA:EURUSD',) -> None:
        self.driver.get(self.adv_url)


    def _open_data_window(self) -> None:
        # Check if data window is open, otherwise open it
        check_datawindow = self.driver.find_elements('xpath', "//div[contains(@class, 'content-')]//button[@aria-label = 'Finestra dati'][@aria-pressed='false']")
        if len(check_datawindow) > 0:
            print('Data window is closed')
            check_datawindow[0].click() 
            time.sleep(SHORT)

    def _add_to_dict_mutli(self, comp, name, value) -> None: 
        if name in self.data_dict[comp]:
            self.data_dict[comp][name].append(value)
        else:
            self.data_dict[comp][name] = [value]

    def _add_to_dict(self, name, value) -> None:
        if name in self.data_dict:
            self.data_dict[name].append(value)
        else:
            self.data_dict[name] = [value]

    def _extract_values(self, values, comp: str = None) -> None: 
        # Extract indicator name components with related values
        for i in range(0,len(values),1):
            name = values[i].find_element('xpath', ".//div[contains(@class, 'itemTitle-')]").text
            value = values[i].find_element('xpath', ".//div/span").text
            if comp: 
                self._add_to_dict_mutli(comp, name, value)
            else:
                self._add_to_dict(name, value)

    def get_single_component_active(self, indicator_name: str = 'Ven_HARSI') -> None: 
        '''Explanation
        # Data window is open by default 
        # Ven_timing and Volume active by deafult
        # Active to unacive data difference is the presence of activation button near to the name of the indicator -> 
        #   contains(@class, 'item- study- disabled-') --> when active: contains(@class, 'item- study-)
        # Indicators are within a div contains(@class, 'sources-')
        # Indicators have data-status='undefined
        # Acivation by means of //div[contains(@class, 'sources-')//div[contains(@class, 'item- study- disabled-')]//div[contains(@class, 'buttonIcon-)]:  --> click
        #   further identification with //g[contains(@class, '-eye')]--> more than one is identified
        # Identification of inactive indicator name: //div[contains(@class, 'sources-')//div[contains(@class, 'item- study- disabled-')]//div[@data-name=
        #   'legend-source-title']//div[contains(@class, 'title-')] --> extract text
        # Activate indicator: click on 
        # Otherwise, in data windows is there the activation button too.

        ## Data window 
        # Element of the data window //div[contains(@class, 'chart-data-window')]
        # Data window components: //div[contains(@class, 'chart-data-window')]//div[contains(@class, 'view-')][contains(@class, 'hoverEnable-')]--> it has data-id field
        # Data window components not enabled: //div[contains(@class, 'chart-data-window')]//div[contains(@class, 'view-')][contains(@class, 'hoverEnable-')][contains(@class, 'hidden-')]
        # Name of compoent in header: //div[contains(@class, 'chart-data-window')]//div[contains(@class, 'view-')][contains(@class, 'hoverEnable-')]//div[contains(@class, 'header-')] --> 
        #   give back the list of componets, also the not active ones
        # Values of component in values: div[contains(@class, 'values-')]
        # Button for activation of indicator: in header --> span[contains(@class, 'button- apply-common-tooltip')]
        # Name of indicator: in header --> span[contains(@class, 'headerTitle- apply-common-tooltip')] --> text()
        # data values in values of component: a div[contains(@class, 'item-')]for each row of value --> div[contains(@class, 'itemTitle-')] text() for the name of row value,
        #   div[2] (no class) text() for value

        # Check if data window is open: check if there is a html element specific of the data window: //div[contains(@class, 'content-')]//button[@aria-label = 
        #   'Finestra dati'][@aria-pressed='false'] if not-open, [aria-pressed='true'] if open
        '''
        
        self._open_data_window()
        self.values_dict : dict = {}
        # Get all the active data components for an indicator of interest
        try: 
            component = self.driver.find_element('xpath', f"//div[contains(@class, 'chart-data-window')]//div[contains(@class, 'view-')][contains(@class, 'hoverEnable-') and not(contains(@class, 'hidden-'))][.//div[contains(@class, 'header-')]//span[contains(@class, 'headerTitle-')]//text()[contains(., '{indicator_name}')]]")
        except ValueError as e:
            print(f'Indicator {indicator_name} is not present')
            raise e
        values = component.find_elements('xpath', './/div[contains(@class, "values-")]/div')
        self._extract_values(values)
    

    def get_single_component(self, indicator_name: str = 'Ven_HARSI') -> None:
        self._open_data_window()
        self.data_dict : dict = {} 
        try: 
            component = self.driver.find_element('xpath', f"//div[contains(@class, 'chart-data-window')]//div[contains(@class, 'view-')][contains(@class, 'hoverEnable-')][.//div[contains(@class, 'header-')]//span[contains(@class, 'headerTitle-')]//text()[contains(., '{indicator_name}')]]")
        except ValueError as e:
            print(f'Indicator {indicator_name} is not present')
            raise e
        # Check if data component is active. If "hidden-", it must be activated before reading data
        if 'hidden-' in component.get_attribute('class'): 
            component.find_element_by_xpath(".//span[contains(@class, 'button-')]").click()
        # Extract data 
        values = component.find_elements('xpath', './/div[contains(@class, "values-")]/div')
        self._extract_values(values)


    def get_multi_components_active(self, indicators_name: list = ['Ven_HARSI']) -> None:
        self._open_data_window()
        self.data_dict : dict = {}
        try: 
            components = self.driver.find_elements('xpath', "//div[contains(@class, 'chart-data-window')]//div[contains(@class, 'view-')][contains(@class, 'hoverEnable-') and not(contains(@class, 'hidden-'))]")
        except IndexError as e:
            print(f'No active indicators')
            raise e
        # First data component is ohcl + variation from previous bar + volume info 
        # Automatic reading of data components
        for k in range(0,len(components),1): 
            indicator_name = components[k].find_element('xpath', ".//div[contains(@class, 'header-')]//span[contains(@class, 'headerTitle-')]").text.split(' ')[0]
            if indicator_name in indicators_name: 
                self.data_dict[indicator_name] = {}
                values = components[k].find_elements('xpath', './/div[contains(@class, "values-")]/div')
                self._extract_values(values, indicator_name)
    

    def get_multi_components(self, indicators_name: list = ['Ven_HARSI']) -> None:
        self._open_data_window()
        self.data_dict : dict = {}
        try: 
            components = self.driver.find_elements('xpath', "//div[contains(@class, 'chart-data-window')]//div[contains(@class, 'view-')][contains(@class, 'hoverEnable-') and not(contains(@class, 'hidden-'))]")
        except IndexError as e:
            print(f'No active indicators')
            raise e
        # First data component is ohcl + variation from previous bar + volume info 
        # Automatic reading of data components
        for k in range(0,len(components),1): 
            indicator_name = components[k].find_element('xpath', ".//div[contains(@class, 'header-')]//span[contains(@class, 'headerTitle-')]").text.split(' ')[0]
            if indicator_name in indicators_name: 
                if 'hidden-' in components[k].get_attribute('class'): 
                    components[k].find_element_by_xpath(".//span[contains(@class, 'button-')]").click()
                self.data_dict[indicator_name] = {}
                values = components[k].find_elements('xpath', './/div[contains(@class, "values-")]/div')
                self._extract_values(values, indicator_name)

# At this point, I have to: 
# - convert data to float (paying attention in particular case such as volume (with k at the end) or variation (with percentage component))
# define thread for reading data every 1min to get new values (or less if sub 1min analysis is of interest)
# - store data in a database or further data structure

    def append_data(self) -> None: 
        if len(self.data) == 0: 
            self.data = self.data_dict
        else: 
            for k,v in self.data_dict.items():
                for key,value in v.items():
                    self.data[k][key] += self.data_dict[k][key]

    def transform_data(self) -> None:
        for k,v in self.data_dict.items():
            if k == self.asset.split(':')[1]:
                # data from asset 
                self.data_dict[k]['Apertura'] = [float(self.data_dict[k]['Apertura'][0])]
                self.data_dict[k]['Massimo'] = [float(self.data_dict[k]['Massimo'][0])]
                self.data_dict[k]['Minimo'] = [float(self.data_dict[k]['Minimo'][0])]
                self.data_dict[k]['Chiusura'] = [float(self.data_dict[k]['Chiusura'][0])]
                self.data_dict[k]['Variazione'] = [self.data_dict[k]['Variazione'][0].split('(')[1][:-1].replace('−', '-')]
                self.data_dict[k]['Vol'] = [float(self.data_dict[k]['Vol'][0])] if 'K' not in self.data_dict[k]['Vol'][0] else [float(self.data_dict[k]['Vol'][0].split('K')[0]) *1000]
            elif k == 'Vol': 
                # Transform data 
                for key, value in v.items(): 
                    self.data_dict[k][key] = [float(self.data_dict[k][key][0])] if 'K' not in self.data_dict[k][key][0] else [float(self.data_dict[k][key][0].split('K')[0]) *1000]
            else: 
                for key, value in v.items(): 
                    if len(self.data_dict[k][key]) == 0: 
                        self.data_dict[k][key] = [None]
                    elif len(self.data_dict[k][key]) == 1: 
                        self.data_dict[k][key] = [float(self.data_dict[k][key][0].replace('−', '-'))]
                    elif len(self.data_dict[k][key]) > 1:
                        self.data_dict[k][key] = [[float(i.replace('−', '-')) for i in self.data_dict[k][key]]]
                    else: 
                        raise ValueError(f'Problematic data for {k} {key}')
        self.append_data()

    def end(self):
        """Closes the TV session"""
        self.driver.quit()

    def start_thread(self,indicators_name: list, thread_time : int): 
        self.i = 0
        stop_thread = False
        while not stop_thread: 
            self.i += 1
            self.get_multi_components(indicators_name)
            # print(self.data_dict)
            self.transform_data()
            time.sleep(thread_time) #timing function
            if self.i == 10: 
                # Wait for the thread to finish, or stop after 5 seconds
                print('Exiting thread...')
                print(self.data)
                stop_thread = True
                self.end()
            
    def run(self,adv_url: str, indicators_name: list, thread_time : int= 60): 
        self.load_chart_with_cookies()
        self.get_layout(adv_url)
        time.sleep(LONG)
        # Create thread of execution of data reading
        t = threading.Thread(target= lambda: self.start_thread(indicators_name=indicators_name, thread_time=thread_time))
        t.daemon = True
        t.start()
        #time.sleep(LONG)
        
        
