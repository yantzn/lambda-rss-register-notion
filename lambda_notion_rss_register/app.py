import traceback
from typing import List
from get_target_url import get_target_url
from get_rss import get_rss
from register_notion import register_notion

def lambda_handler(event, context):

    try:
        ## RSSをAWS SSMから取得する
        rss_url_list = get_target_url()
        rss_list: List[RssContent] = []

        ## RSSから記事情報を取得する
        for url_list in rss_url_list["rsslist"]:
            rss_list += get_rss(url_list["url"], url_list["tag"], interval=60)

        # 新しい順に投稿するためソートする
        rss_list = sorted(rss_list, key=lambda x: x.published_date)

        ## 更新対象の記事がある場合、Notionに登録を行う
        if rss_list:
            register_notion(rss_list)

        return {"result": "OK"}

    except Exception as error:
        error_message = traceback.format_exc()
        return {"result": "NG", "error_message": error_message}
