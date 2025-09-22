import argparse
import os
import csv
from typing import Optional

import pandas as pd
import yfinance as yf

DEFAULT_CSV = "US_stocks.csv"
SAMPLE_STOCKS = [
    ("ABAT", 3.28),
    ("LXRX", 1.2),
    ("NITO", 5.21),
    ("BOXL", 5.45),
    ("AREC", 2.43),
    ("IONQ", 44.89),
    ("ONDS", 7.2),
    ("QRVO", 96.05),
    ("TMDX", 127.48),
    ("TSLA", 423.0),
    ("UEC", 12.6),
    ("UUUU", 13.67),
    ("ORCL", 304.81),
    ("LEU", 229.97),
    ("GOOG", 202.13),
    ("INTC", 31.38),
    ("FIGR", 38.89),
    ("CEG", 332.45),
    ("CHYM", 25.28),
    ("AAPL", 233.91),
    ("QBTS", 17.8),
    ("RGTI", 19.14),
    ("AVAV", 286.3),
    ("RCAT", 11.45),
]


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
