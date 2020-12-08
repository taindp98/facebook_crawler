import json
import requests
import urllib.request
import os
import urllib
import re
from time import sleep
from selenium import webdriver
import csv
import sys
from datetime import date,datetime
def init_browser(url):
    # options = Options()
    global browser
    browser=webdriver.Firefox(executable_path="../geckodriver")
    browser.get(url)
    sleep(2)
    print('Initial browser...')
def login(email,password):
    # sleep(2)
    # browser.refresh()
    browser.find_element_by_xpath("//input[@name='email']").send_keys(email)
    browser.find_element_by_xpath("//input[@name='pass']").send_keys(password)
    sleep(1)
    # if browser.find_element_by_xpath("//input[@aria-label='Đăng nhập']"):
    #     browser.find_element_by_xpath("//input[@aria-label='Đăng nhập']").click()
    # elif browser.find_element_by_xpath("//div[@aria-label='Accessible login button']"):
    #     browser.find_element_by_xpath("//div[@aria-label='Accessible login button']").click()
    if browser.find_element_by_xpath("//button[@name='login']"):
        browser.find_element_by_xpath("//button[@name='login']").click()
    else:
        sys.exit()
    print('Login...')
# get element
def find_page(name_page):
    sleep(0.5)
    findbox = browser.find_element_by_xpath("//input[@role='combobox']")
    sleep(2)
    findbox.send_keys(name_page)

    sleep(1)

    sel_page1 = browser.find_elements_by_xpath("//li[@role='option']")
    sel_page1[0].click()
    sleep(2)
    sel_page2 = browser.find_elements_by_xpath("//a[@role='presentation']")
    sel_page2[0].click()
    sleep(0.5)
    browser.refresh()
def get_post_id(post_element):
    re_token1=r'\(.*?\)'
    re_token2=r'\".*?\"'
    post2str = str(post_element)
    postele = str(re.findall(re_token1,post2str)[0]).replace(r'(',r'').replace(r')',r'')
    id = str(re.findall(re_token2,str(postele.split(',')[-1]))[0]).replace(r'"',r'')
    return id

def press_extra():
    posts = browser.find_elements_by_xpath("//div[@role='article']")
    # print(len(posts))
    sleep(1)
    for post in posts:
        try:
            extras = post.find_elements_by_xpath("//div[@role='button']")
            if extras:
                for extra in extras:
                    # cnt = extra.get_attribute('innerHTML')
                    cnt = extra.get_attribute('innerHTML')
                    if str(cnt).startswith('Xem thêm'):
                        browser.execute_script("arguments[0].click();", extra)
        except:
            continue
    print('Page extra..')
def scroll_page():
    # scroll ---> extra page
    sleep(2)
    last_height = browser.execute_script("return document.body.scrollHeight")
    # browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    new_height = browser.execute_script('window.scrollTo(0, window.scrollY + 1096);')
    # if new_height == last_height:
    #     sys.exit()
    print('Scrolling...')
    sleep(2)
    press_extra()
    print('Scrolled...')
    return True

# def save_img(id,urls,path):
#     folder = os.path.join(path,id)
#     if os.path.isdir(folder):
#         for index,url in enumerate(urls):
#             resource = urllib.request.urlopen(url)
#             if os.path.isfile(os.path.join(folder,f'{id}'+'_'+f'{index}'+'.jpg')):
#                 continue
#             else:
#                 with open(os.path.join(folder,f'{id}'+'_'+f'{index}'+'.jpg'), 'wb') as handler:
#                     handler.write(resource.read())
#     else:
#         os.mkdir(folder)
#         for index,url in enumerate(urls):
#             resource = urllib.request.urlopen(url)
#             if os.path.isfile(os.path.join(folder,f'{id}'+'_'+f'{index}'+'.jpg')):
#                 continue
#             else:
#                 with open(os.path.join(folder,f'{id}'+'_'+f'{index}'+'.jpg'), 'wb') as handler:
#                     handler.write(resource.read())
def get_post(time_scroll,url):
    browser.get(url)
    # today = date.today()
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S").replace(r'/',r'_').replace(r':',r'_').replace(r' ',r'_')
    if not os.path.isdir(f'/home/taindp/sssmarket/instagram_crawler/facebook-crawler/data/{dt_string}'):
        os.mkdir(f'/home/taindp/sssmarket/instagram_crawler/facebook-crawler/data/{dt_string}')
    path_out = f'/home/taindp/sssmarket/instagram_crawler/facebook-crawler/data/{dt_string}/data_crawler.json'
    # list_out = []

    memory = []
    cur_time = 0
    while True:
        if cur_time == time_scroll:
            break
        else:
            cur_time += 1
            print('Current time:{}'.format(cur_time))
            scrolled = scroll_page()
            # try:
            if scrolled:
                # print(scrolled)
                posts = browser.find_elements_by_xpath("//div[@role='article']")
                for post in posts:
                    dict_post = {}
                    if post.get_attribute('aria-posinset'):
                        ids = str(post.get_attribute('aria-describedby')).split(' ')
                        # mỗi ids[] gồm post,content,ảnh,cmt
                        # print(ids[0])
                        if ids[1] not in memory:
                            memory.append(ids[1])
                            # group_contents = browser.find_element_by_id(ids[1])
                            # group_contents = browser.find_element_by_xpath(f"//div[@id='{ids[1]}' and @data-ad-preview='message']")
                            group_img = browser.find_element_by_id(ids[2])
                            # print(len(group_img))
                            contents = browser.find_elements_by_xpath(f"//div[@id='{ids[1]}' and @data-ad-preview='message']//div[@style='text-align: start;']")
                            # contents = group_contents.find_elements_by_xpath('/')
                            imgs = group_img.find_elements_by_tag_name('img')
                            # print(imgs)
                            # print("contents",contents)
                            list_content = []
                            list_url_img = []
                            if len(imgs) >= 1:
                                dict_post['id'] = ids[1]
                                for txt in contents:
                                    # print(ids[1])
                                    # print(txt.text)
                                    if txt.text != '':
                                        list_content.append(txt.text)

                                dict_post['content'] = list_content

                                # print(list_content)
                                # if len(list_content) > 0:
                                for img in imgs:
                                    list_url_img.append(img.get_attribute('src'))
                                # print(list_url_img)
                                # save_img(str(ids[1]),list_url_img,path_folder_img)
                                dict_post['url_img'] = list_url_img
                                # print(dict_post)
                                with open(path_out, 'a') as jsonfile:
                                    dict2str = str(dict_post).replace(r"'",r'"')
                                    jsonfile.write(dict2str)
                                    jsonfile.write('\n')



if __name__== '__main__':
    email = '0936146453'
    password = 'ssstech2020'
    time_scroll = 2
    url = 'https://www.facebook.com/'
    init_browser(url)
    login(email,password)
    url = 'https://www.facebook.com/lyn.pe.56'
    get_post(time_scroll,url)
    browser.close()
