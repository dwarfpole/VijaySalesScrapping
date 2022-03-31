from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert

import time
import os
import re
import csv


class scrape():

    def __init__(self):
        option = webdriver.ChromeOptions()
        # option to perform scrape without an open window
        # option.add_argument("--start-maximized")
        # option.add_argument('headless')

        # stops images from loading to make pages load quicker
        prefs = {"profile.managed_default_content_settings.images": 2}

        option.add_experimental_option("prefs", prefs)
        # adding chrome driver (present in folder named chromedriver_win32)
        os.environ['PATH'] += os.path.join(os.getcwd(), 'chromedriver_win32')
        self.browser = webdriver.Chrome(options=option)
        self.browser.implicitly_wait(10)

        # each item's information to be extracted are listed below
        # add header spec for additional specs
        self.csv_header = ['NAME', 'RATING', 'REVIEW', 'COST', "URL", 'BRAND', 'MODEL NAME', 'SKU', 'BATTERY LIFE', "BLUETOOTH", "BLUETOOTH RANGE", "BATTERY LIFE", "POWER INPUT", "WIRED/WIRELESS", "TYPE", "COMPATIBLE DEVICES", 'WARRANTY SUMMARY', "ADDITIONAL FEATURE", 'Generic Name', 'Country of origin',
                           'Country of Manufacturer', 'Manufacturers Details', 'Importer Detail', 'Packers Details', 'Item Available From Date', 'Product Dimensions(W x D x H)', 'Product Weight']

        # regex to remove html tags from string
        self.CLEANR = re.compile(
            '<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

        # url of main page
        self.url = "https://www.vijaysales.com/mobiles-and-tablets/audio-accessories"
        self.limit = 100  # number of items to be scapped

    # function to scrape main page
    def extract_main_page(self):

        self.browser.get(self.url)
        links = []
        # time.sleep(1)
        # extract html content
        body = self.browser.find_element(By.TAG_NAME, 'html')

        try:
            Alert(self.browser).accept()
        except:
            print("No alert")

        # scroll down till we get 100 items
        while len(links) < self.limit:
            for i in range(2):
                body.send_keys(Keys.SPACE)
            # extracting url from each element of an item
            # each item has class of .vj-cur-pnter nabprod
            links = [link.get_attribute('href') for link in self.browser.find_elements(
                By.CSS_SELECTOR, 'a[class="vj-cur-pnter nabprod"]')]
            # time.sleep(0.1)

        # making sure we don't have more that 100 items
        self.links = links[: -len(links)+self.limit]

    # To manage csv file
    def openCSV(self):
        self.csv = open('output1.csv', 'w',  newline='')
        # adding header to csv file
        self.dict_writer = csv.DictWriter(self.csv, self.csv_header)
        self.dict_writer.writeheader()

    # extract item info from each item's page
    def extract_items_info(self):
        # for link in self.progressbar(self.links, "Computing: ", 40):
        # time.sleep(0.1) # any calculation you need
        count = 0
        for link in self.links:
            # while(staleElement):
            try:
                # item_info dictionary to contain all specs of an item
                item_info = {}
                self.browser.get(link)
                body = self.browser.find_element(By.TAG_NAME, 'html')

                # making sure all elements are loaded:
                for i in range(20):
                    body.send_keys(Keys.SPACE)
                    time.sleep(0.2)
                body.send_keys(Keys.END)

                body = self.browser.find_element(By.TAG_NAME, 'html')

                # extracting name, rating and review
                item_info["NAME"] = body.find_element(
                    By.ID, 'ContentPlaceHolder1_h1ProductTitle').text
                item_info["RATING"] = body.find_element(
                    By.CLASS_NAME, 'starcolor').text
                item_info["REVIEW"] = body.find_element(
                    By.CLASS_NAME, 'clsRatingCounts').text

                item_info["URL"] = link

                # extracting price
                cost = body.find_elements(
                    By.CSS_SELECTOR, 'div[id="ContentPlaceHolder1_fillprice"] > div > div > span:nth-child(3) > span')

                if(len(cost) == 0):
                    cost = body.find_elements(
                        By.CSS_SELECTOR, 'div[id="ContentPlaceHolder1_fillprice"] > div > span:nth-child(3) > span')

                item_info["COST"] = cost[0].text

                # extracting some more specs from product information table
                specs = body.find_elements(By.CLASS_NAME, "cls-li-hld")

                for spec in specs:
                    # extracting spec name and spec valuex
                    specKey = spec.find_element(
                        By.CSS_SELECTOR, 'div:nth-child(1)')
                    specValue = spec.find_element(
                        By.CSS_SELECTOR, 'div:nth-child(2)')

                    # clearing html tag, if any, to get text using regex
                    specKeyText = re.sub(self.CLEANR, '', specKey.get_attribute(
                        "innerHTML").strip())

                    specValueText = re.sub(
                        self.CLEANR, '', specValue.get_attribute("innerText").strip())

                    # adding spec value to item_info
                    item_info[specKeyText] = specValueText

                to_csv = {}
                # adding only specified item info to csv
                for header in self.csv_header:
                    if header in item_info:
                        to_csv[header] = item_info[header]
                    else:
                        to_csv[header] = ''

                self.dict_writer.writerows([to_csv])
                count += 1
                print(f"Progress:{count}/{self.limit}")

            except Exception as e:
                print(e)
                print("error for " + link)

    # closing all resources
    def tearDown(self):
        # close the file
        self.csv.close()
        # close the driver
        self.browser.close()


if __name__ == "__main__":
    scrape = scrape()
    scrape.extract_main_page()
    scrape.openCSV()
    scrape.extract_items_info()
    scrape.tearDown()
    print('Task done')
