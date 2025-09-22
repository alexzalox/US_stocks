# US_stock

簡短說明  
這個專案從 CSV（預設 `US_stocks.csv`）讀取股票代號與成本（欄位: Ticker, Cost），並使用 pandas 印出 DataFrame（若檔案不存在，程式會建立範例 CSV）。程式也可擴充為抓取即時價格（目前 main.py 已保留 yfinance 呼叫）。

需求
- Windows
- Python 3.8+
- 套件：見 requirements.txt

快速上手（Windows）
1. 建立並啟用虛擬環境
```powershell
python -m venv .venv
.venv\Scripts\activate
```
2. 安裝相依套件
```powershell
pip install -r d:\workspace\US_stock\requirements.txt
```
3. 執行（預設讀取 US_stocks.csv）
```powershell
python d:\workspace\US_stock\main.py
# 或指定檔案
python d:\workspace\US_stock\main.py myfile.csv
```

備註
- 若 main.py 使用 yfinance 抓價，需要可用的網路連線與 yfinance。
- 範例 CSV 檔名：US_stocks.csv（若不存在，程式會自動建立）。