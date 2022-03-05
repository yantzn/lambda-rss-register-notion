import boto3
from typing import List
import json

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
    json_dict = json.loads(url_param)
    return json_dict
