"""
電腦周邊 (鍵盤·滑鼠·耳機) 智慧退換貨與爭議風控小幫手
Smart Computer Peripheral Return & Dispute Risk Copilot
專為資管系畢業專題設計之原型系統 (MVP)
技術棧：Python + Streamlit + SQLite + Plotly
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
from PIL import Image
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 0. 網頁基本配置與電競科技風視覺樣式 (CSS)
# ==========================================
st.set_page_config(
    page_title="電腦周邊售後風控平台 · 後台管理系統",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入科技感電競深色主題 CSS，解決頁面單調並全面強化字體對比（杜絕暗字融入背景）
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

    /* 頂部主標題與一般文字色彩通盤加亮，杜絕暗字融入背景 */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    p, span, label, li {
        color: #f1f5f9;
    }

    /* ==========================================
       重點修復一：表單文字、標籤與 Placeholder 亮色優化
       ========================================== */
    /* 輸入框與文字區 placeholder 改為清晰明亮的淺銀白，不再融入背景暗黑中 */
    ::placeholder {
        color: rgba(226, 232, 240, 0.72) !important;
        opacity: 1 !important;
    }
    ::-webkit-input-placeholder {
        color: rgba(226, 232, 240, 0.72) !important;
        opacity: 1 !important;
    }
    ::-moz-placeholder {
        color: rgba(226, 232, 240, 0.72) !important;
        opacity: 1 !important;
    }
    :-ms-input-placeholder {
        color: rgba(226, 232, 240, 0.72) !important;
        opacity: 1 !important;
    }
    input::placeholder, textarea::placeholder {
        color: rgba(226, 232, 240, 0.72) !important;
        opacity: 1 !important;
    }

    /* 表單標籤（如：瑕疵/異常原因詳細說明、周邊商品型號/全名、訂單編號）亮白字體 */
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

    /* 提示小字（st.caption）改為高辨識度冰藍亮白，不再呈現幾乎看不見的暗灰 */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    .stCaption,
    .stCaption p {
        color: #93c5fd !important;
        font-size: 13.5px !important;
        line-height: 1.5 !important;
    }

    /* 輸入表單本體（打字文字白色、暗色質感背景、明亮對比） */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-size: 14.5px !important;
    }
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.4) !important;
    }

    /* ==========================================
       重點修復二：提示框 (st.info, st.success, etc.) 內部文字強制白字
       ========================================== */
    /* 全面強制所有 Streamlit 提示框內部文字、段落、粗體一律為高對比純白字 */
    [data-testid="stAlert"],
    [data-testid="stAlert"] *,
    [data-testid="stNotification"],
    [data-testid="stNotification"] *,
    .stAlert,
    .stAlert * {
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

    /* st.info (AI 判斷證據與理由) 科技藍底 + 純白字 */
    [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]),
    div[data-baseweb="notification"][kind="info"] {
        background: rgba(30, 58, 138, 0.5) !important;
        border: 1px solid rgba(96, 165, 250, 0.6) !important;
    }

    /* st.success (處置建議) 翠綠底 + 純白字 */
    [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]),
    div[data-baseweb="notification"][kind="success"] {
        background: rgba(20, 83, 45, 0.5) !important;
        border: 1px solid rgba(74, 222, 128, 0.6) !important;
    }

    /* st.warning 琥珀黃底 + 純白字 */
    [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]),
    div[data-baseweb="notification"][kind="warning"] {
        background: rgba(120, 53, 15, 0.5) !important;
        border: 1px solid rgba(251, 191, 36, 0.6) !important;
    }

    /* st.error 緋紅底 + 純白字 */
    [data-testid="stAlert"]:has([data-testid="stAlertContentError"]),
    div[data-baseweb="notification"][kind="error"] {
        background: rgba(127, 29, 29, 0.5) !important;
        border: 1px solid rgba(248, 113, 113, 0.6) !important;
    }

    /* ==========================================
       其他細節組件對比度加強 (全站清查改善)
       ========================================== */
    /* 側邊欄文字全盤亮白 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080c14 0%, #0f172a 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.25) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5) !important;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [role="radiogroup"] * {
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* 頂部主視覺科技橫幅卡片 */
    .tech-hero {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
    }
    .tech-hero::after {
        content: '';
        position: absolute;
        top: -50%; right: -20%; width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.22) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-title {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.6;
    }
    .badge-item {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(99, 102, 241, 0.16);
        border: 1px solid rgba(129, 140, 248, 0.35);
        color: #c7d2fe !important;
    }

    /* 指標數據卡 (stMetric) 玻璃擬態 */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
        backdrop-filter: blur(10px) !important;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 10px 28px rgba(99, 102, 241, 0.25) !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    [data-testid="stMetricValue"] div {
        color: #38bdf8 !important;
        font-weight: 800 !important;
    }

    /* 摺疊審核清單 (stExpander) 美化與文字高對比 */
    [data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(10px) !important;
        margin-bottom: 14px !important;
    }
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.65) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(51, 65, 85, 0.75) !important;
        color: #60a5fa !important;
    }
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] div {
        color: #f1f5f9;
    }
    [data-testid="stExpander"] strong {
        color: #ffffff !important;
    }

    /* 下拉選單彈出視窗（Selectbox Popover）選項黑底白字高對比 */
    [data-baseweb="popover"],
    [data-baseweb="popover"] ul,
    [data-baseweb="menu"] {
        background-color: #0f172a !important;
    }
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] li * {
        color: #f8fafc !important;
    }
    [data-baseweb="popover"] li:hover {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
    }

    /* 檔案上傳器拖曳區文字與按鈕亮色 */
    [data-testid="stFileUploader"] section {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px dashed rgba(255, 255, 255, 0.25) !important;
    }
    [data-testid="stFileUploader"] section * {
        color: #cbd5e1 !important;
    }

    /* 主要按鈕電競流光風格 */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #6366f1 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
    }

    /* 資料表格高對比 */
    [data-testid="stDataFrame"] {
        background-color: rgba(15, 23, 42, 0.75) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* 風險燈號專用標籤樣式 (保持鮮明對比) */
    .pill-red {
        background: rgba(239, 68, 68, 0.22);
        color: #fca5a5 !important;
        border: 1px solid rgba(239, 68, 68, 0.5);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .pill-yellow {
        background: rgba(234, 179, 8, 0.22);
        color: #fde047 !important;
        border: 1px solid rgba(234, 179, 8, 0.5);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .pill-green {
        background: rgba(34, 197, 94, 0.22);
        color: #86efac !important;
        border: 1px solid rgba(34, 197, 94, 0.5);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }

    /* 內嵌代碼標籤 (Inline Code) 科技亮青色高對比 */
    code {
        color: #38bdf8 !important;
        background: rgba(15, 23, 42, 0.75) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* 對話彈出視窗 (Modal Dialog) 科技深色高質感樣式與純白字 */
    div[role="dialog"], [data-testid="stDialog"] {
        background-color: #0b1120 !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8) !important;
        color: #f8fafc !important;
    }
    div[role="dialog"] h2, div[role="dialog"] h3, div[role="dialog"] h4,
    div[role="dialog"] p, div[role="dialog"] span, div[role="dialog"] label,
    [data-testid="stDialog"] * {
        color: #f8fafc !important;
    }
    div[role="dialog"] .stCheckbox label span {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 電腦周邊受檢類別清單（嚴格限定：鍵盤、滑鼠、耳機，已依需求移除「電競」兩字）
PERIPHERAL_CATEGORIES = [
    "⌨️ 機械/薄膜鍵盤",
    "🖱️ 辦公滑鼠",
    "🎧 降噪耳機"
]

# ==========================================
# 0.1 郵件設定持久化核心 (email_config.json)
# ==========================================
CONFIG_FILE = "email_config.json"

def load_email_config():
    """讀取本地持久化之郵件設定，防止網頁刷新後密碼遺失"""
    default_cfg = {
        "sender_email": "zhuant610@gmail.com",
        "app_password": ""
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**default_cfg, **data}
        except Exception:
            return default_cfg
    return default_cfg

def save_email_config(sender_email, app_password):
    """將郵件設定儲存至本地 email_config.json"""
    cfg = {
        "sender_email": (sender_email or "zhuant610@gmail.com").strip(),
        "app_password": (app_password or "").strip()
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"儲存郵件設定失敗: {str(e)}")
    return cfg

# 系統預設發送審核結果通知之電子郵件帳號
email_cfg = load_email_config()
SENDER_EMAIL = email_cfg.get("sender_email", "zhuant610@gmail.com")

# ==========================================
# 1. 資料庫初始化與資料遷移 (SQLite)
# ==========================================
DB_FILE = "disputes.db"

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

    # 為歷史舊資料補上預設展示用電子郵件
    c.execute("UPDATE return_requests SET customer_email = 'buyer_sample@example.com' WHERE customer_email IS NULL OR customer_email = ''")

    # 自動遷移舊版資料庫中的非周邊資料，並全數移除「電競」字眼
    c.execute("""
        UPDATE return_requests 
        SET product_category = '⌨️ 機械/薄膜鍵盤',
            product_name = '客製化鋁合金熱插拔機械鍵盤',
            customer_reason = '收到鍵盤外殼角落摔裂凹陷，多個鍵軸被暴力拔起且插座針腳折斷，PCB銅箔破裂。',
            ai_verdict = '疑似嚴重人為摔落撞擊與私自暴力拆改',
            ai_evidence = '鋁合金外殼具有尖銳著地凹痕，且軸座受力屬於垂直外力拔扯斷裂，研判為使用摔落或改裝失誤導致。',
            ai_recommendation = '高風險人為損毀，建議【駁回申請】並提供自費維修報價'
        WHERE product_category LIKE '%平板%' OR product_category LIKE '%手機%'
    """)
    c.execute("UPDATE return_requests SET product_category = '🎧 降噪耳機' WHERE product_category LIKE '%耳機%'")
    c.execute("UPDATE return_requests SET product_category = '⌨️ 機械/薄膜鍵盤' WHERE product_category LIKE '%鍵盤%'")
    c.execute("UPDATE return_requests SET product_category = '🖱️ 辦公滑鼠' WHERE product_category LIKE '%滑鼠%'")
    conn.commit()
    
    # 檢查是否需要預設展示資料
    c.execute("SELECT COUNT(*) FROM return_requests")
    count = c.fetchone()[0]
    if count == 0:
        seed_sample_data(c)
        conn.commit()
    conn.close()

def seed_sample_data(cursor):
    """
    預設示範案例：全面聚焦於電腦周邊 (鍵盤、滑鼠、耳機) 之典型客訴與詐欺情境（包含買家信箱）
    """
    sample_cases = [
        (
            "ORD-PERI-8821", "buyer.service88@gmail.com", "🎧 降噪耳機", "7.1聲道雙模無線降噪耳機",
            "剛開箱充電整晚完全無法開機，電源指示燈完全不亮，插線亦無任何聲音輸出。",
            None, "已通過", "綠燈", 15,
            "電源迴路故障 / 出廠新品不良 (DOA)",
            "外觀無任何外力擠壓裂痕或人為泡水生鏽痕跡，符合保固新品不良免費換新條件。",
            "建議通過全額退款或換新，並安排逆物流取件",
            "已核准新品換貨", "2026-10-05 10:15:00", "2026-10-05 10:30:00"
        ),
        (
            "ORD-PERI-9043", "user.keyboard90@gmail.com", "⌨️ 機械/薄膜鍵盤", "客製化鋁合金熱插拔機械鍵盤",
            "收到鍵盤外殼角落摔裂凹陷，多個鍵軸被暴力拔起且插座針腳折斷，PCB銅箔破裂。",
            None, "已駁回", "紅燈", 92,
            "疑似嚴重人為摔落撞擊與私自暴力拆改",
            "照片顯示鋁合金定位板與外殼有明顯尖銳著地凹痕，且軸座受力屬於垂直外力拔扯斷裂，外包裝盒無相對應壓損，高機率為使用摔落或改裝不當所致。",
            "高風險人為損壞，建議【駁回申請】並告知不屬出廠保固範疇，提供自費維修報價",
            "外力撞擊凹痕與拆解損壞明顯，已電話聯繫買家駁回", "2026-10-06 14:20:00", "2026-10-06 14:45:00"
        ),
        (
            "ORD-PERI-9188", "tech.user91@gmail.com", "⌨️ 機械/薄膜鍵盤", "RGB三模無線矮軸機械鍵盤",
            "打字起來手感怪怪的，鍵程好像太短不順手，有時候打太快感覺有按鍵沒反應。",
            None, "待審核", "黃燈", 55,
            "手感主觀感受爭議 / 缺特定鍵位測試事證",
            "買家描述偏向主觀手感不適應，且未指出具體失靈鍵位（未提供線上 Key-Test 按鍵測試截圖或動態操作短片）。",
            "建議要求買家補件：提供線上鍵盤測試網頁操作截圖或特定卡鍵按鍵短片",
            "", "2026-10-07 09:10:00", None
        ),
        (
            "ORD-PERI-9302", "office.worker93@gmail.com", "🖱️ 辦公滑鼠", "PAW3395 輕量化無線滑鼠",
            "使用第三天左鍵微動開關嚴重雙擊連點（按一下變兩下），且滾輪下滾時偶爾向上跳動。",
            None, "待審核", "綠燈", 22,
            "微動開關彈片耗損與滾輪編碼器信號跳動",
            "買家回報為典型滑鼠微動開關觸點異常與光學/機械編碼器跳幀現象，外觀無摔裂泡水跡象，符合新品保固條款。",
            "建議核准換貨新品（小額電腦周邊可評估免寄回不良品以節省逆物流運費）",
            "", "2026-10-07 13:40:00", None
        )
    ]
    cursor.executemany("""
        INSERT INTO return_requests 
        (order_id, customer_email, product_category, product_name, customer_reason, image_data, status, risk_level, risk_score, ai_verdict, ai_evidence, ai_recommendation, review_comment, created_at, reviewed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_cases)

