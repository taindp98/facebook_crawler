import json
import utils
import requests
import urllib.request
import os
import urllib
import re
from time import sleep
from selenium import webdriver
import csv
def init_browser(url):
    # options = Options()
    global browser
    browser=webdriver.Firefox(executable_path="../geckodriver")
    browser.get(url)
    sleep(2)
    print('Initial browser...')
def login(email,password):
    browser.find_element_by_xpath("//input[@name='email']").send_keys(email)
    browser.find_element_by_xpath("//input[@name='pass']").send_keys(password)
    sleep(2)
    browser.find_element_by_xpath("//div[@aria-label='Accessible login button']").click()
    sleep(2)
    print('Login...')
# get element
def get_post_id(post_element):
    re_token1=r'\(.*?\)'
    re_token2=r'\".*?\"'
    post2str = str(post_element)
    postele = str(re.findall(re_token1,post2str)[0]).replace(r'(',r'').replace(r')',r'')
    id = str(re.findall(re_token2,str(postele.split(',')[-1]))[0]).replace(r'"',r'')
    return id

def press_extra():
    posts = browser.find_elements_by_xpath("//div[@role='article']")
    for post in posts:
        extras = post.find_elements_by_xpath("//div[@role='button']")
        if extras:
            for extra in extras:
                cnt = extra.get_attribute('innerHTML')
                if cnt == 'Xem thêm':
                    browser.execute_script("arguments[0].click();", extra)
    print('Page extra..')
def scroll_page():
    # scroll ---> extra page
    sleep(1)
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    print('Scrolling...')
    sleep(1)
    press_extra()
    print('Scrolled...')
    return True
def save_img(id,urls,path):
    folder = os.path.join(path,id)
    if os.path.isdir(folder):
        for index,url in enumerate(urls):
            resource = urllib.request.urlopen(url)
            if os.path.isfile(os.path.join(folder,f'{id}'+'_'+f'{index}'+'.jpg')):
                continue
            else:
                with open(os.path.join(folder,f'{id}'+'_'+f'{index}'+'.jpg'), 'wb') as handler:
                    handler.write(resource.read())
    else:
        os.mkdir(folder)
        for index,url in enumerate(urls):
            resource = urllib.request.urlopen(url)
            if os.path.isfile(os.path.join(folder,f'{id}'+'_'+f'{index}'+'.jpg')):
                continue
            else:
                with open(os.path.join(folder,f'{id}'+'_'+f'{index}'+'.jpg'), 'wb') as handler:
                    handler.write(resource.read())
def get_post(time_scroll,path_folder_img):
    list_out = []
    cur_time = 0
    while True:
        if cur_time == time_scroll:
            break
        else:
            cur_time += 1
            print('Current time:{}'.format(cur_time))
            scrolled = scroll_page()
            try:
                if scrolled:
                    posts = browser.find_elements_by_xpath("//div[@role='article']")
                    for post in posts:
                        if post.get_attribute('aria-posinset'):
                            ids = str(post.get_attribute('aria-describedby')).split(' ')

                            dict_post = {}
                            group_contents = browser.find_element_by_id(ids[1])
                            group_img = browser.find_element_by_id(ids[2])
                            # print(len(group_img))
                            contents = group_contents.find_elements_by_tag_name('span')
                            imgs = group_img.find_elements_by_tag_name('img')
                            # print(len(group_img))
                            list_content = []
                            list_url_img = []
                            if len(imgs) >= 3:
                                dict_post['id'] = ids[1]
                                for txt in contents:
                                    if txt.text != '':
                                        list_content.append(txt.text)
                                dict_post['content'] = list_content
                                if len(list_content) > 0:
                                    for img in imgs:
                                        list_url_img.append(img.get_attribute('src'))
                                save_img(str(ids[1]),list_url_img,path_folder_img)
                                dict_post['url_img'] = list_url_img
                            if len(dict_post['url_img']) > 0 and dict_post not in list_out:
                                list_out.append(dict_post)
            except:
                continue
    return list_out



if __name__== '__main__':
    # url = 'https://www.facebook.com/groups/2285293311800666/'
    url =   'https://www.facebook.com/lyn.pe.56'
    path_out = '/home/taindp/sssmarket/instagram_crawler/facebook-crawler/data/data_crawler.csv'
    path_folder_img = '/home/taindp/sssmarket/instagram_crawler/facebook-crawler/data/img/'
    email = '0936146453'
    password = 'ssstech2020'
    time_scroll = 5
    init_browser(url)
    login(email,password)
    dict_crawl = (get_post(time_scroll,path_folder_img))
    csv_columns = ['id','content','url_img']
    with open(path_out, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_crawl:
            with open(path_out,'r') as file1:
                existingLines = [line for line in csv.reader(file1, delimiter=',')]
                print(len(existingLines))
                if data not in existingLines:
                    writer.writerow(data)
    browser.close()
