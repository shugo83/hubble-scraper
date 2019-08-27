from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urllib.request
from bs4 import BeautifulSoup
import time
import os
import logging
import sys
from datetime import datetime

timeout = 30
count = image_found = image_unique = 0
chrome_options = Options()
adresses = images = names = []
waiting = True
idxpath = '//*[@id="hubble-camsetn-camnotify"]/div[2]/ul/li[1]/div[1]'
prefs = {
    "profile.default_content_setting_values.plugins": 1,
    "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
    "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
    "PluginsAllowedForUrls": "https://app.hubbleconnected.com/#devices"
                             "https://app.hubbleconnected.com/#login"
                             "https://app.hubbleconnected.com/dashboard"
}

format_string = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=format_string,
                    filename='hubble.log',
                    filemode='w',
                    level=logging.INFO)
logging.info('Logging started')
chrome_options.add_experimental_option("prefs", prefs)
logging.info("Chrome experimental options set")

script_dir = os.path.dirname(__file__)
rel_path = 'credentials.txt'
abs_file_path = os.path.join(script_dir, rel_path)

with open(abs_file_path, 'r') as f:
    load = f.readlines()
login = load[0]
password = load[1]
logging.info('Credentials Loaded')
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1600, 900)  # ensures responsive design does not hide relevant buttons
driver.get('https://app.hubbleconnected.com/#login')
username_field = driver.find_element_by_name('hubble-signin-username')
password_field = driver.find_element_by_name('hubble-signin-password')
login_button = driver.find_element_by_id('hubble-signin')

username_field.send_keys(login)
password_field.send_keys(password)
login_button.click()
logging.info('Logged in')
while waiting:
    time.sleep(2)
    try:
        timeline_button = driver.find_element_by_class_name('hubble-dash-playwrap')
        timeline_button.click()
        waiting = False
    except Exception as E:
        logging.warning('Waiting for load')
        logging.debug(E)

        count += 2
        if count > timeout:
            logging.critical('Timeout')
            driver.quit()
            sys.exit(0)
logging.info('Element Loading')
try:
    element_present = EC.presence_of_element_located(
            (By.XPATH, idxpath))
    WebDriverWait(driver, timeout).until(element_present)
    logging.info('Waiting')
except TimeoutException:
    logging.info('Timed out')

logging.info('Looking for images')
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
for link in soup.find_all('img'):
    adresses.append(link.get('src'))
driver.quit()

script_dir = os.path.dirname(__file__)
pos = script_dir + '/saves'
for file in os.listdir(pos):
    k = file.split('-')[-1]
    k = k.split('.')[0]
    names.append(k)
logging.debug(adresses)
logging.info('Current images in directory scanned')
save_file_path = os.path.join(script_dir, 'saves/')
for i in range(len(adresses)):
    if str(adresses[i]).startswith(
            'https://hubble-resources.s3.amazonaws.com/freemium/'):
        image_found += 1
        images.append(adresses[i])
        location = adresses[i]
        dt = datetime.now().strftime('%Y-%m-%d')
        idt = adresses[i].split('/')[8]
        ident = idt.split('.')[0]
        if ident not in names:
            image_unique += 1
            name = save_file_path + str(dt) + '-' + str(ident) + '.jpg'
            try:
                urllib.request.urlretrieve(location, name)
            except Exception as E:
                logging.error(E)
logging.info(
        str(image_found) + ' images found, ' + str(image_unique) + ' new')
