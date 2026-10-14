"""
電腦周邊 (鍵盤·滑鼠·耳機) 買家端售後與退換貨申請門戶
Buyer Portal for Computer Peripheral Returns & Warranty
獨立買家前台：與店長/老闆管理後台完全分離，確保商務機密安全
技術棧：Python + Streamlit + SQLite
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
from PIL import Image
import io

# ==========================================
# 0. 網頁基本配置與電競科技風視覺樣式 (CSS)
# ==========================================
st.set_page_config(
    page_title="電腦周邊售後客服中心 · 買家申請門戶",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入科技感電競深色主題 CSS，保持高對比度純白字體
CUSTOM_CSS = """
<style>
    /* 全域科技感微光漸層背景與微網格 */
    .stApp {
        background: 
            radial-gradient(circle at 12% 15%, rgba(56, 189, 248, 0.12) 0%, transparent 45%),
            radial-gradient(circle at 88% 18%, rgba(168, 85, 247, 0.14) 0%, transparent 45%),
            radial-gradient(circle at 50% 88%, rgba(34, 197, 94, 0.08) 0%, transparent 50%),
            linear-gradient(135deg, #090d16 0%, #0f172a 45%, #0a0f1d 100%) !important;
        background-attachment: fixed !important;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans TC", sans-serif !important;
    }

    /* 背景精緻科技微網格 */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 38px 38px;
        pointer-events: none;
        z-index: 0;
    }

    /* 文字色彩通盤加亮，杜絕暗字融入背景 */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    p, span, label, li {
        color: #f1f5f9;
    }

    /* 輸入框與文字區 placeholder 改為清晰明亮的淺銀白 */
    ::placeholder, ::-webkit-input-placeholder, ::-moz-placeholder, :-ms-input-placeholder,
    input::placeholder, textarea::placeholder {
        color: rgba(226, 232, 240, 0.72) !important;
        opacity: 1 !important;
    }

    /* 表單標籤文字純白 */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    label[data-testid="stWidgetLabel"],
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stFileUploader label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        letter-spacing: 0.2px;
    }

    /* 提示小字 (st.caption) 冰藍亮白 */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    .stCaption,
    .stCaption p {
        color: #93c5fd !important;
        font-size: 13.5px !important;
        line-height: 1.5 !important;
    }

    /* 輸入表單本體（打字文字白色、深黑科技背景、全面覆蓋 BaseWeb 杜絕反白） */
    .stTextInput input,
    .stTextArea textarea,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="input"] input,
    [data-baseweb="base-input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="input"],
    [data-baseweb="textarea"],
    [data-baseweb="base-input"],
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-size: 14.5px !important;
    }
    .stTextInput input:focus, 
    .stTextArea textarea:focus,
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.4) !important;
    }

    /* 檔案上傳器拖曳區文字與按鈕亮色，全面杜絕白底 */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploaderDropzone"],
    [data-baseweb="file-uploader"],
    [data-testid="stFileUploader"] section > div {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border: 1px dashed rgba(56, 189, 248, 0.4) !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploaderDropzone"] * {
        color: #cbd5e1 !important;
    }
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #334155 !important;
        background: #334155 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }

    /* 摺疊面板 (stExpander) 徹底杜絕反白變白條 */
    [data-testid="stExpander"],
    [data-testid="stExpander"] details {
        background-color: rgba(15, 23, 42, 0.85) !important;
        background: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
        margin-bottom: 14px !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details summary,
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] details summary:hover,
    .streamlit-expanderHeader:hover {
        background-color: #334155 !important;
        background: #334155 !important;
        color: #38bdf8 !important;
    }
    [data-testid="stExpander"] summary *,
    [data-testid="stExpander"] details summary *,
    .streamlit-expanderHeader *,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] div {
        color: #f1f5f9 !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        background: rgba(15, 23, 42, 0.95) !important;
        color: #f1f5f9 !important;
    }

    /* 提示框純白字體 */
    [data-testid="stAlert"], [data-testid="stAlert"] *,
    [data-testid="stNotification"], [data-testid="stNotification"] * {
        color: #ffffff !important;
    }
    [data-testid="stAlert"] strong {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
    }

    /* 下拉選單本體與彈出選單（Selectbox & Popover）全面深色杜絕反白 */
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    [data-testid="stSelectbox"] > div > div {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    div[data-baseweb="select"] *,
    [data-testid="stSelectbox"] * {
        color: #ffffff !important;
    }
    div[data-baseweb="select"] svg {
        fill: #38bdf8 !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="popover"] ul,
    [data-baseweb="menu"],
    div[data-baseweb="menu"],
    ul[role="listbox"],
    div[role="listbox"] {
        background-color: #0f172a !important;
        background: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.85) !important;
    }
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] li *,
    li[role="option"],
    li[role="option"] * {
        background-color: transparent !important;
        background: transparent !important;
        color: #f8fafc !important;
    }
    [data-baseweb="popover"] li:hover,
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #1e293b !important;
        background: #1e293b !important;
        color: #38bdf8 !important;
    }

    /* 圖表與資料表格浮動工具列 (stElementToolbar) 徹底深色化 */
    [data-testid="stElementToolbar"],
    div[data-testid="stElementToolbar"],
    .stElementToolbar {
        background-color: #0f172a !important;
        background: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        border-radius: 9999px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.75) !important;
        color: #f1f5f9 !important;
    }
    [data-testid="stElementToolbar"] button,
    div[data-testid="stElementToolbar"] button,
    [data-testid="stElementToolbarButton"],
    button[data-testid="stElementToolbarButton"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        color: #f1f5f9 !important;
        border-radius: 9999px !important;
    }
    [data-testid="stElementToolbar"] button:hover,
    div[data-testid="stElementToolbar"] button:hover,
    [data-testid="stElementToolbarButton"]:hover,
    button[data-testid="stElementToolbarButton"]:hover {
        background-color: #1e293b !important;
        background: #1e293b !important;
        color: #38bdf8 !important;
    }
    [data-testid="stElementToolbar"] svg,
    div[data-testid="stElementToolbar"] svg,
    [data-testid="stElementToolbarButton"] svg,
    button[data-testid="stElementToolbarButton"] svg {
        fill: #f1f5f9 !important;
        stroke: #f1f5f9 !important;
        color: #f1f5f9 !important;
    }

    /* 側邊欄樣式 */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 15, 29, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* 頂部主橫幅 */
    .tech-hero {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
    }
    .hero-title {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 14.5px;
        color: #cbd5e1 !important;
        margin-top: 6px;
    }
    .badge-item {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12.5px;
        font-weight: 600;
        background: rgba(99, 102, 241, 0.16);
        border: 1px solid rgba(129, 140, 248, 0.35);
        color: #c7d2fe !important;
    }

    /* 按鈕樣式（含次要按鈕，徹底杜絕白底反白） */
    .stButton > button,
    div[data-testid="stButton"] > button,
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"] {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        color: #ffffff !important;
    }
    .stButton > button:hover,
    div[data-testid="stButton"] > button:hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover {
        background-color: #334155 !important;
        background: #334155 !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 14px rgba(56, 189, 248, 0.25) !important;
    }
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #6366f1 100%) !important;
        background-color: #2563eb !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
    }

    /* 狀態卡片樣式 */
    .status-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .status-badge-green {
        background: rgba(34, 197, 94, 0.2);
        color: #86efac;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid rgba(34, 197, 94, 0.4);
    }
    .status-badge-yellow {
        background: rgba(234, 179, 8, 0.2);
        color: #fde047;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid rgba(234, 179, 8, 0.4);
    }
    .status-badge-red {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .status-badge-pending {
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 電腦周邊受檢類別清單
PERIPHERAL_CATEGORIES = [
    "⌨️ 機械/薄膜鍵盤",
    "🖱️ 滑鼠",
    "🎧 耳機"
]

# ==========================================
# 1. 資料庫連線與初始化 (SQLite: disputes.db)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "disputes.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS return_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            customer_email TEXT,
            product_category TEXT,
            product_name TEXT,
            customer_reason TEXT,
            image_data BLOB,
            status TEXT DEFAULT '待審核',
            risk_level TEXT,
            risk_score INTEGER,
            ai_verdict TEXT,
            ai_evidence TEXT,
            ai_recommendation TEXT,
            review_comment TEXT DEFAULT '',
            created_at TEXT,
            reviewed_at TEXT
        )
    """)
    conn.commit()

    # 自動檢查並為現有資料庫新增 customer_email 欄位
    try:
        c.execute("ALTER TABLE return_requests ADD COLUMN customer_email TEXT DEFAULT ''")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # 自動同步遷移周邊類別名稱為標準格式
    c.execute("UPDATE return_requests SET product_category = '🎧 耳機' WHERE product_category LIKE '%耳機%'")
    c.execute("UPDATE return_requests SET product_category = '⌨️ 機械/薄膜鍵盤' WHERE product_category LIKE '%鍵盤%' OR product_category LIKE '%平板%'")
    c.execute("UPDATE return_requests SET product_category = '🖱️ 滑鼠' WHERE product_category LIKE '%滑鼠%'")
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. 電腦周邊專用 AI 初審分析引擎
# ==========================================
def analyze_return_request(category, product_name, reason, image_file, api_key=""):
    """
    電腦周邊專用瑕疵與風控分析核心：
    - 若有提供 API Key：呼叫 Gemini 多模態視覺模型深度檢測
    - 若無 API Key：啟用電腦周邊專用風控規則引擎
    """
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""
            你是一位專精於「電腦周邊（機械/薄膜鍵盤、滑鼠、耳機）」售後退換貨與爭議防詐風控的資深專家。
            檢測範圍嚴格限定於電腦周邊三大品類：鍵盤、滑鼠、耳機。
            
            請根據買家提供的退貨資訊進行嚴謹審查：
            - 周邊品類: {category}
            - 周邊名稱: {product_name}
            - 買家申訴原因: {reason}

            【電腦周邊風控研判原則】：
            1. 紅燈 (高風險人為損害/拆裝/進水，75-100分)：外力摔破、外殼凹裂、暴力撬拔軸體/微動、飲料進水受潮、私自拆解改裝、線材扯斷。
            2. 黃燈 (事證不足/主觀感受爭議，40-74分)：手感不習慣、按鍵壓力不適應、主觀音質偏好、延遲感覺模糊，未附連點測試數據或操作影片。
            3. 綠燈 (正常新品瑕疵 DOA，0-39分)：微動雙擊連點、滾輪跳幀、特定軸體不觸發、完全無法通電、無線接收器失靈、單耳無聲。

            請以 JSON 格式輸出：
            {{
                "risk_level": "綠燈" / "黃燈" / "紅燈",
                "risk_score": 0到100整數,
                "verdict": "一句話簡短判定結論 (精準指出周邊故障類型)",
                "evidence": "具體判斷依據與分析說明 (結合鍵盤/滑鼠/耳機結構特性分析)",
                "recommendation": "給賣家店長的具體處置建議 (如：免寄回換新/補傳測試短片/駁回並提供自費維修)"
            }}
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            res_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(res_text)
            return data["risk_level"], data["risk_score"], data["verdict"], data["evidence"], data["recommendation"]
        except Exception:
            pass

    # 電腦周邊專用模擬引擎
    reason_lower = reason.lower()
    if any(k in reason_lower for k in ["摔", "破", "碎", "斷", "裂", "撞", "泡水", "進水", "飲料", "撬", "拆", "改裝", "狗咬", "拉扯", "焦", "燒"]):
        return (
            "紅燈", 88,
            "周邊外觀重大受損 / 疑似人為暴力損害或私自拆裝",
            "申訴特徵符合高能量外力衝擊、飲料進水受潮或人為改裝破壞（非屬正常鍵軸/微動出廠耗損），高機率為使用不當導致之硬體損毀。",
            "建議【駁回申請】，依保固規範主動提供原廠保固外自費維修或零件更換服務報價"
        )
    elif any(k in reason_lower for k in ["怪怪", "手感", "不習慣", "不順", "不好用", "不喜歡", "沒想像", "音質不如", "鍵程", "延遲", "稍微", "偏重", "偏輕"]):
        return (
            "黃燈", 52,
            "手感或聽感主觀感受爭議 / 瑕疵事證未明",
            "買家描述偏向個人使用習慣適應性或音質主觀偏好，未附具體按鍵測試器截圖、連點測試數據或破音錄音影片，事證尚不齊全。",
            "建議【要求買家補件】：請買家提供特定按鍵/微動/聲道之動態操作測試影片或檢測截圖"
        )
    else:
        return (
            "綠燈", 20,
            "周邊電子元件硬體瑕疵 / 出廠新品不良 (DOA)",
            "描述符合鍵盤軸體觸發不良、滑鼠微動雙擊、滾輪編碼器信號跳動或耳機單元斷路等典型出廠品質問題，無人為外力損壞跡象。",
            "建議【核准全額退款】或安排換發新品（電腦周邊小件可評估免寄回以節省逆物流運費）"
        )

# ==========================================
# 3. 買家端專屬側邊欄導航 (無任何後台管理連結)
# ==========================================
st.sidebar.markdown("""
<div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 15px;">
    <div style="font-size: 20px; font-weight: 800; color: #f8fafc; letter-spacing: -0.5px;">🛍️ 周邊售後客服中心</div>
    <div style="font-size: 12px; color: #38bdf8; margin-top: 4px;">● 買家退換貨服務門戶 (Buyer Portal)</div>
</div>
""", unsafe_allow_html=True)

buyer_menu = st.sidebar.radio(
    "📌 買家服務選單",
    [
        "📝 提交退換貨申請",
        "🔍 查詢申請進度 / 補充照片"
    ]
)

st.sidebar.info("""
**🎯 受理電腦周邊範圍：**
- ⌨️ **機械/薄膜鍵盤** (軸體/鍵位/PCB)
- 🖱️ **滑鼠** (微動/編碼器/感應器)
- 🎧 **耳機** (單元/頭樑/收音)

**📋 買家售後須知：**
1. 購買 7 日內商品享新品不良免費換新/退款服務。
2. 申請時【必須上傳瑕疵佐證照片】，未附照片恕無法受理申請。
3. 請務必填寫正確的電子信箱，審核判決將自動寄發通知信。
4. 若收到「要求補件」通知，可隨時至「查詢進度」補傳照片。
""")

st.sidebar.caption("📧 售後服務信箱：zhuant610@gmail.com")

# ==========================================
# 頁面一：提交退換貨申請
# ==========================================
if buyer_menu == "📝 提交退換貨申請":
    st.markdown("""
    <div class="tech-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-title">📱 買家端：電腦周邊售後與退換貨申請門戶</div>
                <div class="hero-subtitle">
                    專為 <strong>鍵盤、滑鼠、耳機</strong> 設計之 7 天鑑賞期瑕疵檢驗與智慧退換貨申訴通道
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <span class="badge-item">⌨️ 鍵盤檢測</span>
                <span class="badge-item">🖱️ 滑鼠檢測</span>
                <span class="badge-item">🎧 耳機檢測</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("#### 📝 填寫申訴資訊")
        order_id = st.text_input("訂單編號", value=f"ORD-PERI-{datetime.now().strftime('%m%d%H%M')}")
        customer_email = st.text_input("買家電子信箱 (Email) *必填，接收審核判決通知", placeholder="例如：buyer@example.com")
        category = st.selectbox("周邊商品類別 (僅限電腦周邊)", PERIPHERAL_CATEGORIES)
        
        # 依據所選周邊顯示專屬檢驗指引
        if "鍵盤" in category:
            st.caption("💡 **鍵盤檢驗提示**：建議拍照包含鍵帽外觀、軸體插座或背光狀態；若為卡鍵請註明特定鍵位 (如 Space, Enter, WASD)。")
        elif "滑鼠" in category:
            st.caption("💡 **滑鼠檢驗提示**：建議拍照包含滾輪、底面腳墊磨損與接收器外觀；若為連點請註明左鍵或右鍵。")
        elif "耳機" in category:
            st.caption("💡 **耳機檢驗提示**：建議拍照包含頭樑伸縮關節、耳罩皮革與線材接頭；請註明是左耳、右耳或麥克風異常。")

        product_name = st.text_input("周邊商品型號 / 全名", placeholder="例如：Logitech G PRO X 機械鍵盤 / Razer Viper V2 Pro 無線滑鼠 / HyperX Cloud III 耳麥")
        reason = st.text_area(
            "瑕疵/異常原因詳細說明", 
            placeholder="請清楚描述周邊異常狀態（例如：滑鼠左鍵點一下會連點成雙擊、鍵盤空白鍵卡住回彈不良、耳機左耳完全無聲音等）", 
            height=130
        )

    with col2:
        st.markdown("#### 📸 上傳瑕疵佐證照片 *(必填)")
        uploaded_image = st.file_uploader("上傳周邊外觀或損壞照片 (支援 JPG/PNG) *必填", type=["jpg", "jpeg", "png"])
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="買家上傳之周邊實體照片", use_container_width=True)
        else:
            st.markdown("""
            <div style="border: 2px dashed rgba(239, 68, 68, 0.45); border-radius: 12px; padding: 36px 20px; text-align: center; color: #e2e8f0; background: rgba(239, 68, 68, 0.08);">
                <span style="font-size:16px; font-weight:700; color:#fca5a5;">⚠️ 尚未上傳瑕疵照片 (此項為必填)</span><br>
                <span style="font-size:13.5px; color:#cbd5e1; margin-top:8px; display:inline-block;">為保障買賣雙方權益並進行保固核銷，系統規定必須上傳周邊實體瑕疵照片方可受理申請。</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 送出退貨申請 (立即完成初審登記)", type="primary", use_container_width=True):
        if not order_id or not customer_email or not product_name or not reason:
            st.error("請完整填寫訂單編號、買家電子信箱、周邊名稱與瑕疵說明！")
        elif "@" not in customer_email or "." not in customer_email:
            st.error("請填寫正確有效的買家電子信箱格式（例如：user@example.com）！")
        elif not uploaded_image:
            st.error("❌ 申請失敗：為加速出廠保固核銷，系統規定【必須上傳瑕疵佐證照片】否則不給予受理申請！請點選上方按鈕選取照片後再送出。")
        else:
            with st.spinner("🤖 正在為您提交退貨申訴資料並進行初步建檔..."):
                img_bytes = uploaded_image.getvalue() if uploaded_image else None
                
                # 執行電腦周邊 AI 風控初審
                risk_lvl, risk_score, verdict, evidence, rec = analyze_return_request(
                    category, product_name, reason, img_bytes
                )

                # 寫入 SQLite (disputes.db)
                try:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute("""
                        INSERT INTO return_requests 
                        (order_id, customer_email, product_category, product_name, customer_reason, image_data, status, risk_level, risk_score, ai_verdict, ai_evidence, ai_recommendation, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, '待審核', ?, ?, ?, ?, ?, ?)
                    """, (order_id, customer_email.strip(), category, product_name, reason, img_bytes, risk_lvl, risk_score, verdict, evidence, rec, now_str))
                    conn.commit()
                    conn.close()

                    st.success(f"🎉 退換貨申請已成功提交！您的案件編號為 **`{order_id}`**。")
                    st.info(f"📧 審核結果將寄發至您的電子信箱：**`{customer_email.strip()}`**。您亦可隨時在左側「🔍 查詢申請進度」輸入訂單編號追蹤審核狀態。")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ 申訴資料寫入資料庫失敗：{str(e)}。請聯繫系統管理員確認後台連線。")

# ==========================================
# 頁面二：查詢申請進度 / 補充照片
# ==========================================
elif buyer_menu == "🔍 查詢申請進度 / 補充照片":
    st.markdown("""
    <div class="tech-hero">
        <div>
            <div class="hero-title">🔍 買家端：退貨審核進度查詢與照片補傳</div>
            <div class="hero-subtitle">
                輸入您的 <strong>訂單編號</strong> 或 <strong>電子信箱</strong>，隨時追蹤退換貨最新處理狀態。
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    query_input = st.text_input("輸入訂單編號 (例如: ORD-PERI-xxxx) 或 買家電子信箱", placeholder="請輸入完整訂單編號或送出申請時填寫的 Email")

    if query_input:
        conn = sqlite3.connect(DB_FILE)
        query_sql = """
            SELECT * FROM return_requests 
            WHERE order_id = ? OR customer_email = ? 
            ORDER BY id DESC
        """
        df_query = pd.read_sql_query(query_sql, conn, params=(query_input.strip(), query_input.strip()))
        conn.close()

        if df_query.empty:
            st.warning("⚠️ 查無相符的退換貨申請案件，請確認您輸入的訂單編號或電子信箱是否正確。")
        else:
            st.markdown(f"##### 📋 查詢結果：共找到 {len(df_query)} 筆相關案件")
            for _, item in df_query.iterrows():
                # 狀態標籤樣式
                cur_status = item['status']
                if cur_status == '已通過':
                    status_badge = '<span class="status-badge-green">✅ 已通過核准</span>'
                elif cur_status == '需補件':
                    status_badge = '<span class="status-badge-yellow">⚠️ 需補充資料</span>'
                elif cur_status == '已駁回':
                    status_badge = '<span class="status-badge-red">🚫 申請已駁回</span>'
                else:
                    status_badge = '<span class="status-badge-pending">⏳ 待店長審核中</span>'

                with st.container():
                    st.markdown(f"""
                    <div class="status-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <span style="font-size:17px; font-weight:700; color:#ffffff;">訂單：{item['order_id']} ({item['product_name']})</span>
                            {status_badge}
                        </div>
                        <div style="font-size:14px; color:#cbd5e1; line-height:1.7;">
                            • <strong>周邊品類</strong>：{item['product_category']}<br>
                            • <strong>申請時間</strong>：{item['created_at']}<br>
                            • <strong>申訴原因</strong>：{item['customer_reason']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # 若狀態為「需補件」，提供補件說明與上傳照片功能
                    if cur_status == "需補件":
                        st.info(f"**📢 客服店長補件指示說明**：\n\n{item['review_comment'] or '請補充清晰之瑕疵外觀照片或操作測試短片。'}")
                        
                        st.markdown("##### 📷 補傳瑕疵照片或佐證資料：")
                        supp_image = st.file_uploader(f"選擇欲補傳之瑕疵照片 (JPG/PNG)", type=["jpg", "jpeg", "png"], key=f"supp_img_{item['id']}")
                        
                        if st.button("🚀 確認送出補件照片", type="primary", key=f"btn_supp_{item['id']}"):
                            if supp_image:
                                supp_bytes = supp_image.getvalue()
                                update_conn = sqlite3.connect(DB_FILE)
                                cur = update_conn.cursor()
                                # 補上照片並將狀態更新為「待審核 (已補件)」
                                cur.execute("""
                                    UPDATE return_requests 
                                    SET image_data = ?, status = '待審核', customer_reason = customer_reason || ' [買家已於 ' || ? || ' 補上瑕疵照片]'
                                    WHERE id = ?
                                """, (supp_bytes, datetime.now().strftime("%Y-%m-%d %H:%M"), item['id']))
                                update_conn.commit()
                                update_conn.close()
                                st.success("✅ 補件照片已成功上傳！案件已重新提交給客服店長進行二次審核。")
                                st.rerun()
                            else:
                                st.warning("請先選取要上傳的照片檔案！")
                    
                    elif cur_status == "已通過":
                        st.success(f"🎉 **退換貨已核准**！\n\n客服備註：{item['review_comment'] or '已通過出廠保固瑕疵核銷，請留意物流或退款通知。'}")
                    
                    elif cur_status == "已駁回":
                        st.error(f"🚫 **退貨申請未通過**\n\n駁回原因說明：{item['review_comment'] or '經檢驗非屬出廠保固範圍。'}")
                    
                    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
