#-*- coding: utf-8 -*-

import time
import random
import json
from urllib import parse

from selenium import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from webdriver_manager.chrome import ChromeDriverManager


ACCOUNT_LOGIN_PATH = 'https://www.instagram.com/accounts/login/'
EXPLORE_TAGS_PATH = 'https://www.instagram.com/explore/tags/{}/'

SCROLLING_SCRIPT = 'window.scrollTo(0,document.body.scrollHeight)'

LIMIT_ARTICLE_INTERACTIVE_COUNT = 30 # 한 계정당 최대 30개 게시글 접근
LIMIT_PAGING_COUNT = 3 # 최대 3번 다운 스크롤
ERROR_COOLING_TIME = 60 # 에러시 60초간 휴식

META_FILE_PATH = './meta.json'

USERNAME_FIELD_NAME = 'username'
PASSWROD_FIELD_NAME = 'password'
ARTICLE_AREA_CLASS_NAME = '_aao7'
LIKE_BUTTON_CLASS_NAME = '_abl_'
ARTICLE_DETAIL_BUTTON = '_acan._acao._acas'
FOLLOW_DIV_CLASS_NAME = '_aacl._aaco._aacw._adda._aad6._aade'

class InstagramBot:

    def __init__(self, username, password):   #Constructor for InstaBot class
        self.username = username
        self.password = password
        self.bot = webdriver.Chrome(ChromeDriverManager().install())

    def login(self):
        print("[🔐 ACTION] {} Login".format(self.username))
        self.bot.get(ACCOUNT_LOGIN_PATH)
        
        self.random_sleep(5)

        email = self.bot.find_element(By.NAME, USERNAME_FIELD_NAME)
        password = self.bot.find_element(By.NAME, PASSWROD_FIELD_NAME)
        
        email.clear()
        password.clear()
        email.send_keys(self.username)
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)

        self.random_sleep(3)

    def random_sleep(self, min_time):
        rand_diff_time = random.randrange(1, 3)
        time.sleep(min_time + rand_diff_time)

    def tags_url_with_hashtag(self, hashtag):
        return EXPLORE_TAGS_PATH.format(parse.quote(hashtag))

    def scroll_to_bottom(self):
        print("[🎯 ACTION] Scrolling")
        self.bot.execute_script(SCROLLING_SCRIPT)
        self.random_sleep(2)

    def get_article_links(self):
        # we get links in the format of instagram.com/p/id
        try:
            article = self.bot.find_element(By.CLASS_NAME, ARTICLE_AREA_CLASS_NAME)
            atags = article.find_elements(By.TAG_NAME, 'a')
            links = [atag.get_attribute('href') for atag in atags]
            return links
        except Exception as ex:
            print("[❌ ACTION] {} element not found".format(ARTICLE_AREA_CLASS_NAME))
            return []

    def is_executable(self):
        return random.choice([True, False]) == True
    
    def open_article_detail(self, link):
        self.bot.get(link)
        self.random_sleep(5)

    def random_like(self):
        if self.is_executable() == False:
            print("[⛔ ACTION] skip like (i'm not a robot)")
            return False
        
        try:
            like_button = self.bot.find_element(By.CLASS_NAME, LIKE_BUTTON_CLASS_NAME)
            like_button.click()
            print("[✅ ACTION] like success")
            return True
        except Exception as ex:
            print("[❌ ACTION] already liked")
            return False
    
    def random_follow(self):
        if self.is_executable() == False:
            print("[⛔ ACTION] skip follow (i'm not a robot)")
            return False
        
        article_detail_buttons = self.bot.find_elements(By.CLASS_NAME, ARTICLE_DETAIL_BUTTON)
        for button in article_detail_buttons:
            try:
                self.bot.find_element(By.CLASS_NAME, FOLLOW_DIV_CLASS_NAME)
                button.click()
                print("[✅ ACTION] follow success")
                return
            except Exception as ex:
                pass
        
        print("[❌ ACTION] already follow")
        return False 
        
    def run(self, hashtag):
        count = 0
        total_like_count = 0
        total_follow_count = 0
        
        url = self.tags_url_with_hashtag(hashtag)
        self.bot.get(url)
        self.random_sleep(5)

        for i in range(LIMIT_PAGING_COUNT - 1):
            self.scroll_to_bottom()
            links = self.get_article_links()

            for link in links:
                count += 1
                if count == LIMIT_ARTICLE_INTERACTIVE_COUNT:
                    self.bot.close()
                    return
                else:
                    try:
                        self.open_article_detail(link)
                        if self.random_like():
                            total_like_count += 1
                        if self.random_follow():
                            total_follow_count += 1
                    except Exception as ex:
                        self.random_sleep(ERROR_COOLING_TIME)
        
        print("[✅ Output] {}'s settlement:\ntotal follow count: {}, total like count: {} 🎉".format(self.username, total_follow_count, total_like_count))
      
class InstagramBotWorker:

    def __init__(self):
        with open(META_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.accounts = data["accounts"] # List<object>
            self.tags = data["tags"] # List<string>

    def execute(self):
        print("[🔭 INFO] total account count: {}".format(len(self.accounts)))
        print("[🔭 INFO] total tag count: {}".format(len(self.tags)))

        for account in self.accounts:
            bot = InstagramBot(account["id"], account["password"])
            bot.login()
            for tag in self.tags:
                print("[🔍 ACTION] Searching #{}".format(tag))
                bot.run(tag)
                time.sleep(3)
            print("[🔒 ACTION] {} Logout".format(account["id"]))
            time.sleep(3)
        
# Run
worker = InstagramBotWorker()
worker.execute()