import os
import traceback
from typing import List
from get_secrets import get_secrets_manager_key_value
from bs4 import BeautifulSoup
import requests
from notion_client import Client, APIResponseError
import urllib.request, urllib.error

def register_notion(rss_list:dict) -> None:
    """
    Notionの指定したデータベースに記事のタイトル、タグ、URL、記事内容を登録する
    """

    try:

        ## AWS Secrets Managerに設定しているNotionのシークレットを取得する
        notion_token = get_secrets_manager_key_value('notion_rss', 'NOTION_TOKEN')

        ## AWS Secrets Managerに設定しているNotionのシークレットを取得する
        database_id = get_secrets_manager_key_value('notion_rss', 'DATABASE_ID')

        ## 認証を行う
        notion = Client(auth=notion_token)

        ## 取得したRSS数文登録を行う
        for rss in rss_list:

            block = []

            if not checkURL(rss.url):
                continue

            soup = BeautifulSoup(requests.get(rss.url).content, 'html.parser')

            articleTag = soup.find_all("div", {"class": "content"})

            if not articleTag:
                articleTag = soup.find_all(['section','article'])

            for article in articleTag:
                targetTags = article.find_all(['h1','h2','h3','p','span','img','li','pre','blockquote'])
                for tag in targetTags:
                    if tag.name == 'h1':
                        if tag.get_text(strip=True):
                            block.append(append_message("heading_1",tag.get_text(strip=True)))
                    if tag.name == 'h2':
                        if tag.get_text(strip=True):
                            block.append(append_message("heading_2",tag.get_text(strip=True)))
                    if tag.name == 'h3':
                        if tag.get_text(strip=True):
                            block.append(append_message("heading_3",tag.get_text(strip=True)))
                    if tag.name == 'li':
                        if tag.get_text(strip=True):
                            block.append(append_message("bulleted_list_item",tag.get_text(strip=True)))
                    if tag.name == 'p':
                        if tag.parent.name == 'blockquote':
                            continue
                        if tag.get_text(strip=True):
                            block.append(append_message("paragraph",tag.get_text(strip=True)))
                    if tag.name == 'img':
                        if checkURL(tag['src']) and checkExtension(tag['src']):
                                block.append(append_image(tag['src']))
                    if tag.name == 'pre':
                        if tag.get_text(strip=True):
                            block.append(append_code(tag.get_text(strip=True)))
                    if tag.name == 'blockquote':
                        if tag.get_text(strip=True):
                            block.append(append_message("quote",tag.get_text(strip=True)))
            ## Notionに登録を行う
            notion.pages.create(
                parent={'database_id': database_id},
                properties=property_data(rss),
                children=block
            )

    except APIResponseError as error:
        print('未登録：記事タイトル={}、記事URL={}'.format(rss.title, rss.url))
        print(block)
        error_message = traceback.format_exc()
        print("error_message:{}".format(error_message))
    except Exception as error:
        raise Exception(error)

def checkURL(url)->bool:
    try:
        f = urllib.request.urlopen(url)
        f.close()
        return True
    except:
        print ("NotFound URL:" + url)
        return False

def checkExtension(url)->bool:
    ext = os.path.splitext(url)
    chkTargetTxt = ['.png','.jpg','.jpeg','.gif','.tif','.tiff','.bmp','.svg','.heic']
    if ext[1] in chkTargetTxt:
        return True
    else:
        return False

def property_data(rss: str):
    return {
        'タイトル': {
            'title': [
                {
                    'text': {
                        'content': rss.title
                    }
                }
            ]
        },
        'タグ': {
            'multi_select':[
                {
                    "name": rss.tag
                }
            ]
        },
        'URL':{
            "url": rss.url
        }
    }


def append_message(key: str, message: str):
    return {
        "object": "block",
        "type": key,
        key: {
            "text": [{"type": "text", "text": {
                "content": message
            }}]
        }
    }

def append_code(message: str):
    return {
        "object": "block",
        "type": "code",
        "code": {
            "text": [{"type": "text", "text": {
                "content": message
            }}],
        "language": "plain text"
        }
    }

def append_image(url: str):
    return {
        "object": "block",
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": url
            }
        }
    }
