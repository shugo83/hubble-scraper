from selenium import webdriver
import urllib.request
from bs4 import BeautifulSoup
import time
from datetime import datetime
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
adresses=[]
images=[]
prefs = {
    "profile.default_content_setting_values.plugins": 1,
    "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
    "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
    "PluginsAllowedForUrls": "https://app.hubbleconnected.com/#devices"
                             "https://app.hubbleconnected.com/#login"
}
chrome_options.add_experimental_option("prefs",prefs)

with open('credentials.txt','r') as f:
    load = f.readlines()
login=load[0]
password=load[1]
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.set_window_size(1920, 1080) # ensures responsive design does not hide relevant buttons
driver.get("https://app.hubbleconnected.com/#login")
username_field = driver.find_element_by_name("username")
password_field = driver.find_element_by_name("password")
login_button = driver.find_element_by_id("login_submit")

username_field.send_keys(login)
password_field.send_keys(password)
login_button.click()
print('logged in')
time.sleep(5)
#nasty way of waiting - required else ElementNotVisibleException: element not visible - cannot catch with an except

timeline_button = driver.find_element_by_class_name("timeline-tab")
timeline_button.click()

time.sleep(5)
#same as above
print('looking')
html = driver.page_source
soup = BeautifulSoup(html,'html.parser')
for link in soup.find_all('a'):
    adresses.append(link.get('href'))
driver.quit()
for i in range(len(adresses)):
    if str(adresses[i]).startswith('https://hubble-resources.s3.amazonaws.com/freemium/'):
        print('found image')
        images.append(adresses[i])
        location=adresses[i]
        dt=datetime.now().strftime('%y-%m-%d')
        name='saves/' + str(dt) + '-' + str(i) + '.jpg'
        urllib.request.urlretrieve(location, name)
