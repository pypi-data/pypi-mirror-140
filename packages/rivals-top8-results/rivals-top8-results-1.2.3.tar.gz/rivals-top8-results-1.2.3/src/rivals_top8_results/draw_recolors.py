import glob
import os
from pathlib import Path
import time
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

characters = {
    "Clairen": "#charRow1 > div:nth-child(1)",
    "Forsburn": "#charRow1 > div:nth-child(2)",
    "Zetterburn": "#charRow1 > div:nth-child(3)",
    "Wrastor": "#charRow1 > div:nth-child(4)",
    "Absa": "#charRow1 > div:nth-child(5)",
    "Elliana": "#charRow1 > div:nth-child(6)",
    "Sylvanos": "#charRow2 > div:nth-child(1)",
    "Maypul": "#charRow2 > div:nth-child(2)",
    "Kragg": "#charRow2 > div:nth-child(3)",
    "Orcane": "#charRow2 > div:nth-child(4)",
    "Etalus": "#charRow2 > div:nth-child(5)",
    "Ranno": "#charRow2 > div:nth-child(6)",
    "Ori": "#charRow3 > div:nth-child(1)",
    "Shovel Knight": "#charRow3 > div:nth-child(2)",
    "Mollo": "#charRow3 > div:nth-child(3)",
    "Hodan": "#charRow3 > div:nth-child(4)",
    "Pomme": "#charRow3 > div:nth-child(5)",
    "Olympia": "#charRow3 > div:nth-child(6)",
}

code_length = {
    "Clairen": 54,
    "Forsburn": 54,
    "Zetterburn": 39,
    "Wrastor": 39,
    "Absa": 39,
    "Elliana": 49,
    "Sylvanos": 39,
    "Maypul": 39,
    "Kragg": 34,
    "Orcane": 19,
    "Etalus": 24,
    "Ranno": 39,
    "Ori": 39,
    "Shovel Knight": 34,
    "Mollo": 54,
    "Hodan": 54,
    "Pomme": 49,
    "Olympia": 54,
}

def get_latest_file(dir):
    list_of_files = glob.glob(f"{dir}/*")
    latest_file = max(list_of_files, key=os.path.getmtime)
    return latest_file


def generate_recolor(driver, character, skin_code):
    char_button = driver.find_element(By.ID, "charSelector")
    char_button.click()

    select_char_button = driver.find_element(By.CSS_SELECTOR, characters[character])
    select_char_button.click()

    # waits for portrait to to avoid char length hiccups
    time.sleep(0.2)

    code_input = driver.find_element(By.ID, "codeInput")

    if len(skin_code) == code_length[character]:
        code_input.send_keys(skin_code)

    # clicks on download button
    download_button = driver.find_element(By.ID, "downImgButton")

    # might be needed to correctly load the download buttons
    # time.sleep(0.1)
    download_button.click()

    # clicks on "download portrait" button
    download_portrait_button = driver.find_element(By.ID, "Portrait")
    download_portrait_button.click()

    # useful when creating multiple recolors
    back_button = driver.find_element(By.CSS_SELECTOR, "button.okButton:nth-child(3)")
    back_button.click()

    # prevents *.tmp and *.crdownload files from being left around
    time.sleep(0.5)


def generate_recolors_sequence(driver, skins_dict, dir):
    # a temporary folder is needed to prevent same-name conflicts, useful for proper renames
    try:
        os.mkdir("tmp")
    except FileExistsError:
        pass

    for entry in skins_dict:
        generate_recolor(
            driver, skins_dict[entry]["Character"], skins_dict[entry]["Code"]
        )
        filename = get_latest_file(dir)

        try:
            os.rename(filename, f"{skins_dict[entry]['Code']}.png")
        except FileExistsError:
            pass

        try:
            shutil.move(f"{skins_dict[entry]['Code']}.png", "./tmp")
        except shutil.Error:
            pass

    # moves files to requested dir
    for file in os.listdir("./tmp"):
        if file not in os.listdir(dir):
            shutil.move(file, dir)

    # deletes temp folder
    shutil.rmtree("./tmp")


def start_headless_driver(download_dir=os.path.dirname(os.path.realpath(__file__))):
    prefs = {"download.default_directory": str(download_dir)}

    # sets options
    options = Options()
    options.add_argument("--headless")
    options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=options)


if __name__ == "__main__":
    custom_skins_dir = Path(os.path.dirname(os.path.realpath(__file__))) / Path("Resources/Characters/Main/Custom")

    # initializes Chrome driver with the desired options
    driver = start_headless_driver(custom_skins_dir)

    # gets recolorer webpage
    driver.get("https://readek.github.io/RoA-Skin-Recolorer/")

    recolors = {
        0: {
            "Character": "Orcane",
            "Code": "994C-E2FF-DE00-7F00",
        },
        1: {
            "Character": "Pomme",
            "Code": "A17D-5DD7-0000-BC5B-E500-0000-FFCC-00FF-0000-9600",
        },
        2: {
            "Character": "Pomme",
            "Code": "E8D9-D300-1C5F-0049-9600-9FCA-FFB3-22D2-7BFF-A400",
        },
        3: {
            "Character": "Kragg",
            "Code": "551C-7AFF-FFFF-9D47-D4E5-6600-6700",
        },
        4: {
            "Character": "Olympia",
            "Code": "42FE-842B-FF4B-4538-42C4-237B-FFFF-FFFF-FFFF-00FF-5377",
        },
        5: {
            "Character": "Olympia",
            "Code": "F5A9-B8F5-A9B8-F2DB-C2F5-A9B8-5BCE-FAFF-F9F9-5BCE-FA8A",
        },
        6: {
            "Character": "Elliana",
            "Code": "1111-5DD7-0000-BC5B-E500-0000-FFCC-00FF-1111-9600",
        },
        7: {
            "Character": "Mollo",
            "Code": "FF00-00A6-0000-3112-1231-1212-FF00-00FF-0000-000D-202F",
        },
    }

    # generate_recolors_sequence(driver, recolors, custom_skins_dir)
    generate_recolor(driver, "Orcane", "0000-0000-0000-1111")

    # closing browser
    driver.close()
