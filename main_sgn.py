import sys
sys.path.append(sys.path[0]+'\selenium-fb\Lib\site-packages')

import pandas as pd
import re
import time
import datetime
import schedule
import requests
import random
from gsheetApi import play_with_gsheet, gsheet_build_service

# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# Credentials
import accounts

def standby(min=1, max=3):
    time.sleep(random.uniform(min,max))

def open_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--mute-audio")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    return driver

def login_fb(driver, account, password):
    driver.get('https://facebook.com')
    standby(3, 5)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(account)
    standby()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'pass'))).send_keys(password)
    standby()
    driver.switch_to.active_element.send_keys(Keys.RETURN)

def get_fb_posts(driver, groupId, kwBlacklist):
    if type(kwBlacklist) != 'list':
        kwBlacklist = list(kwBlacklist)
    kwBlacklist = '|'.join(kwBlacklist)

    dataframe = pd.DataFrame(columns=['phone', 'time', 'content', 'post', 'profile'])

    driver.get(f'https://facebook.com/groups/{groupId}?sorting_setting=CHRONOLOGICAL')
    posts = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'userContentWrapper')))
    for p in posts:
        if p.text.find('Vừa xong') != -1 or p.text.find('1 phút') != -1:
            try:
                p.find_element_by_class_name('see_more_link_inner').click()
            except: pass

            content = p.find_element_by_class_name('userContent').text

            if len(re.findall(r'(ứng \d+)|(ship \d+)', content)) != 0 and not re.findall(kwBlacklist, content, re.IGNORECASE):
                try:
                    profile = p.find_element_by_class_name('profileLink').get_attribute('href')
                except:
                    profile = p.find_element_by_link_text(p.find_element_by_class_name('_7tae').text).get_attribute('href')
                if profile.find('profile.php') == -1:
                    profile = profile.split('?')[0]
                else:
                    profile = profile.split('&')[0]

                try:
                    phone = re.search(r'([^0-9]+(0|84|\+84)[-.\s]?\d{1,3}[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4})', content).group()
                    phone = re.sub(r'\D+', '', phone)
                    phone = re.sub(r'^0', '84', phone)
                except:
                    phone = None
            
                try:
                    post = p.find_element_by_class_name('_5pcq').get_attribute('href')
                except:
                    break

                post_time = pd.to_datetime(p.find_element_by_class_name('_5ptz').get_attribute('data-utime'), unit='s') + pd.DateOffset(hour=16)

                dataframe = dataframe.append({'phone':phone, 'time':post_time, 'content':content,
                                              'post':post, 'profile':profile}, ignore_index=True)
            else: continue
    dataframe = dataframe.drop_duplicates(subset='post')
    return dataframe

def push_tele(df, botToken, teleId):
    for i in range(len(df)):
        profile = df.iloc[i]['profile']
        content = df.iloc[i]['content']
        phone = df.iloc[i]['phone']
        post = df.iloc[i]['post']
        staff = df.iloc[i]['staff']

        text = """
<b>NEW POST</b>
<b>Nội dung:</b> {content}
<b>Facebook:</b> {profile}
<b>Phone:</b> {phone}
<b>Link:</b> {post}
{staff}
    """.format(content=content, profile=profile, phone=phone, post=post, staff=staff)

        data = {
            'chat_id': teleId,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }

        try:
            requests.post("https://api.telegram.org/bot{token}/sendMessage".format(token=botToken), data=data)
        except:
            pass

def get_old_users():
    global oldUsersList
    dfOldUsers = play_with_gsheet(accounts.spreadsheetIdHubspot, 'Sheet1', first_time=True)
    oldUsersList = dfOldUsers.id
    return oldUsersList

def append_posts(spreadsheetId, df, service):
    play_with_gsheet(spreadsheetId, 'Sheet1', dataframe=df, method='append', first_time=False, service=service)

def assign_staff(df, staffList):
    global num
    staffCol = []
    for _ in range(len(df)):
        staffCol.append(staffList[num])
        if num < len(staffList) - 1:
            num += 1
        else: num = 0
    df = pd.concat([df, pd.Series(staffCol, name='staff')], axis=1, ignore_index=True)
    df.columns = ['phone', 'time', 'content', 'post', 'profile', 'staff']
    return df


fb_email = accounts.acc2
fb_pass = accounts.pass2

spreadsheetIdNoti = accounts.spreadsheetIdNotiSgn
spreadsheetIdLog = accounts.spreadsheetIdLogSgn
spreadsheetIdHubspot = accounts.spreadsheetIdHubspot

groupIdList = accounts.groupIdListSgn
staffList = accounts.staffListSgn
num = 0
kwBlacklist = ['bắn', 'mua']

oldUsersList = get_old_users()
schedule.every(30).minutes.do(get_old_users)

driver = open_browser()
login_fb(driver, fb_email, fb_pass)
standby()

while True:
    if datetime.datetime.now().time() >= datetime.time(18, 30) or datetime.datetime.now().time() < datetime.time(9, 29):
        driver.quit()
        sys.exit(0)
    for groupId in groupIdList:
        try:
            schedule.run_pending()
            service = gsheet_build_service()
            newPosts = get_fb_posts(driver, groupId, kwBlacklist)
            oldPostsList = play_with_gsheet(spreadsheetIdLog, 'Sheet1', first_time=False, service=service).post
            newPosts = newPosts[~newPosts.post.isin(oldPostsList)]
            indayPosts = play_with_gsheet(spreadsheetIdNoti, 'Sheet1', first_time=False, service=service)
            oldProfilesList = indayPosts.profile
            oldPhonesList = indayPosts.phone
            postsToStaff = newPosts[(~newPosts.profile.isin(oldProfilesList)) & (~newPosts.phone.isin(oldPhonesList)) &
                                    ((~newPosts.phone.isin(oldUsersList)) | (newPosts.phone.isna()))].drop_duplicates(subset='profile')
            postsToStaff = assign_staff(postsToStaff.reset_index(drop=True), staffList)
            append_posts(accounts.spreadsheetIdNotiSgn, postsToStaff, service)
            push_tele(postsToStaff, accounts.botToken, accounts.teleIdSgn)
            append_posts(accounts.spreadsheetIdLogSgn, newPosts, service)
            del newPosts, postsToStaff, oldPostsList, oldPhonesList
        except Exception as err:
            if type(err).__name__ in ['WebDriverException', 'NoSuchWindowException']:
                try:
                    driver.quit()
                except: pass
                driver = open_browser()
                login_fb(driver, fb_email, fb_pass)
            if type(err).__name__ != 'TimeoutException':
                err_text = f"SGN Error: {type(err).__name__}.\n{str(err)}"
                data = {
                    'chat_id': '807358017',
                    'text': err_text,
                    'parse_mode': 'HTML'
                }
                r = requests.post("https://api.telegram.org/bot{token}/sendMessage".format(token=accounts.botToken), data=data)
            continue