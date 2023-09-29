from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def test_eight_components():
    options = Options()
    options.binary_location = "/opt/google/chrome-linux64/chrome" # "/usr/bin/chrome" 
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.neuralnine.com/")

    driver.quit()

if __name__ == "__main__":
    test_eight_components()