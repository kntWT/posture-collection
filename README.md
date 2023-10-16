## posture-correction

**〜概要〜**

- スマホからユーザの首の角度を取得するシステムのプロトタイプ（卒論）

**システム構成**

- 開発環境
  - Docker
    - Docker上でAngular + TypeScript，Python，MySQL，PHPMyAdminを動かしてる
  - GPUの関係上全てをDocker上で動かすことができないので，推定系はローカルで立ち上げて，Docker上のシステムで取得した画像から後で推定
- フロントエンド
  - [Angular](https://angular.io/)
  - [TypeScript](https://www.typescriptlang.org/)
  - [scss](https://sass-lang.com/)
- バックエンド
  - [Python](https://www.python.org/)
    - フレームワーク：[FastAPI](https://fastapi.tiangolo.com//)
- データベース
  - MySQL

### 設定ファイル
- `./.env`
  - ```
    MYSQL_HOST=mysql:3306
    MYSQL_DATABASE=posture_correction_db
    MYSQL_USER=ユーザ名
    MYSQL_PASSWORD=パスワード
    MYSQL_ROOT_PASSWORD=パスワード
    PMA_HOST=mysql
    PMA_USER=ユーザ名
    PMA_PASSWORD=パスワード
    TZ=Asia/Tokyo

    IMAGE_DIR=images
    ORIGINAL_IMAGE_DIR=images/original

    API_URL=http://api:8000
    API_ENDPOINT=/api/
    ```

### 開発で使用するポート一覧

|     | port | 説明                           | docker container 名 |
| :-: | ---- | :----------------------------- | ------------------- |
|     | 7150 | クライアント, Angular            | posture-correction-client       |
|     | 7151 | API, Python                        | posture-correction-api          |
|     | 7152 | データベース，   MySQL         | posture-correction-mysql        |
|     | 7153 | データベースの操作, PHPMyAdmin | posture-correction-phpmyadmin   |