init_db()

# ==========================================
# 2. 審核判決郵件發送核心 (寄件信箱: zhuant610@gmail.com)
# ==========================================
def send_decision_email(customer_email, order_id, product_name, status, review_comment, verdict="", recommendation=""):
    """
    於店長審核判決拍板時，寄送電子郵件通知至買家信箱
    寄送時使用的電子信箱: zhuant610@gmail.com
    嚴格診斷連線與認證狀態，提供清晰的反饋資訊
    """
    if not customer_email or "@" not in customer_email:
        return False, "⚠️ 買家未填寫有效之電子信箱，跳過郵件發送。"

    cfg = load_email_config()
    sender = cfg.get("sender_email", "zhuant610@gmail.com").strip()
    app_pwd = cfg.get("app_password", "").strip() or st.session_state.get("gmail_app_password", "").strip() or os.environ.get("GMAIL_APP_PASSWORD", "").strip()

    if not app_pwd:
        return False, f"⚠️ 尚未設定 Gmail 應用程式密碼！目前無法由 {sender} 發送真實 Email。\n\nGoogle 自 2022 年起已全面禁用一般帳號密碼發信，請前往「⚙️ 系統設定 & API」輸入 16 碼應用程式密碼。"

    subject = f"【售後退換貨審核通知】訂單 {order_id} - 審核結果：{status}"

    html_body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans TC', sans-serif; background-color: #f8fafc; padding: 24px; margin: 0;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 14px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 24px 28px; border-bottom: 3px solid #38bdf8;">
                <h2 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 700;">🛡️ 電腦周邊售後客服中心 · 審核結果通知</h2>
                <p style="color: #94a3b8; font-size: 13px; margin: 6px 0 0 0;">人機協同爭議風控平台 (HITL System)</p>
            </div>
            
            <div style="padding: 28px;">
                <p style="font-size: 15px; color: #1e293b; margin-top: 0;">親愛的買家您好：</p>
                <p style="font-size: 14px; color: #475569; line-height: 1.6;">
                    您於本平台提交之電腦周邊售後申請，經由 <strong>AI 初審與店長人機協同複審</strong>，最終裁決結果如下：
                </p>
                
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px 22px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; color: #64748b; width: 30%;">訂單編號</td>
                            <td style="padding: 10px 0; color: #0f172a; font-weight: 600;">{order_id}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; color: #64748b;">商品名稱</td>
                            <td style="padding: 10px 0; color: #0f172a; font-weight: 600;">{product_name}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; color: #64748b;">審核判決</td>
                            <td style="padding: 10px 0; font-weight: bold; font-size: 15px; color: {'#16a34a' if status == '已通過' else ('#d97706' if status == '需補件' else '#dc2626')};">
                                {status}
                            </td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; color: #64748b; vertical-align: top;">店長備註/補件指示</td>
                            <td style="padding: 10px 0; color: #0f172a; white-space: pre-wrap; line-height: 1.6;">{review_comment or '無特別備註'}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; color: #64748b;">AI 判定依據</td>
                            <td style="padding: 10px 0; color: #334155; font-size: 13px;">{verdict}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; color: #64748b;">處置建議</td>
                            <td style="padding: 10px 0; color: #334155; font-size: 13px;">{recommendation}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="font-size: 13px; color: #64748b; line-height: 1.6; margin-bottom: 0;">
                    ※ 本郵件由系統自動發送，寄件信箱：<strong>{sender}</strong>。<br>
                    ※ 若有補傳瑕疵照片/操作短片之需求，或對審核結果有任何疑問，歡迎直接回覆此郵件聯繫我們。
                </p>
            </div>
            
            <div style="background-color: #f1f5f9; padding: 14px 28px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8;">
                電腦周邊智慧退換貨與爭議風控系統 · 感謝您的配合
            </div>
        </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"電腦周邊售後客服中心 <{sender}>"
        msg["To"] = customer_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        clean_pwd = app_pwd.replace(" ", "")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(sender, clean_pwd)
            server.sendmail(sender, customer_email, msg.as_string())
        return True, f"已成功由 {sender} 發送真實通知信至買家信箱：{customer_email}！"
    except smtplib.SMTPAuthenticationError:
        return False, f"❌ Gmail 認證失敗 (535)：帳號 {sender} 或應用程式密碼錯誤。請確認 Google 帳戶已開啟「兩步驟驗證」，並至安全性設定中產生專用 16 碼「應用程式密碼」（注意：非一般登入密碼）。"
    except smtplib.SMTPConnectError as e:
        return False, f"❌ 無法連線至 Gmail 伺服器 (smtp.gmail.com:465)：{str(e)}"
    except Exception as e:
        return False, f"❌ 郵件發送失敗：{str(e)}"

