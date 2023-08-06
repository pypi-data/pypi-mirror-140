import time
from warnings import warn

import requests

from .paths import *
from .url import hearthcards_url

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, \
    WebDriverException


class PathIsNotAbsolute(Warning):
    pass


def create_card(
        save_name: str = 'card.png',
        card_type: str = 'minion',
        card_name: str = '',
        card_class: str = 'Neutral',
        minion_type: str = '',
        rarity: str = 'basic',
        card_text: str = '',
        card_image: str = '',
        mana_cost: int = 0,
        attack: int = 0,
        health: int = 0,
        hd: bool = False,
        gold: bool = False,
        addon: str = '',
        wait_time: int = 5):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(hearthcards_url)

        CLASS = driver.find_element(By.CSS_SELECTOR, '#' + card_class)
        driver.execute_script("arguments[0].checked = true;", CLASS)

        if addon:
            ADDON = driver.find_element(By.CSS_SELECTOR, '#swirl')
            driver.execute_script(f"arguments[0].value = '{addon}';", ADDON)

        driver.find_element(By.XPATH, MANA_FIELD).send_keys(mana_cost)
        driver.find_element(By.XPATH, ATTACK_FIELD).send_keys(attack)
        driver.find_element(By.XPATH, HEALTH_FIELD).send_keys(health)

        driver.find_element(By.XPATH, TYPE).send_keys(minion_type)

        if rarity != 'basic':
            RARITY_BUTTON = RARITY_BUTTONS[rarity]
            driver.find_element(By.CSS_SELECTOR, RARITY_BUTTON).click()

        if card_image:
            try:
                driver.find_element(By.XPATH, ART_UPLOAD).send_keys(card_image)
            except WebDriverException:
                warn('Path is not absolute. THere will be no image',
                     PathIsNotAbsolute)

        if hd:
            driver.find_element(By.CSS_SELECTOR, HD).click()
            driver.find_element(By.XPATH, HD_USE).click()

        if gold:
            driver.find_element(By.CSS_SELECTOR, GOLDEN).click()

        driver.find_element(By.XPATH, TEXT_FIELD).send_keys(card_text)

        if card_type != 'minion':
            driver.find_element(By.CSS_SELECTOR,
                                TYPE_BUTTONS[card_type]).click()

        driver.find_element(By.XPATH, NAME_FIELD).send_keys(card_name)

        try:
            driver.find_element(By.XPATH, SUBMIT_BTN).click()
        except NoSuchElementException:
            pass

        time.sleep(wait_time)

        ht = driver.page_source
        ht = ht[ht.find('<a id="card-click" download="') + 29:]
        ht = ht[:ht.find('"')]
        link = 'https://www.hearthcards.net/' + ht
        card = requests.get(link)

        f = open(save_name, 'wb')
        f.write(card.content)
        f.close()

        driver.stop_client()
        driver.close()
        driver.quit()
    except:
        driver.stop_client()
        driver.close()
        driver.quit()
        raise Exception('Something went wrong')


class CardCreator:
    def __init__(self, driver=None, wait_time: int = 10):
        if not driver:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')

            driver = webdriver.Chrome(options=chrome_options)

        self.driver = driver
        self.wait_time = wait_time

    def create_card(self,
                    save_name: str = 'card.png',
                    card_type: str = 'minion',
                    card_name: str = '',
                    card_class: str = 'Neutral',
                    minion_type: str = '',
                    rarity: str = 'basic',
                    card_text: str = '',
                    card_image: str = '',
                    mana_cost: int = 0,
                    attack: int = 0,
                    health: int = 0,
                    hd: bool = False,
                    gold: bool = False,
                    addon: str = ''):

        try:

            driver = self.driver

            driver.get(hearthcards_url)

            CLASS = driver.find_element(By.CSS_SELECTOR, '#' + card_class)
            driver.execute_script("arguments[0].checked = true;", CLASS)

            if addon:
                ADDON = driver.find_element(By.CSS_SELECTOR, '#swirl')
                driver.execute_script(f"arguments[0].value = '{addon}';",
                                      ADDON)

            driver.find_element(By.XPATH, MANA_FIELD).send_keys(mana_cost)
            driver.find_element(By.XPATH, ATTACK_FIELD).send_keys(attack)
            driver.find_element(By.XPATH, HEALTH_FIELD).send_keys(health)

            driver.find_element(By.XPATH, TYPE).send_keys(minion_type)

            if rarity != 'basic':
                RARITY_BUTTON = RARITY_BUTTONS[rarity]
                driver.find_element(By.CSS_SELECTOR, RARITY_BUTTON).click()

            if card_image:
                try:
                    driver.find_element(By.XPATH, ART_UPLOAD).send_keys(
                        card_image)
                except WebDriverException:
                    warn('Path is not absolute. THere will be no image',
                         PathIsNotAbsolute)

            if hd:
                driver.find_element(By.CSS_SELECTOR, HD).click()
                driver.find_element(By.XPATH, HD_USE).click()

            if gold:
                driver.find_element(By.CSS_SELECTOR, GOLDEN).click()

            driver.find_element(By.XPATH, TEXT_FIELD).send_keys(card_text)

            if card_type != 'minion':
                driver.find_element(By.CSS_SELECTOR,
                                    TYPE_BUTTONS[card_type]).click()

            driver.find_element(By.XPATH, NAME_FIELD).send_keys(card_name)

            try:
                driver.find_element(By.XPATH, SUBMIT_BTN).click()
            except NoSuchElementException:
                pass

            time.sleep(self.wait_time)

            ht = driver.page_source
            ht = ht[ht.find('<a id="card-click" download="') + 29:]
            ht = ht[:ht.find('"')]
            link = 'https://www.hearthcards.net/' + ht
            card = requests.get(link)

            f = open(save_name, 'wb')
            f.write(card.content)
            f.close()
        except:
            raise Exception('Something went wrong')

    def stop(self):
        self.driver.stop_client()
        self.driver.close()
        self.driver.quit()
