import argparse
import os
import csv
from typing import Optional

import pandas as pd
import yfinance as yf

DEFAULT_CSV = "US_stocks.csv"
SAMPLE_STOCKS = [("AAPL", 233.91)]


def ensure_sample(path: str) -> None:
    if os.path.exists(path):
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Ticker", "Cost"])
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
        "csv", nargs="?", default=DEFAULT_CSV, help="輸入 CSV，欄位: Ticker,Cost"
    )
    args = parser.parse_args()

    ensure_sample(args.csv)
    df_in = pd.read_csv(args.csv, dtype={"Ticker": str, "Cost": float})
    df_in = df_in.dropna(subset=["Ticker", "Cost"])
    df_in["Ticker"] = df_in["Ticker"].str.strip().str.upper()

    # 去除重複的 Ticker，並提示使用者
    dup = df_in[df_in.duplicated(subset=["Ticker"], keep=False)]
    if not dup.empty:
        unique_dup_tickers = sorted(dup["Ticker"].unique())
        print(f"警告：輸入檔包含重複的 Ticker（將只保留每個 Ticker 的第一筆）：{', '.join(unique_dup_tickers)}")
    df_in = df_in.drop_duplicates(subset=["Ticker"], keep="first")

    rows = []
    for _, r in df_in.iterrows():
        ticker = r["Ticker"]
        cost = float(r["Cost"])
        price = fetch_price(ticker)
        short_t = round(cost * 1.28, 2)
        mid_t = round(cost * 1.65, 2)
        long_t = round(cost * 2.2, 2)
        stop = round(cost * 0.82, 2)
        if price is None:
            stage = "❌ 無法取得現價"
        elif price >= long_t * 0.95:
            stage = "🚀 接近長期目標"
        elif price >= mid_t * 0.95:
            stage = "📈 接近中線目標"
        elif price >= short_t * 0.95:
            stage = "⚡ 接近短線目標"
        else:
            stage = "❌ 還未達短線目標"
        rows.append([ticker, cost, price, short_t, mid_t, long_t, stop, stage])

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
        ],
    )
    print(df_out.to_string(index=False))


if __name__ == "__main__":
    main()
