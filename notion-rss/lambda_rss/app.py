import os
import json
import boto3
import base64
from botocore.exceptions import ClientError
import ast
from typing import List
import time
import feedparser


def lambda_handler(event, context):

    ## AWS Secrets Managerに設定しているNotionのシークレットを取得する
    notion_token = get_secrets_manager_key_value('notion_rss', 'NOTION_TOKEN')
    ## AWS Secrets Managerに設定しているNotionのシークレットを取得する
    database_id = get_secrets_manager_key_value('notion_rss', 'DATABASE_ID')
    rss_url_list = get_target_url()
    rss_list: List[RssContent] = []
    print(rss_url_list)
    for url in rss_url_list:
        #rss_list += get_rss(url, interval=60)
    #        d_rss_feed = feedparser.parse(rss_url_list)
        d_rss_feed = feedparser.parse(rss_url_list)
        print(d_rss_feed.feed.title)
        print(d_rss_feed.feed.link)
        print(url)
    #        print(f"target_url:{url}")
    #        print(f"feed_length{str(len(rss_list))}")



    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello",
            # "location": ip.text.replace("\n", "")
        }),
    }

def get_secrets_manager_key_value(secret_name: str, secret_key: str) -> str:
    """AWS Secrets Managerからシークレットキーの値を取得する."""
    value = ''
    secrets_dict = get_secrets_manager_dict(secret_name)
    if secrets_dict:
        if secret_key in secrets_dict:
            # secrets_dictが設定されていてsecret_keyがキーとして存在する場合
            value = secrets_dict[secret_key]
        else:
            print('シークレットキーの値取得失敗：シークレットの名前={}、シークレットキー={}'.format(secret_name, secret_key))
    return value

def get_secrets_manager_dict(secret_name: str) -> dict:
    """Secrets Managerからシークレットのセットを辞書型で取得する"""
    region_name = "ap-northeast-1"

    secrets_dict = {}
    if not secret_name:
        print('シークレットの名前未設定')
    else:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            print('シークレット取得失敗：シークレットの名前={}'.format(secret_name))
            print(e.response['Error'])
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
            else:
                secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            secrets_dict = ast.literal_eval(secret)
    return secrets_dict

def get_target_url() -> List[str]:
    """
    取得対象にするrssのURLを返却する
    """
    region_name = "ap-northeast-1"
    ssm = boto3.client('ssm',region_name=region_name)

    url_param: str = ssm.get_parameter(
        Name='RSSURLList'
    )['Parameter']['Value']
    # url_paramには改行区切りでURLが保存されているので、改行で分割して出力
    url_list: List[str] = url_param.split("\n")
    return url_list
