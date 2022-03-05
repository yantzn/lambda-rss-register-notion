import boto3
import base64
from botocore.exceptions import ClientError
import ast

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
