# Linguaporta-Killer

LinguaportaをSeleniumを用いて自動化しました。

`ALL-ROUND TRAINING FOR THE TOEIC(R) L&R TEST(TOEIC(R) L&R TEST オールラウンド演習)`のみに対応しています

## 使用方法

chromeをインストールしてください

pythonを導入してください

user_data.jsonに自分のIDとPASS、Pageとmodeを入力してください。

Pageは始めたいページ番号 (1推奨)

modeは自動周回するユニットです。
- `mode = 1` 「単語・語句の意味」「空所補充」「音声を聞いて読み取り」の答えを収集、入力します
- `mode = 2` 「単語の並び替え」の答えを収集します。入力はできません

`pip install -r requirements.txt`

`python linguaporta_auto.py`

で起動できます

## エラー

`chromedriver.exe`のバージョンによりエラーが起きる可能性があります。

ここから自分のchromeに合うバージョンをインストールして、置き換えてください。

https://chromedriver.chromium.org/downloads

