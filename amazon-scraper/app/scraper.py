import contextlib
import re
import time
from dataclasses import dataclass

from fake_useragent import UserAgent
from requests_html import HTML
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from slugify import slugify


def extract_price_from_string(value: str, regex=r"[\$]{1}[\d]+\.?\d{0,2}"):
    x = re.findall(regex, value)
    val = None
    if len(x) == 1:
        val = x[0]

    return val


def get_user_agent():
    return UserAgent().random


@dataclass
class Scraper:
    url: str = None
    asin: str = None
    endless_scroll: bool = False
    endless_scroll_time: int = 5
    html_obj: HTML = None

    driver: WebDriver = None

    def __post_init__(self):
        if self.asin is not None:
            self.url = f"https://amazon.ae/dp/{self.asin}"
        if self.asin is None and self.url is None:
            raise Exception("ASIN or url is required.")

    def get_driver(self):
        if self.driver is None:
            user_agent = get_user_agent()

            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            options.add_argument(f"user-agent={user_agent}")
            self.driver = Chrome(options=options)

            return self.driver

    def perform_endless_scroll(self, driver):
        if driver is None:
            return
        if self.endless_scroll:
            current_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(self.endless_scroll_time)

                iter_height = driver.execute_script("return document.body.scrollHeight")
                if current_height == iter_height:
                    break

                current_height = iter_height
        return

    def extract_element_text(self, element_id):
        html_obj = self.get_html_obj()
        el = html_obj.find(element_id, first=True)
        return el.text if el else ""

    def extract_tables(self):
        html_obj = self.get_html_obj()
        return html_obj.find("table")

    def extract_table_dataset(self, tables):
        dataset = {}
        for table in tables:
            for tbody in table.element.getchildren():
                for tr in tbody.getchildren():
                    row = []
                    for col in tr.getchildren():
                        content = ""
                        with contextlib.suppress(Exception):
                            content = col.text_content()

                        if content != "":
                            _content = content.strip()
                            row.append(_content)

                    if len(row) != 2:
                        continue

                    key = row[0]
                    value = row[1]
                    # print(key, value)

                    key = slugify(key)
                    if key not in dataset:
                        if "AED" in value or "$" in value:
                            new_key = key
                            old_key = f"{key}_raw"
                            new_value = extract_price_from_string(value)
                            old_value = value

                            dataset[new_key] = new_value
                            dataset[old_key] = old_value
                        else:
                            dataset[key] = value

        return dataset

    def get_html_obj(self):
        if self.html_obj is None:
            html_str = self.get()
            self.html_obj = HTML(html=html_str)

        return self.html_obj

    def get(self):
        driver = self.get_driver()
        driver.get(self.url)
        if self.endless_scroll:
            self.perform_endless_scroll(driver=driver)
        else:
            time.sleep(10)

        return driver.page_source

    def scrape(self) -> dict:
        price_class_or_id_selector = ".a-offscreen"
        title_class_or_id_selector = "#productTitle"

        price_str = self.extract_element_text(price_class_or_id_selector)
        title_str = self.extract_element_text(title_class_or_id_selector)
        tables = self.extract_tables()
        dataset = self.extract_table_dataset(tables)

        return {"price_str": price_str, "title_str": title_str, **dataset}
