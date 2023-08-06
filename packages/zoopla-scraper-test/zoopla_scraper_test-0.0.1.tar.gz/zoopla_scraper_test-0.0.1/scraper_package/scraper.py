from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
from typing import Optional
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

class Scraper:
    '''
    This class is a scraper that can be used for browsing different websites
    Parameters
    ----------
    url: str
        The link that we want to visit
   
    Attribute
    ---------
    driver:
        THis is the webdriver object
    '''
    def __init__(self, url):
        self.driver = Chrome(ChromeDriverManager().install())
        self.driver.get(url)


    def accept_cookies(self, xpath: str, iframe: Optional[str] = None):
        '''
        This method looks for and click on the accept ccokies button
        Parameters
        ----------
        xpath: str
            The xpath of the accept cookies button
        iframe: Optional[str]
            The id of the iframe in case there is one in front of the accept cookies button
        '''
        try:
            time.sleep(2)
            self.driver.switch_to.frame(iframe)
            cookies_button = (
                WebDriverWait(self.driver, 10)
                .until(EC.presence_of_element_located((
                    By.XPATH, xpath))
                    )
            )
            print(cookies_button)
            self.driver.find_element(By.XPATH, xpath).click()

        except TimeoutException:
            print('No cookies found')
    def look_for_search_bar(self,
                            xpath: str):
        '''
        Looks for the search bar given the xpat
        Parameters
        ----------
        xpath: str
            The xpath of the search bar
        Returns
        -------
        Optional[webdriver.element]
        '''
        try:
            time.sleep(1)
            search_bar = (
                WebDriverWait(self.driver, 5)
                .until(EC.presence_of_element_located(
                    (By.XPATH, xpath)
                    )
                    )
            )
            search_bar.click()
            return search_bar
        except TimeoutException:
            print('No search bar found')
            return None
    def send_keys_to_search_bar(self,
                                text: str,
                                xpath: str) -> None:
        '''
        Write something on a search bar
        Parameters
        ----------
        text: str
            The text we want to pass to the search bar
        xpath: str
            xpath of the search bar
        '''
        search_bar = self.look_for_search_bar(xpath)
        if search_bar:
            search_bar.send_keys(text)
        else:
            raise Exception('No search bar found')
    def find_container(self, xpath: str) -> None:
        '''
        Finds the container of items in a website
        '''
        return self.driver.find_element(By.XPATH, xpath)


class ScraperZoopla(Scraper):
    '''
    Scraper that works only for the zoopla website
    It will extract information about the price, n_bedrooms, n_bathrooms,
    and sqft of the properties in a certain location
    Parameters
    ----------
    location: str
        The location to look properties in
    Attributes
    ----------
    prop_dict: dict
        Contains price, bedrooms, bathrooms, and sqft of each property
    '''
    def __init__(self, location: str):
        super().__init__('https://www.zoopla.co.uk')
        self.prop_dict = {
            'Price': [],
            'Bedrooms': [],
            'Bathrooms': [],
            'Sqft': [],
            }
        self.location = location

    def scrape_properties(self):
        self.accept_cookies(xpath='//button[@id="save"]',
                            iframe='gdpr-consent-notice')
        self.send_keys_to_search_bar(
            text=self.location,
            xpath='//input[@id="header-location"]')
        time.sleep(1)
        list_locations = self.driver.find_element(By.XPATH, '//ul[@data-testid="autosuggest-list"]')
        time.sleep(1)
        list_locations.find_element(By.XPATH, './li').click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, '//button[@data-testid="search-button"]').click()
        # container = self.find_container(xpath='//div[@class="css-1anhqz4-ListingsContainer earci3d2"]')
        # container.find_elements(By.XPATH)


if __name__ == '__main__':
    bot = ScraperZoopla('London')
    bot.scrape_properties()