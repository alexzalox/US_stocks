import argparse
import os
import csv
from typing import Optional
from datetime import datetime

import pandas as pd
import yfinance as yf

# ====== 設定區 (可自由調整) ======
DEFAULT_CSV = "US_stocks.csv"
SAMPLE_STOCKS = [("AAPL", 233.91, 1)]

# 接近目標階段判斷規則 (依序檢查，第一個符合的就採用)
STAGE_RULES = [
    (lambda p, s, st, mt, lt: p is None, "❌ 無法取得現價"),
    (lambda p, s, st, mt, lt: p <= s, "🛑 觸發停損"),
    (lambda p, s, st, mt, lt: p >= lt, "🎉 超過長期目標"),
    (lambda p, s, st, mt, lt: p >= lt * 0.95, "🚀 接近長期目標"),
    (lambda p, s, st, mt, lt: p >= mt, "🎯 超過中期目標"),
    (lambda p, s, st, mt, lt: p >= mt * 0.95, "📈 接近中期目標"),
    (lambda p, s, st, mt, lt: p >= st, "✅ 超過短期目標"),
    (lambda p, s, st, mt, lt: p >= st * 0.95, "⚡ 接近短期目標"),
]
# =================================


def ensure_sample(path: str) -> None:
    if os.path.exists(path):
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Ticker", "Cost", "Custom"])
        w.writerows(SAMPLE_STOCKS)
    print(f"範例檔已建立：{path}")


def fetch_price(ticker: str) -> Optional[float]:
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d", actions=False)
        if hist.empty or "Close" not in hist.columns:
            return None
        close = hist["Close"].dropna()
        return float(close.iloc[-1]) if not close.empty else None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="從 CSV 讀取股票與成本，抓取現價並印出表格（不輸出檔案）。"
    )
    parser.add_argument(
        "csv", nargs="?", default=DEFAULT_CSV, help="輸入 CSV，欄位: Ticker,Cost,Custom"
    )
    args = parser.parse_args()

    ensure_sample(args.csv)
    df_in = pd.read_csv(args.csv, dtype={"Ticker": str, "Cost": float})
    df_in = df_in.dropna(subset=["Ticker", "Cost"])
    df_in["Ticker"] = df_in["Ticker"].str.strip().str.upper()

    # 統一欄位名稱，避免大小寫或空格問題
    df_in.columns = df_in.columns.str.strip().str.capitalize()

    # 去除重複的 Ticker，並提示使用者
    dup = df_in[df_in.duplicated(subset=["Ticker"], keep=False)]
    if not dup.empty:
        unique_dup_tickers = sorted(dup["Ticker"].unique())
        print(
            f"警告：輸入檔包含重複的 Ticker(將只保留每個 Ticker 的第一筆）：{', '.join(unique_dup_tickers)}"
        )
    df_in = df_in.drop_duplicates(subset=["Ticker"], keep="first")

    # 股票按字母順序排序
    df_in = df_in.sort_values(by="Ticker").reset_index(drop=True)

    rows = []
    for _, r in df_in.iterrows():
        ticker = r["Ticker"]
        cost = float(r["Cost"])
        price = fetch_price(ticker)
        if price is not None:
            price = round(price, 2)

        short_t = round(cost * 1.28, 2)
        mid_t = round(cost * 1.65, 2)
        long_t = round(cost * 2.2, 2)
        stop = round(cost * 0.82, 2)

        # 使用規則判斷接近目標階段
        stage = None
        for cond, label in STAGE_RULES:
            if cond(price, stop, short_t, mid_t, long_t):
                stage = label
                break
        if stage is None:
            stage = "❌ 還未達短線目標"

        # 標記是否為自選股 (處理 1.0、1、空值等情況)
        custom_val = r.get("Custom", "")
        try:
            custom_flag = "自選股" if int(float(custom_val)) == 1 else ""
        except:
            custom_flag = ""

        rows.append(
            [ticker, cost, price, short_t, mid_t, long_t, stop, stage, custom_flag]
        )

    df_out = pd.DataFrame(
        rows,
        columns=[
            "股票",
            "成本價",
            "現價",
            "短線目標(+28%)",
            "中線目標(+65%)",
            "長期目標(+120%)",
            "停損價(-18%)",
            "接近目標階段",
            "自選股",
        ],
    )
    print(df_out.to_string(index=False))

    # 是否要輸出 CSV（加上今天日期）
    save = input("是否要產出 output.csv (y/n)? ").strip().lower()
    if save in {"y", "yes"}:
        today_str = datetime.today().strftime("%Y%m%d")
        output_filename = f"output_{today_str}.csv"
        df_out.to_csv(output_filename, index=False, encoding="utf-8-sig")
        print(f"已輸出：{output_filename}")
    else:
        print("canceled")


if __name__ == "__main__":
    main()
