# NotionRSS

lambdaで取得した記事をNotionのデータベースに登録するアプリです。

## 構成図

![](/doc/aws.drawio.png)


## 準備

## AWS SAM 

SAM CLIを使用するには、次のツールをインストールしておく

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

### Notion integrationを作成

https://www.notion.so/my-integrations

「New Integration」からインテグレーションを作成する。

インテグレーションを作成したらInternal Integration Tokenをコピーしておく

![](/doc/integration.png)

### ワークスペースにインテグレーションを招待

共有から作成したインテグレーションを招待する

![](/doc/notion_Invite.png)

### データベースIDを取得する

URLの「?v」の前にある文字列部分を取得する

``` text
https://www.notion.so/{workspace_name}/{database_id}?v={view_id}
```

## AWS System Managerの設定

### 作成

* パラメータ名：RSSURLList
* 利用枠：標準
* タイプ：文字列
* データ型：text
* 値 (下記json参照)
   * url：記事の取得先URL
   * tag：Notionに記事登録時のタグ名称

``` json

{
  "rsslist": [
    {
      "url": "https://aws.amazon.com/jp/about-aws/whats-new/recent/feed/",
      "tag": "AWS"
    },
    {
      "url": "https://dev.classmethod.jp/feed/",
      "tag": "技術ブログ"
    }
  ]
}

```

## Secret Manegerの設定

### 作成

* シークレットのタイプ：その他のシークレットのタイプ
* キー/値のペア
  * NOTION_TOKEN：Integration Token
  * DATABASE_ID：データベースID
* 暗号化キー：DefaultEncryptionKey


## ビルド/実行/デプロイ


```bash
pip install -r lambda_notion_rss_register/requirements.txt
sam build --use-container
sam local invoke NotionRegisterFunction --event events/event.json
sam deploy --s3-bucket <your-s3-bucket-name>
```

## 実行結果

データベースに追加される

![](/doc/notion.png)

記事の内容がページに登録される

![](/doc/notion_page.png)
