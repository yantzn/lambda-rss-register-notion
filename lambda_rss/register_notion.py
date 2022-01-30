from typing import List
from get_secrets import get_secrets_manager_key_value
from notion_client import Client

def register_notion(rss_list:dict) -> None:
    """
    Notionの指定したデータベースに記事のタイトル、タグ、URLを登録する
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

            ## Notionに登録を行う
            notion.pages.create(
                **{
                    'parent': { 'database_id': database_id},
                    'properties': {
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
                }
            )

    except Exception as error:
        raise Exception(error)
