# Flavius API
FlaviusへAPI接続するためのパッケージ

## インストール
```shell
pip install flavius-api
```

## 動作環境
* Python3.6以上

## パケージの基本動作
FlaviusのAPIに対してPOSTメソッドにて通信を行います。

## 実装方法

```python
from flavius_api.api import FlaviusDto, FlaviusItem, FlaviusEnvironment, FlaviusPage


FlaviusDto.endpoint = endpoint
FlaviusDto.endpoint_dev = endpoint
flavius_dto = FlaviusDto()

query = {
    'target': 'page',
    'order[sort]': 'ASC',
    'filter_field[]': [],
    'filter_value[]': [],
}
query['filter_field[]'].append('parent')
query['filter_value[]'].append(env['value'])

items = flavius_dto.search(query)
```

### ```endpoint```と```endpoint_dev```について
```Django```の```DEBUG```の値を参照し、どちらの```URL```を実行するか判断しています。

* ```DEBUG = True```：```endpoint_dev```
* ```DEBUG = False```：```endpoint```

```Django```の```settings.py```で接続先のURLを指定することもできます。

| 設定項目 | 値 |
| -------- | ---- |
| ```FLAVIUS_ENDPOINT``` | 本番環境URL |
| ```FLAVIUS_ENDPOINT_DEV``` | 開発環境URL |

### 設定するFlaviusのURLについて
```URL```を設定する場合、```ipos/```までを含んだ文字列を設定します。

```ex: http://sample.flavius2008.com/ipos/```

## API一覧
現在利用可能なAPIは下記の通り

| class名 | 対象データ | create | edit | delete | search | 備考 |
| ------- | -------- | ------ | ---- | ------ | ------ | ---- |
| FlaviusBackData | backdata | × | × | × | ◯ |  |
| FlaviusDto | ※ | × | × | × | ◯ | パラメータにテーブル名を設定することで<br />Flaviusの任意のテーブルからデータを取得できます。 |
| FlaviusDtoFetch | ※ | × | × | × | ◯ | パラメータにテーブル名を設定することで<br />Flaviusの任意のテーブルからデータを```1件```取得できます。 |
| FlaviusItem | item | ◯ | ◯ | × | ◯ |  | 
| FlaviusEnvironment | environment | ◯ | ◯ | × | ◯ |  |
| FlaviusSort | sort | × | × | × | ◯ |  |
| FlaviusHeader | header | ◯ | ◯ | × | ◯ |  |
| FlaviusData | data | ◯ | ◯ | ◯ | × |  |
| FlaviusPage | page | × | × | × | ◯ |  |
| FlaviusOrderDecide | - | × | ◯ | × | × | オーダー送信用のAPI |
| FlaviusCreditAdd | data | ◯ | × | × | × | クレジット支払用の明細追加API |
| FlaviusPaymentComplete | - | × | ◯ | × | × | 売上伝票完了API |
| FlaviusPickupLocation | pickup_location | ◯ | ◯ | ◯ | ◯ |  |
| FlaviusPickupTime | pickup_time | ◯ | ◯ | ◯ | ◯ |  |
| FlaviusHeaderExtPickup| header_ext_pickup | ◯ | ◯ | ◯ | ◯ |  |
| FlaviusPickupLocationFileUpload | pickup_location | ◯ | × | × | × | 画像ファイルアップロード用API |
