from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import json

driver_path = 'C:\\Users\\Usuario\\Downloads\\geckodriver.exe'
page_url = "https://blackclover.fandom.com/wiki/List_of_Story_Arcs"

service = FirefoxService(driver_path)
driver = webdriver.Firefox(service=service)

driver.maximize_window()
driver.get(page_url)

def get_arc_title(arc):
    arc_title = arc.text.strip("\"")
    return arc_title

def map_chapter_element(chapter_element):
    chapter_element = chapter_element.text
    chapter_title = chapter_element.strip("\"")
    return chapter_title

def map_chapter_anchor_tag(chapter_anchor_tag):
    chapter_text = chapter_anchor_tag.text.strip()
    chapter_number_search = re.search("\d+", chapter_text)
    chapter_number = int(chapter_number_search.group())
    return chapter_number


def map_arc_table(table): 
    buffer = []
    chapter_list = table.find('ul')
    chapter_anchor_tags = chapter_list.find_all('a')
    chapter_numbers = list(map(map_chapter_anchor_tag , chapter_anchor_tags))
    chapter_elements = chapter_list.find_all('i')
    chapters_titles = list(map(map_chapter_element, chapter_elements))
    chapter_numbers.reverse()
    chapters_titles.reverse()
    for index, title in enumerate(chapters_titles):
        buffer.append({ "number": chapter_numbers[index], "title": title })
    return buffer

try:
   source = driver.page_source
   soup = BeautifulSoup(source, "lxml")
   buffer = { "arcs": [] }

   manga_arcs_container = soup.find('div', class_ = "mw-parser-output")
   manga_arcs_headers = manga_arcs_container.find_all('h2')
   manga_arc_tables = manga_arcs_container.find_all('table', recursive=False)
   manga_arcs_titles = list(map(get_arc_title, manga_arcs_headers[1:]))
   manga_arcs_chapters = list(map(map_arc_table, manga_arc_tables))

   with open("arcs.json", "w") as outfile:
        for index, arc in enumerate(manga_arcs_titles):
            arc_synopsis = driver.find_element(By.XPATH, f"/html/body/div[4]/div[3]/div[3]/main/div[3]/div[2]/div/table[{index + 1}]/tbody/tr[2]/td")
            arc_object = { "title": arc, "synopsis": arc_synopsis.text, "chapters": manga_arcs_chapters[index] }
            buffer["arcs"].append(arc_object)

        buffer["arcs"].reverse()
        json.dump(buffer, outfile, indent=4, separators=(',', ':'))

except Exception as e: # work on python 3.x
    print('Failed to upload to ftp: '+ str(e))
    driver.quit()
    
driver.quit()