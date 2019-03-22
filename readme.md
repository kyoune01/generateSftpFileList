# sftp（鍵なし）サーバからファイルリストを作成します。
## 必要なファイル
・list.txt -> 設定の記述場所
・sftp.exe -> 実行ファイル
## 使い方
list.txt に設定を記述してください。（下記）  
list.txt　に記述したら sftp.exe　を実行してください。  
res.csv と log.txt が必ず吐き出されます。  
res.csv には　ファイルパス・パーミッション・所有者　を記載してます。  
## 設定書き方
［1行目］IPアドレス  
［2行目］ID  
［3行目］パスワード  
［4行目］調査開始したい場所  

例：  
192.168.1.1  
userID  
passwd  
/  

※1行目：サーバーがDHCP対応してるなら名前解決もしてくれるかも  
※4行目：初期ログイン箇所をルートとします。
