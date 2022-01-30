from typing import List
import time
import feedparser
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

@dataclass
class RssContent():
    title: str
    url: str
    tag: str
    published_date: datetime

def get_rss(endpoint: str, tag: str, interval: int = 60) -> List[RssContent]:
    """
    rssのxmlを返すendpoint(url)からrss情報を取得し、必要な情報だけ抜き出す
    interval分以内の記事だけを返す。定期実行はinterval分と同じ間隔にすればよい
    intervalを負数にすると全記事返す(デバッグ用)
    """
    nowtime = datetime.now(timezone(timedelta(hours=+9), 'JST'))
    feed = feedparser.parse(endpoint)
    rss_list: List[RssContent] = []
    for entry in feed.entries:
        if not entry.get("link"):
            continue
        published = convert_time(entry.published_parsed)
        if (nowtime - published).total_seconds() // 60 <= interval or interval < 0:
            rss_content = RssContent(
                title=entry.title,
                url=entry.link,
                tag=tag,
                published_date=published
            )
            rss_list.append(rss_content)
    return rss_list

def convert_time(struct_time: time.struct_time) -> datetime:
    """
    time.struct_timeをdatetime.datetime(JST)に変換する
    feedparserがrss(XML)から返す日付がtime.struct_timeだが、そのままでは使いにくい
    """
    jst_zone = timezone(timedelta(hours=+9), 'Asia/Tokyo')
    converted_time = datetime(
        *struct_time[:6], tzinfo=timezone.utc).astimezone(jst_zone)
    return converted_time