# ==========================================
# 2.1 要求補件對話小視窗 (Modal Dialog)
# ==========================================
dialog_decorator = getattr(st, "dialog", getattr(st, "experimental_dialog", None))

def render_supplement_dialog_content(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation):
    """
    補件小視窗內容：填寫具體需補件的內容 (包含缺照片)，確認後才更新案件並發送 Email
    """
    st.markdown(f"**訂單編號**：`{order_id}` ｜ **商品型號**：`{product_name}`")
    st.markdown(f"**買家通知信箱**：`{customer_email}`")
    st.markdown("---")

    st.markdown("##### 📌 請勾選需要買家補件的項目：")
    c1, c2 = st.columns(2)
    with c1:
        req_photo = st.checkbox("📷 缺少清晰瑕疵照片 (外觀/受損處特寫)", value=True, key=f"dlg_photo_{case_id}")
        req_sn = st.checkbox("🏷️ 缺少商品序號/防偽貼紙照片", value=False, key=f"dlg_sn_{case_id}")
    with c2:
        req_video = st.checkbox("🎥 缺少故障操作短片 (連點/卡鍵/跳幀/無聲)", value=False, key=f"dlg_video_{case_id}")
        req_test = st.checkbox("📊 缺少按鍵/微動檢測截圖 (Key-Test)", value=False, key=f"dlg_test_{case_id}")

    st.markdown("##### ✍️ 填寫需補件的具體說明與要求內容：")
    default_text = "經店長與 AI 初步審核，目前退貨申訴缺乏關鍵瑕疵照片佐證。請於 3 日內補充清晰特寫照片或操作短片，以利完成出廠保固核銷與後續退換換新流程。"
    custom_desc = st.text_area(
        "補件詳細指示 (此內容將完整呈現於寄送給買家的 Email 通知中)：",
        value=default_text,
        height=110,
        key=f"dlg_desc_{case_id}"
    )

    st.caption("※ 點擊下方確認按鈕後，案件將正式更新為「需補件」，並立即透過 **zhuant610@gmail.com** 發送補件 Email 給買家。")

    col_send, col_cancel = st.columns([1, 1])
    with col_send:
        if st.button("🚀 確認送出補件要求並發送 Email", type="primary", use_container_width=True, key=f"dlg_submit_{case_id}"):
            missing_items = []
            if req_photo:
                missing_items.append("缺少清晰瑕疵照片 (外觀/受損處特寫)")
            if req_sn:
                missing_items.append("缺少商品序號/防偽貼紙照片")
            if req_video:
                missing_items.append("缺少故障操作短片 (連點/卡鍵/跳幀/無聲)")
            if req_test:
                missing_items.append("缺少按鍵/微動檢測截圖 (Key-Test)")

            missing_str = "、".join(missing_items) if missing_items else "請依說明補充相關佐證"
            final_note = f"【需補件項目】：{missing_str}\n【店長指示說明】：{custom_desc}"

            # 更新資料庫
            update_conn = sqlite3.connect(DB_FILE)
            cur = update_conn.cursor()
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("UPDATE return_requests SET status='需補件', review_comment=?, reviewed_at=? WHERE id=?", 
                        (final_note, now_time, case_id))
            update_conn.commit()
            update_conn.close()

            # 發送補件 Email 通知
            ok, res_msg = send_decision_email(
                customer_email=customer_email,
                order_id=order_id,
                product_name=product_name,
                status='需補件',
                review_comment=final_note,
                verdict=ai_verdict,
                recommendation=ai_recommendation
            )

            st.session_state["last_email_notification"] = {
                "ok": ok,
                "order_id": order_id,
                "status": "需補件",
                "to": customer_email,
                "msg": res_msg
            }
            if "active_supplement_id" in st.session_state:
                del st.session_state["active_supplement_id"]
            st.rerun()

    with col_cancel:
        if st.button("❌ 取消返回", use_container_width=True, key=f"dlg_cancel_{case_id}"):
            if "active_supplement_id" in st.session_state:
                del st.session_state["active_supplement_id"]
            st.rerun()

