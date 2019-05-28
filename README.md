# 家計簿ビューア
## 概要
* エクセルで作成した家計簿を[こちら](https://yutatera.github.io/kakeibo/templates/)のように見ることができます。

## 入力
#### エクセルで作成した家計簿
* エクセルのテーブルは以下のカラムを含む必要があります。
  * yyyymm
  * 分類
  * 入金
  * 残高

* イメージは以下の通りです。

|yyyymm|dd|品名|分類|入金|出金|残高|
|---|---|---|---|---|---|---|
|201704|1|||||6978|
|201704|15|りんご|食料品||200|6778|
|201704|18|専門書|教育教養||1500|5278|
|201704|20|ATMで引き出し|移動|50000||555278|
|...|...|...|...|...|...|...|

* 複数、口座、財布がある場合は複数のシートに記述します。
* サンプルは[こちら](https://github.com/yutatera/kakeibo/blob/master/sample/kakeibo.xlsx)です。

#### 設定ファイル
* ビューアで表示する期間や、収入、支出の項目をyaml形式で記載します。
* サンプルは[こちら](https://github.com/yutatera/kakeibo/blob/master/sample/config.yaml)です。

## 実行環境構築
* Anacondaでpythonをインストール
* Anaconda Promptを開き以下を実行
  * `pip install tqdm`
  * `pip install pandas`
  * `pip install flask`
  
## ビューア実行方法
1. doServer.batをダブルクリック
1. shortcutをダブルクリック
