# US_stock

簡短說明  
這個專案從 CSV（預設 `US_stocks.csv`）讀取股票代號、成本與自選股標記（欄位: Ticker, Cost, Custom），並使用 pandas 印出 DataFrame（若檔案不存在，程式會建立範例 CSV）。程式也可擴充為抓取即時價格（目前 main.py 已保留 yfinance 呼叫）。

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
pip install -r d:\<your_project_dir>\requirements.txt
```
3. 執行（預設讀取 US_stocks.csv）
```powershell
python d:\<your_project_dir>\main.py
# 或指定檔案
python d:\<your_project_dir>\main.py myfile.csv
```

功能更新 (v0.1.0)
- 支援「自選股」標記：Custom 欄位為 1 表示自選股，非自選股留空
- 可選擇輸出 CSV（程式執行時會詢問 y/n）
- 更新接近目標階段判斷規則：
    - 停損優先
    - 超過長期 → 接近長期 → 超過中期 → 接近中期 → 超過短期 → 接近短期
    - 未達短線目標為兜底
- 輸出股票自動按字母排序

備註
- 若 main.py 使用 yfinance 抓價，需要可用的網路連線與 yfinance。
- 範例 CSV 檔名：US_stocks.csv（若不存在，程式會自動建立）。