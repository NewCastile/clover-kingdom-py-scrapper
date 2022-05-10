from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from unidecode import unidecode
import json
import re

basePath = "https://inmanga.com"
driver_path = 'C:\\Users\\Usuario\\Downloads\\geckodriver.exe'
page_url = 'https://inmanga.com/ver/manga/Black-Clover/e7f9297e-377a-4c23-b396-ae88600251b1'

def map_chapter(chapter):
    data = chapter.find_all('span')
    chapter_number_string = unidecode(data[0].text.strip())
    chapter_number_search = re.search("\d+", chapter_number_string)
    chapter_number = int(chapter_number_search.group())
    return { "number": chapter_number, "pages": [] }

service = FirefoxService(driver_path)
driver = webdriver.Firefox(service=service)

driver.maximize_window()
driver.get(page_url)

try:
   
    description = driver.find_element(By.CLASS_NAME, "panel-body")
    title = driver.find_element(By.CSS_SELECTOR, ".panel-heading h1")
    
    buffer = { "manga": {
        "title": title.text,
        "description": description.text,
    } }

    WebDriverWait(driver, 60).until(
        EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".custom-list-group-item"))
    )

    source = driver.page_source
    soup = BeautifulSoup(source, "lxml")
    
    chapters_container = soup.find('div', id="ChaptersContainer")
    chapters_elements = chapters_container.find_all('a', class_="custom-list-group-item", href=True)
    
    ## remove [1:2] to process all chapters
    mapped_chapters = list(map(map_chapter, chapters_elements[1:2]))
    with open("last-chapter.json", "w") as outfile:
        for chapter in mapped_chapters:
            chapter_link = chapter["link"]
            driver.get(chapter_link)
            WebDriverWait(driver, 60)
            try:
                WebDriverWait(driver, 60).until(
                    EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".ImageContainer"))
                )

                pages = driver.find_elements(By.CSS_SELECTOR, ".ImageContainer")
                images = list(map(lambda element: element.get_attribute("id") , pages))
                images_length = len(images)

                for index, imageId in enumerate(images[0 : images_length]):
                    page_element = driver.find_element(By.ID, imageId)
                    image_src = page_element.get_attribute('src')
                    chapter["pages"].append(image_src)
                    if index == images_length - 1:
                        break
                    page_element.click()

            except Exception as e: # work on python 3.x
                print('Failed to upload to ftp: '+ str(e))
                driver.quit()

        buffer["manga"]["chapters"] = mapped_chapters
        json.dump(buffer, outfile, indent=4, sort_keys=True, separators=(',', ':'))
        
except Exception as e: # work on python 3.x
    print('Failed to upload to ftp: '+ str(e))
    driver.quit()

driver.quit()