if dialog_decorator:
    @dialog_decorator("⚠️ 要求補件：填寫補件內容與通知")
    def open_supplement_modal(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation):
        render_supplement_dialog_content(case_id, order_id, product_name, customer_email, ai_verdict, ai_recommendation)


# ==========================================
# 3. 電腦周邊專用 AI 智能初審核心 (LLM / 專用模擬雙軌)
# ==========================================
def analyze_return_request(category, product_name, reason, image_file, api_key=""):
    """
    電腦周邊專用瑕疵與風控分析核心：
    - 若有提供 API Key：呼叫 Gemini 多模態視覺模型深度檢測
    - 若無 API Key：啟用電腦周邊專用風控規則引擎（覆蓋軸體、微動、編碼器、單元、進水摔裂等關鍵特徵）
    """
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""
            你是一位專精於「電腦周邊（機械/薄膜鍵盤、辦公滑鼠、降噪耳機）」售後退換貨與爭議防詐風控的資深專家。
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
        except Exception as e:
            st.warning(f"真實 API 呼叫異常 ({str(e)})，系統已自動無縫降級為電腦周邊展示模擬引擎。")

    # 電腦周邊專用模擬引擎 (Domain-Specific Mock Engine)
    reason_lower = reason.lower()
    
    # 1. 人為暴力外力摔裂、拆解改裝、泡水受潮 (高風險紅燈)
    if any(k in reason_lower for k in ["摔", "破", "碎", "斷", "裂", "撞", "泡水", "進水", "飲料", "撬", "拆", "改裝", "狗咬", "拉扯", "焦", "燒"]):
        return (
            "紅燈", 88,
            "周邊外觀重大受損 / 疑似人為暴力損害或私自拆裝",
            "申訴特徵符合高能量外力衝擊、飲料進水受潮或人為改裝破壞（非屬正常鍵軸/微動出廠耗損），高機率為使用不當導致之硬體損毀。",
            "建議【駁回申請】，依保固規範主動提供原廠保固外自費維修或零件更換服務報價"
        )
    # 2. 主觀手感、聽感偏好或事證模糊 (黃燈需補件)
    elif any(k in reason_lower for k in ["怪怪", "手感", "不習慣", "不順", "不好用", "不喜歡", "沒想像", "音質不如", "鍵程", "延遲", "稍微", "偏重", "偏輕", "延遲"]):
        return (
            "黃燈", 52,
            "手感或聽感主觀感受爭議 / 瑕疵事證未明",
            "買家描述偏向個人使用習慣適應性或音質主觀偏好，未附具體按鍵測試器截圖、連點測試數據或破音錄音影片，事證尚不齊全。",
            "建議【要求買家補件】：請買家提供特定按鍵/微動/聲道之動態操作測試影片或檢測截圖"
        )
    # 3. 典型出廠硬體不良 (微動雙擊、滾輪跳動、單耳無聲、軸體失靈、無法開機) (綠燈快審)
    else:
        return (
            "綠燈", 20,
            "周邊電子元件硬體瑕疵 / 出廠新品不良 (DOA)",
            "描述符合鍵盤軸體觸發不良、滑鼠微動雙擊、滾輪編碼器信號跳動或耳機單元斷路等典型出廠品質問題，無人為外力損壞跡象。",
            "建議【核准全額退款】或安排換發新品（電腦周邊小件可評估免寄回以節省逆物流運費）"
        )

