# http-log-receiver

簡單的 HTTP POST 日誌伺服器，可將收到的訊息記錄到每日檔案，並提供網頁介面查看、下載或刪除日誌。

A simple HTTP POST log server that records incoming messages to daily log files and provides a web interface to view, download, or delete logs.

## 設定環境

```
sudo apt install -y python-is-python3 python3-pip
sudo mv /usr/lib/python3.12/EXTERNALLY-MANAGED /usr/lib/python3.12/EXTERNALLY-MANAGED.bak
pip install flask
```

## 啟用 log server

```
python http_log_server.py
```

## 測試指令

Client:

```bash
while true; do \
	curl -X POST http://<ipaddr>:8080/testlog -H "Content-Type: text/plain" --data "$(echo $RANDOM)"; \
	sleep 2; \
done
```

Server:

```
$ python http_log_server.py
 * Serving Flask app 'http_log_server'
 * Debug mode: off
[2025-09-09 19:14:57] 4865
[2025-09-09 19:14:59] 19284
[2025-09-09 19:15:01] 2155
[2025-09-09 19:15:03] 5983
[2025-09-09 19:15:06] 18048
```



## 查看 logs

```
http://<ipaddr>:8080/logs
```

![](webui.png)