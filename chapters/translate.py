from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import clipboard


target_lang = 'es'
source_lang = 'en'
arcs = open('./arcs.json')
chapters = open("./chapters.json")
chaptersData = json.load(chapters)
arcsData = json.load(arcs)

buffer = { "arcs": [] }

driver_path = 'C:\\Users\\Usuario\\Downloads\\geckodriver.exe'
service = FirefoxService(driver_path)
driver = webdriver.Firefox(service=service)
button_xpath = "/html/body/div[3]/main/div[3]/div[3]/section[2]/div[3]/div[6]/div[4]/span/span/span/button"
ignored_element_class = "dl_cookieBanner_innerLax"
to_wait_element_xpath = "/html/body/div[3]/main/div[3]/div[3]/section[2]/div[3]/div[6]/div[1]"


try:
    for arc in arcsData['arcs']:
        arc_title = arc["title"]
        driver.get(f"https://www.deepl.com/{target_lang}/translator#{source_lang}/{target_lang}/{arc_title}")
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, to_wait_element_xpath))
        )
        button = driver.find_element(By.XPATH, button_xpath)
        button.click()
        translated_arc_title = clipboard.paste()

        translated_arc_obj = { "title": translated_arc_title, "synopsis": "" , "chapters": [] }
        buffer["arcs"].append(translated_arc_obj)
    
    ## remove[0:1] to translate all arcs
    for index, arc in enumerate(arcsData['arcs'][0:1]):
        arc_synopsis = arc["synopsis"]
        driver.get(f"https://www.deepl.com/{target_lang}/translator#{source_lang}/{target_lang}/{arc_synopsis}")
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, to_wait_element_xpath))
        )
        button = driver.find_element(By.XPATH, button_xpath)
        button.click()
        translated_arc_synopsis = clipboard.paste()
        buffer["arcs"][index]["synopsis"] = translated_arc_synopsis

        with open("translated-last-arcs.json", "w") as outfile:
            for chapter in arc["chapters"]:
                chapter_title = chapter["title"]
                driver.get(f"https://www.deepl.com/{target_lang}/translator#{source_lang}/{target_lang}/{chapter_title}")
                WebDriverWait(driver, 60).until(
                    EC.visibility_of_element_located((By.XPATH, to_wait_element_xpath))
                )
                button = driver.find_element(By.XPATH, button_xpath)
                button.click()
                translated_chapter_title = clipboard.paste()
                print(translated_chapter_title)
                translated_chapter_obj = { "number": chapter["number"], "title": translated_chapter_title }
                buffer["arcs"][index]["chapters"].append(translated_chapter_obj)
            json.dump(buffer, outfile, indent=4, separators=(',', ':'))
except Exception as e:
    print(e)
    driver.quit()

driver.quit()


arcs.close()