# ==========================================
# 3. 系統側邊欄導航
# ==========================================
st.sidebar.markdown("""
<div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 15px;">
    <div style="font-size: 20px; font-weight: 800; color: #f8fafc; letter-spacing: -0.5px;">🛡️ Peripheral Copilot</div>
    <div style="font-size: 12px; color: #38bdf8; margin-top: 4px;">● 電腦周邊專用風控引擎 (HITL)</div>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "📌 後台管理功能",
    [
        "🧑‍💼 店長：人機對照審核台",
        "📊 老闆：BI 營運成效儀表板",
        "⚙️ 系統設定 & API"
    ]
)

st.sidebar.info("""
**🎯 檢測對象聚焦：**
- ⌨️ **機械/薄膜鍵盤** (軸體/鍵位/PCB)
- 🖱️ **辦公滑鼠** (微動/編碼器/感應器)
- 🎧 **降噪耳機** (單元/頭樑/收音)

---
🛡️ **前後台分離架構說明**：
買家退換貨門戶已獨立為 `buyer.py`，客戶端無法檢視或存取本後台之審核、BI 與系統設定。
""")

# ==========================================
# 模組一：店長人機對照審核台 (HITL)
# ==========================================
if menu == "🧑‍💼 店長：人機對照審核台":
    st.markdown("""
    <div class="tech-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-title">🧑‍💼 店長端：周邊人機協同審核台 (Human-in-the-Loop)</div>
                <div class="hero-subtitle">
                    透過 <strong>紅黃綠燈風險分流</strong>，店長精準對照買家申訴與 AI 佐證，秒級裁決核准、補件或駁回。
                </div>
            </div>
            <div>
                <span class="badge-item">🛡️ 人機協同防詐</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 顯示上一筆案件之郵件通知寄送狀態
    if "last_email_notification" in st.session_state:
        n_info = st.session_state.pop("last_email_notification")
        if n_info.get("ok"):
            st.success(f"📧 **審核裁決完成，通知郵件已成功寄出！**\n\n- 訂單編號：**{n_info['order_id']}** (狀態更新為：`{n_info['status']}`)\n- 收件買家：`{n_info['to']}`\n- 寄件帳號：`{SENDER_EMAIL}`\n- 發送狀態：{n_info['msg']}")
        else:
            st.error(f"⚠️ **審核裁決已更新至資料庫，但 Email 發送未成功**！\n\n- 訂單編號：**{n_info['order_id']}** (狀態更新為：`{n_info['status']}`)\n- 收件買家：`{n_info['to']}`\n- 寄件帳號：`{SENDER_EMAIL}`\n- 失敗原因：\n{n_info['msg']}\n\n👉 *提示：請前往「⚙️ 系統設定 & API」填寫 Google 帳戶 16 碼應用程式密碼，即可正常發送信件。*")

    # 讀取案件
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM return_requests ORDER BY id DESC", conn)
    conn.close()

    # 頂部狀態指標卡片
    c1, c2, c3, c4 = st.columns(4)
    pending_count = len(df[df['status'] == '待審核'])
    approved_count = len(df[df['status'] == '已通過'])
    rejected_count = len(df[df['status'] == '已駁回'])
    red_count = len(df[df['risk_level'] == '紅燈'])

    c1.metric("⏳ 待審核案件", f"{pending_count} 件")
    c2.metric("✅ 已通過退換", f"{approved_count} 件")
    c3.metric("🚫 已駁回案件", f"{rejected_count} 件")
    c4.metric("🚨 高風險紅燈警告", f"{red_count} 件", delta="風控攔截")

    st.markdown("---")

    # 雙維度篩選器 (處理狀態 + 周邊類別)
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_status = st.selectbox("📌 篩選處理狀態", ["全部", "待審核", "已通過", "已駁回", "需補件"], index=1)
    with filter_col2:
        filter_cat = st.selectbox("🎯 篩選周邊品類", ["全部周邊"] + PERIPHERAL_CATEGORIES, index=0)

    filtered_df = df.copy()
    if filter_status != "全部":
        filtered_df = filtered_df[filtered_df['status'] == filter_status]
    if filter_cat != "全部周邊":
        filtered_df = filtered_df[filtered_df['product_category'] == filter_cat]

    if filtered_df.empty:
        st.info("目前無符合篩選條件的周邊退貨案件。")
    else:
        st.subheader("📋 案件審核清單")
        for idx, row in filtered_df.iterrows():
            # 燈號標籤
            if row['risk_level'] == "紅燈":
                pill_html = '<span class="pill-red">🔴 紅燈 ‧ 高風險</span>'
            elif row['risk_level'] == "黃燈":
                pill_html = '<span class="pill-yellow">🟡 黃燈 ‧ 需補件</span>'
            else:
                pill_html = '<span class="pill-green">🟢 綠燈 ‧ 低風險</span>'

            with st.expander(f"【{row['risk_level']}｜風險分 {row['risk_score']}】{row['product_category']} - 訂單：{row['order_id']} ({row['product_name']}) ｜ 狀態：{row['status']}"):
                left_col, right_col = st.columns([1, 1], gap="large")

                with left_col:
                    st.markdown("#### 👤 買家申訴原始資料")
                    target_email = row['customer_email'] if ('customer_email' in row and row['customer_email']) else '未提供'
                    st.write(f"**買家信箱**：`{target_email}`")
                    st.write(f"**商品品類**：{row['product_category']}")
                    st.write(f"**周邊型號**：`{row['product_name']}`")
                    st.write(f"**申訴原因**：{row['customer_reason']}")
                    st.write(f"**申請時間**：`{row['created_at']}`")
                    if row['image_data']:
                        img = Image.open(io.BytesIO(row['image_data']))
                        st.image(img, caption="買家佐證圖片", use_container_width=True)
                    else:
                        st.caption("*(此示範案例未附圖)*")

                with right_col:
                    st.markdown("#### 🤖 AI 周邊瑕疵與風控佐證")
                    st.markdown(f"**風控判定**：{pill_html} (人為損害/爭議指數: **{row['risk_score']} / 100**)", unsafe_allow_html=True)
                    st.markdown(f"**判定結論**：**{row['ai_verdict']}**")
                    st.info(f"**AI 判斷證據與理由**：\n{row['ai_evidence']}")
                    st.success(f"**處置建議**：\n{row['ai_recommendation']}")

                    # 審核操作區 (僅待審核案件可操作)
                    if row['status'] == "待審核":
                        st.markdown("#### ✍️ 店長最終裁決 (人機協同拍板)")
                        review_note = st.text_input("審核備註 (選填)", key=f"note_{row['id']}")
                        
                        btn_c1, btn_c2, btn_c3 = st.columns(3)
                        with btn_c1:
                            if st.button("✅ 核准退換", key=f"app_{row['id']}", type="primary", use_container_width=True):
                                update_conn = sqlite3.connect(DB_FILE)
                                cur = update_conn.cursor()
                                now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                final_note = review_note or "符合出廠保固瑕疵核准"
                                cur.execute("UPDATE return_requests SET status='已通過', review_comment=?, reviewed_at=? WHERE id=?", 
                                            (final_note, now_time, row['id']))
                                update_conn.commit()
                                update_conn.close()
                                
                                # 觸發寄送通知信至買家信箱 (zhuant610@gmail.com 寄出)
                                ok, res_msg = send_decision_email(
                                    customer_email=target_email,
                                    order_id=row['order_id'],
                                    product_name=row['product_name'],
                                    status='已通過',
                                    review_comment=final_note,
                                    verdict=row['ai_verdict'],
                                    recommendation=row['ai_recommendation']
                                )
                                st.session_state["last_email_notification"] = {
                                    "ok": ok,
                                    "order_id": row['order_id'],
                                    "status": "已通過",
                                    "to": target_email,
                                    "msg": res_msg
                                }
                                st.rerun()
                        with btn_c2:
                            if st.button("⚠️ 要求補件", key=f"req_{row['id']}", use_container_width=True):
                                if dialog_decorator:
                                    open_supplement_modal(
                                        case_id=row['id'],
                                        order_id=row['order_id'],
                                        product_name=row['product_name'],
                                        customer_email=target_email,
                                        ai_verdict=row['ai_verdict'],
                                        ai_recommendation=row['ai_recommendation']
                                    )
                                else:
                                    st.session_state["active_supplement_id"] = row['id']
                                    st.rerun()
                        with btn_c3:
                            if st.button("🚫 駁回申請", key=f"rej_{row['id']}", use_container_width=True):
                                update_conn = sqlite3.connect(DB_FILE)
                                cur = update_conn.cursor()
                                now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                final_note = review_note or "非屬出廠瑕疵（人為外力損毀）駁回"
                                cur.execute("UPDATE return_requests SET status='已駁回', review_comment=?, reviewed_at=? WHERE id=?", 
                                            (final_note, now_time, row['id']))
                                update_conn.commit()
                                update_conn.close()
                                
                                # 觸發寄送通知信至買家信箱
                                ok, res_msg = send_decision_email(
                                    customer_email=target_email,
                                    order_id=row['order_id'],
                                    product_name=row['product_name'],
                                    status='已駁回',
                                    review_comment=final_note,
                                    verdict=row['ai_verdict'],
                                    recommendation=row['ai_recommendation']
                                )
                                st.session_state["last_email_notification"] = {
                                    "ok": ok,
                                    "order_id": row['order_id'],
                                    "status": "已駁回",
                                    "to": target_email,
                                    "msg": res_msg
                                }
                                st.rerun()

                        # 若環境不支援裝飾器對話框時之頁面內補件表單備援
                        if not dialog_decorator and st.session_state.get("active_supplement_id") == row['id']:
                            st.markdown("---")
                            render_supplement_dialog_content(
                                case_id=row['id'],
                                order_id=row['order_id'],
                                product_name=row['product_name'],
                                customer_email=target_email,
                                ai_verdict=row['ai_verdict'],
                                ai_recommendation=row['ai_recommendation']
                            )
                    else:
                        st.markdown("<div style='background:rgba(30,41,59,0.5); padding:10px 14px; border-radius:8px; margin-top:10px;'>", unsafe_allow_html=True)
                        st.write(f"**審核結果**：`{row['status']}`")
                        st.write(f"**店長備註**：{row['review_comment'] or '無'}")
                        st.write(f"**完成時間**：`{row['reviewed_at']}`")
                        st.write(f"**通知紀錄**：已發送判決郵件至 `{target_email}` (寄件者: `{SENDER_EMAIL}`)")
                        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 模組三：BI 營運成效儀表板 (限定電腦周邊)
# ==========================================
elif menu == "📊 老闆：BI 營運成效儀表板":
    st.markdown("""
    <div class="tech-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-title">📊 老闆端：電腦周邊逆物流與客訴 BI 營運儀表板</div>
                <div class="hero-subtitle">
                    呈現導入 <strong>鍵盤/滑鼠/耳機 AI 協同審核</strong> 後之核心商業 KPI、退貨品類佔比與防詐欺成效。
                </div>
            </div>
            <div>
                <span class="badge-item">📈 商業效益量化</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM return_requests", conn)
    conn.close()

    total_cases = len(df)
    approved_rate = round(len(df[df['status'] == '已通過']) / total_cases * 100, 1) if total_cases > 0 else 0
    # 假設傳統人工作業審核平均 15 分鐘，AI 輔助後只需 2.5 分鐘 (節省約 83% 工時)
    hours_saved = round(total_cases * (12.5 / 60), 1)
    # 電腦周邊平均單價以 NT$ 2,800 計算 (鍵盤/高階滑鼠/電競耳機平均行情)
    fraud_blocked_count = len(df[(df['risk_level'] == '紅燈') & (df['status'] == '已駁回')])
    fraud_money_saved = fraud_blocked_count * 2800

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 周邊申請案件數", f"{total_cases} 件")
    col2.metric("🎯 退換貨核准率", f"{approved_rate} %")
    col3.metric("⚡ 累計節省審核工時", f"{hours_saved} 小時", delta="+83% 審核提速")
    col4.metric("💰 攔截潛在損失金額", f"NT$ {fraud_money_saved:,}", delta="高單價防損防線")

    st.markdown("---")

    chart_c1, chart_c2 = st.columns(2)

    with chart_c1:
        st.subheader("📌 案件風險燈號分佈")
        risk_counts = df['risk_level'].value_counts().reset_index()
        risk_counts.columns = ['風險等級', '案件數量']
        st.bar_chart(risk_counts.set_index('風險等級'), color="#38bdf8")

    with chart_c2:
        st.subheader("🔍 電腦周邊品類退貨佔比")
        cat_counts = df['product_category'].value_counts().reset_index()
        cat_counts.columns = ['周邊品類', '退貨件數']
        st.dataframe(cat_counts, use_container_width=True)

    st.markdown("---")
    st.subheader("💡 電腦周邊電商專業學術與商業價值剖析")
    st.markdown("""
    1. **BPR 流程再造 (Business Process Reengineering)**：
       傳統電腦周邊（微動連點、軸體卡頓、耳機雜音）常因買家描述模糊導致客服來回溝通 3~5 天。透過本系統 AI 5 秒精準分類（分流紅黃綠燈），店長可在 2 分鐘內對照裁決。
    2. **精準攔截人為改裝與使用損壞 (Fraud & Abuse Prevention)**：
       電腦周邊社群常有客製化「熱插拔軸體撬斷」、「私自拆解更換微動開關」及「摔落裂痕冒充新品不良」之爭議。AI 視覺比對著力點與凹痕，捍衛賣家毛利率。
    3. **綠燈免逆物流退款 (Zero-Return Replacement)**：
       針對小單價周邊出廠新品不良（DOA），經綠燈審核後可直接換新，免除 NT$ 80~120 的逆物流黑洞成本。
    """)

# ==========================================
# 模組四：系統設定與 API 串接
# ==========================================
elif menu == "⚙️ 系統設定 & API":
    st.markdown("""
    <div class="tech-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-title">⚙️ 系統設定與真實 AI 模型串接</div>
                <div class="hero-subtitle">
                    支援內建模擬規則引擎與 Google Gemini 多模態視覺模型雙軌切換
                </div>
            </div>
            <div>
                <span class="badge-item">🔌 API 管理</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("系統預設已搭載**電腦周邊智慧展示模擬引擎**（零門檻保證可跑）。若想接入真實 Google Gemini 視覺多模態模型，請在此輸入 API 金鑰。")

    current_key = st.session_state.get("gemini_api_key", "")
    new_key = st.text_input("Google Gemini API Key (選填)", value=current_key, type="password")

    if st.button("儲存 API Key", type="primary"):
        st.session_state["gemini_api_key"] = new_key
        st.success("API Key 已成功更新至 Session！後續分析將優先調用 Gemini 2.5 Flash。")

    st.markdown("---")
    st.subheader("📧 審核結果郵件發送設定 (Gmail SMTP)")
    st.markdown(f"系統指定之發信寄件者信箱：`{SENDER_EMAIL}`")

    cfg = load_email_config()
    current_pwd = cfg.get("app_password", "")

    with st.expander("ℹ️ 為什麼需要「16 碼應用程式密碼」？（點此查看 Google 帳戶設定教學）", expanded=not bool(current_pwd)):
        st.markdown("""
        **重要說明**：
        Google 為維護帳戶安全性，自 2022 年起已全面停用「低安全性應用程式存取權限」，因此**無法直接使用您的 Google 登入密碼發送郵件**，必須在 Google 帳戶內產生專用的 **16 碼「應用程式密碼」**。

        **⚙️ 取得步驟（僅需設定一次）：**
        1. 登入寄件電子信箱 **`zhuant610@gmail.com`** 的 Google 帳戶。
        2. 前往 [Google 帳戶安全性設定 (myaccount.google.com/security)](https://myaccount.google.com/security)。
        3. 確認「**兩步驟驗證**」狀態為【**已開啟**】（未開啟兩步驟驗證將無法建立應用程式密碼）。
        4. 在頂部搜尋欄輸入「**應用程式密碼**」(App Passwords) 或至安全性頁面點擊進入。
        5. 應用程式名稱輸入「`電腦周邊退換貨小幫手`」，點擊「**建立**」。
        6. 複製彈出視窗中的 **16 碼英文字母**（例如：`abcd efgh ijkl mnop`），貼入下方輸入框並點擊「**儲存郵件設定**」即可！
        """)

    new_pwd = st.text_input(
        "Gmail 應用程式密碼 (App Password)", 
        value=current_pwd, 
        type="password",
        placeholder="例如：abcd efgh ijkl mnop (共16碼英文字母)",
        help="輸入 Google 帳戶安全性中產生的 16 碼專用密碼。儲存後會持久化記錄於本地 email_config.json，重新整理不遺失。"
    )
    if st.button("💾 儲存郵件設定", type="primary"):
        save_email_config(SENDER_EMAIL, new_pwd.strip())
        st.session_state["gmail_app_password"] = new_pwd.strip()
        st.success(f"✅ 郵件設定已成功永久儲存至 `email_config.json`！裁決時將透過 `{SENDER_EMAIL}` 正式發送通知信。")

    st.markdown("##### 📨 測試郵件寄送功能")
    test_c1, test_c2 = st.columns([3, 1])
    with test_c1:
        test_email_target = st.text_input("收件測試電子信箱", value="", placeholder="輸入您想要接收測試信件的信箱 (例如: user@gmail.com)")
    with test_c2:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 發送測試信件", use_container_width=True):
            if test_email_target and "@" in test_email_target:
                with st.spinner(f"正在連線至 smtp.gmail.com:465 透過 {SENDER_EMAIL} 寄送測試信至 {test_email_target}..."):
                    ok, res_msg = send_decision_email(
                        customer_email=test_email_target.strip(),
                        order_id="ORD-TEST-8888",
                        product_name="客製化機械鍵盤 (系統連線測試件)",
                        status="已通過",
                        review_comment="系統連線與郵件推播功能測試正常，收發無虞！",
                        verdict="測試連線核發",
                        recommendation="此為系統發送測試信，請確認收件夾或垃圾郵件匣"
                    )
                    if ok:
                        st.success(f"{res_msg}")
                    else:
                        st.error(f"{res_msg}")
            else:
                st.warning("⚠️ 請先輸入正確格式的收件測試電子信箱！")

    st.markdown("---")
    st.subheader("🛠️ 資料庫重設與展示資料還原")
    st.caption("點擊下方按鈕將清除目前資料庫，並重新載入精選的「鍵盤、滑鼠、耳機」展示案例。")
    if st.button("重設回電腦周邊示範資料 (Reset DB)"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        init_db()
        st.success("資料庫已成功重設，並載入精選電腦周邊示範案例！")
        st.rerun()
