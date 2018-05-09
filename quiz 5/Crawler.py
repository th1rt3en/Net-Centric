from contextlib import closing

from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.support.ui import WebDriverWait

option = ChromeOptions()
option.add_argument("headless")

titles = ""

with closing(Chrome("chromedriver.exe", chrome_options=option)) as browser:
    browser.get("https://junemanga.com/collections/all")
    pages = int(browser.execute_script(
        "return document.getElementsByClassName('pagination-page')[0].children[5].children[0].innerHTML"))
    for i in range(1, pages+1):
        with closing(Chrome("chromedriver.exe", chrome_options=option)) as b:
            b.get("https://junemanga.com/collections/all?page=" + str(i))
            number_of_titles = int(b.execute_script(
                "return document.getElementsByClassName('products-grid')[0].children.length"))
            for j in range(number_of_titles):
                titles += b.execute_script(
                    "return document.getElementsByClassName('product-title')[%d].innerHTML" % j).encode("ascii", "ignore") + "\n"

with open("titles.txt", "w") as f:
    f.write(titles)
