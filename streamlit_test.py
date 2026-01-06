import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="CSV/Excel 表示アプリ（Streamlit版）", layout="wide")
st.title("CSV/Excel 表示アプリ（Streamlit版）")

uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択", type=["csv", "xlsx"])

if uploaded_file:
    header_keywords = ['公報番号']
    encodings = ['utf-8-sig', 'utf-8', 'cp932']
    df = None

    try:
        if uploaded_file.name.lower().endswith(".csv"):
            raw_bytes = uploaded_file.read()

            for enc in encodings:
                try:
                    text = raw_bytes.decode(enc)
                except Exception:
                    continue

                lines = text.splitlines()
                header_index = None
                for i, line in enumerate(lines[:10]):  # 先頭10行まで探索
                    if any(kw in line for kw in header_keywords):
                        header_index = i
                        break

                try:
                    if header_index is not None:
                        csv_text = "\n".join(lines[header_index:])
                        df = pd.read_csv(StringIO(csv_text), sep=",", engine="python", dtype=str, on_bad_lines="skip", index_col=False)
                    else:
                        df = pd.read_csv(StringIO(text), sep=",", engine="python", dtype=str, on_bad_lines="skip", index_col=False)
                    st.success(f"エンコーディング: {enc}, ヘッダー行: {header_index}")
                    break
                except Exception as e:
                    st.warning(f"{enc} での読み込み失敗: {e}")
                    df = None
                    continue

            if df is None:
                uploaded_file.seek(0)  # ★ ここが重要（先頭に戻す）
                try:
                    df = pd.read_csv(uploaded_file, dtype=str, on_bad_lines="skip", encoding=enc, engine="python")
                except Exception as e:
                    st.error(f"最終読み込み失敗: {e}")
                    df = pd.DataFrame()
        else:
            df = pd.read_excel(uploaded_file, dtype=str)

        if df is not None:
            df = df.fillna("")
            # st.dataframe(df, width='content')
            st.dataframe(df, use_container_width=True)

    except Exception as ex:
        st.error(f"読み込みエラー: {ex}")
