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
from datetime import datetime
timeout = 10
chrome_options = Options()
adresses = []
images = []
names = []
waiting = True
prefs = {
    "profile.default_content_setting_values.plugins": 1,
    "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
    "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
    "PluginsAllowedForUrls": "https://app.hubbleconnected.com/#devices"
                             "https://app.hubbleconnected.com/#login"
}
format_string = '%(levelname)8s:\t%(message)s'
logging.basicConfig(format=format_string, level=logging.INFO)
logging.info("Logging system active")
chrome_options.add_experimental_option("prefs", prefs)
logging.info("Chrome experimental options set")

with open('credentials.txt', 'r') as f:
    load = f.readlines()
login = load[0]
password = load[1]
logging.info('Credentials Loaded')
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.set_window_size(1920, 1080)  # ensures responsive design does not hide relevant buttons
driver.get("https://app.hubbleconnected.com/#login")
username_field = driver.find_element_by_name("username")
password_field = driver.find_element_by_name("password")
login_button = driver.find_element_by_id("login_submit")

username_field.send_keys(login)
password_field.send_keys(password)
login_button.click()
logging.info('logged in')
while waiting:
    time.sleep(0.5)
    try:
        timeline_button = driver.find_element_by_class_name("timeline-tab")
        timeline_button.click()
        waiting = False
    except Exception as E:
        logging.error(E)


try:
    element_present = EC.presence_of_element_located(
            (By.ID, 'timeline_container'))
    WebDriverWait(driver, timeout).until(element_present)
    logging.info('Waiting')
except TimeoutException:
    logging.info('Timed out')

logging.info('Looking')
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
for link in soup.find_all('a'):
    adresses.append(link.get('href'))

try:
    timeline_next = driver.find_element_by_class_name("pagelinks-last")
    count = 0
    while count < 10:  # Maximum number of page expected
        timeline_next.click()
        time.sleep(5)  # not sure of an alternative
        logging.info('looking on page' + count)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            if link.get('href') not in adresses:
                adresses.append(link.get('href'))
except:
    logging.info('No further pages found')
driver.quit()


script_dir = os.path.dirname(__file__)
pos = script_dir + '/saves'
for file in os.listdir(pos):
    k = file.split('-')[-1]
    k = k.split('.')[0]
    names.append(k)
logging.info('Current images scanned')
for i in range(len(adresses)):
    if str(adresses[i]).startswith(
            'https://hubble-resources.s3.amazonaws.com/freemium/'):
        logging.info('Found image')
        images.append(adresses[i])
        location = adresses[i]
        dt = datetime.now().strftime('%y-%m-%d')
        idt = adresses[i].split('/')[8]
        ident = idt.split('.')[0]
        if ident not in names:
            logging.info('unique found')
            name = 'saves/' + str(dt) + '-' + str(ident) + '.jpg'
            try:
                urllib.request.urlretrieve(location, name)
            except Exception as E:
                logging.error(E)
        else:
            logging.info('Already collected')
