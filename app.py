import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# === 観測地点の設定（松江の例） ===
PREC_NO = "68"
BLOCK_NO = "47741"

def get_jma_hourly_excel(year: int, month: int, day: int):
    """気象庁サイトから指定日の1時間ごとのデータを取得し、Excelデータを返す"""

    # JMAのURL
    base_url = "https://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php"
    params = {
        "prec_no": PREC_NO,
        "block_no": BLOCK_NO,
        "year": year,
        "month": f"{month:02d}",
        "day": f"{day:02d}",
        "view": "p1",
    }

    # ブラウザっぽく見せるヘッダ
    headers = {"User-Agent": "Mozilla/5.0"}

    # ページ取得
    r = requests.get(base_url, params=params, headers=headers)
    r.encoding = r.apparent_encoding

    # HTML からテーブルを読み込み
    dfs = pd.read_html(r.text)
    df = dfs[0]

    # 列名がMultiIndex（2段組）になっている場合は、下の行だけ使う
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)

    # Excel をメモリ上に書き出し
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    filename = f"matsue_{year}{month:02d}{day:02d}_hourly.xlsx"
    return filename, buffer


# ================= Streamlit の画面部分 =================

st.title("気象庁 松江 1時間ごとの気象データ Excel 出力")

st.write("日付を選んで「Excel を作る」を押すと、その日のデータを Excel 形式でダウンロードできます。")

# 日付入力
selected_date = st.date_input("日付を選んでください")

if st.button("Excel を作る"):
    with st.spinner("気象庁サイトからデータを取得中…"):
        try:
            fname, excel_bytes = get_jma_hourly_excel(
                selected_date.year,
                selected_date.month,
                selected_date.day,
            )
        except Exception as e:
            st.error(f"データ取得に失敗しました: {e}")
        else:
            st.success("Excel ファイルの準備ができました。下のボタンからダウンロードしてください。")
            st.download_button(
                label="Excel ダウンロード",
                data=excel_bytes,
                file_name= fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
