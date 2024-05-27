import time
import logging
import openpyxl

from Utils import Utils
from Locators import Locators as loc

from RPA.Browser.Selenium import By, Selenium
from robocorp.tasks import task

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NewsExtractor:
    def __init__(self, search_phrase,  months=None, news_category=None, local=True):
        self.search_phrase = search_phrase
        self.months = months
        self.news_category = news_category
        self.browser = Selenium()
        self.base_url = "https://apnews.com/"
        self.results = []
        self.results_count = 0
        # Configure logging
        self.logger = logging.getLogger('NewsExtractor')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('news_extractor.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.local = local

    def open_site(self):
        """Open the news site"""
        page_url = self.base_url
        self.browser.open_available_browser(url=page_url, maximized=True)
        self.logger.info("Opened the news site")          

    def click_on_search_button(self):
        """Click on search button to open search bar"""                
        # Wait for the search button to be present in the DOM and interactable
        try:
            # Wait for the element to be visible and interactable
            search_button = WebDriverWait(self.browser, 20).until(
                EC.element_to_be_clickable(self.browser.find_element(loc.search_button_xpath))
            )
            # Attempt to click the search button using Selenium's click method
            search_button.click()
        except Exception as e:
            self.logger.exception(e)
            # If the standard click does not work, use JavaScript to click the element
            try:
                # Use JavaScript to click the element
                self.browser.click_button_when_visible(search_button)
            except Exception as e:
                self.logger.exception(e)
                
    def enter_search_phrase(self):
        # Enter the search phrase
        searchbar = self.browser.find_element(loc.searchbar_xpath)
        searchbar = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable(searchbar)
            )
        self.browser.input_text(searchbar, self.search_phrase)
        self.browser.press_keys(searchbar, "ENTER")

    def filter_newest(self):
        try:
        # Wait up to 10 seconds before throwing a TimeoutException unless it finds the element to return
            WebDriverWait(self.browser.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, loc.dropdown_xpath))
            )
            self.browser.select_from_list_by_value(loc.dropdown_xpath, "3")
        except Exception as error:
            self.logger.warning(f"Option not available - {str(error)}")
    
    def click_on_news_category(self):
        try:
            category_menu = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable(self.browser.find_element(loc.category_menu_xpath))
            )
            category_menu.click()

            category_text = self.news_category
            category_checkbox_xpath = f'//div/div/label[span[contains(text(), {category_text})]]/input'
            WebDriverWait(self.browser.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, category_checkbox_xpath))
            )
            checkbox = self.browser.find_element(category_checkbox_xpath)
            # self.browser.select_checkbox(checkbox)
            self.browser.click_element_when_visible(checkbox)
        except Exception as error:
            self.logger.warning(f"Unable to click on checkbox - {str(error)}")
        
        # time.sleep(25)

    def click_on_next_page(self):
        next_results_arrow = self.browser.find_element(loc.next_results_xpath)
        self.browser.click_element_when_clickable(next_results_arrow)
        
    def extract_articles_data(self):
        """Extract data from news articles"""
        articles = self.browser.get_webelements(loc.articles_xpath)
        
        for r in articles:
            browser = self.browser.driver
            months = self.months

            # Capture and convert date string to datetime object
            date, valid_date = Utils.date_extraction_and_validation(browser=browser, months=months, article=r)

            if (valid_date):
                title = Utils.title_extraction(browser=browser, article=r)

                description = Utils.description_extraction(article=r)

                # Download picture if available and extract the filename
                picture_filename = Utils.picture_extraction(self.local, article=r)

                # Count search phrase occurrences in title and description
                count_search_phrases = (title.count(self.search_phrase) + description.count(self.search_phrase))

                # Check if title or description contains any amount of money
                monetary_amount = Utils.contains_monetary_amount(title) or Utils.contains_monetary_amount(description)

                # Store extracted data in a dictionary
                article_data = {
                    "title": title,
                    "date": date,
                    "description": description,
                    "picture_filename": picture_filename,
                    "count_search_phrases": count_search_phrases,
                    "monetary_amount": monetary_amount
                }
                
                self.results.append(article_data)
                self.results_count += 1
            else:
                break

        return valid_date
    
    def paging_for_extraction(self, goto_next_page=True):
        while (goto_next_page):
            goto_next_page = self.extract_articles_data()
            self.click_on_next_page()
        print(f"Extracted data from {self.results_count} articles")
    
    def close_site(self):
        # Close the browser
        self.browser.close_browser()

    def run(self):
        # Execute the entire news extraction process
        self.open_site()
        self.click_on_search_button()
        self.enter_search_phrase()
        self.click_on_news_category()
        self.filter_newest()
        self.paging_for_extraction()
        if self.local:
            Utils.LOCAL_save_to_excel(self.results)
        else:
            Utils.save_to_excel(self.results)
        self.close_site()
