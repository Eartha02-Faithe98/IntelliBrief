import streamlit as st
import os
from dotenv import load_dotenv
from database import init_db, save_news_item, get_news_by_category, get_all_news, clear_all_news
from scraper import fetch_google_news, extract_article_content
from ai_processor import generate_summary
from generator import create_pptx

# 載入環境變數
load_dotenv()

# 設定 Streamlit 頁面參數
st.set_page_config(page_title="AI 自動化新聞簡報系統", page_icon="📰", layout="wide")

# 初始化資料庫
@st.cache_resource
def setup_database():
    init_db()

setup_database()

# --- 側邊欄 (Sidebar) ---
with st.sidebar:
    st.header("⚙️ 系統設定")

    # 初始化 session state 來控制輸入框的顯示
    if 'show_api_input' not in st.session_state:
        st.session_state.show_api_input = False

    # API Key 設定區塊
    current_api_key = os.environ.get("GEMINI_API_KEY", "")
    has_api_key = bool(current_api_key)

    if has_api_key:
        st.success("🟢 狀態：已設定 (安全隱藏)")
        btn_label = "更換 API Key"
    else:
        st.warning("🔴 狀態：尚未設定")
        btn_label = "設定 API Key"

    # 控制顯示/隱藏輸入框的按鈕
    if st.button(btn_label):
        st.session_state.show_api_input = not st.session_state.show_api_input
        st.rerun()

    # 只有當 show_api_input 為 True 時才顯示輸入框
    if st.session_state.show_api_input:
        st.markdown("---")
        # 使用普通的 text_input，沒有 type="password" 就不會有眼睛按鈕
        new_key_input = st.text_input(
            "請貼上新的 Gemini API Key", 
            value="", 
            placeholder="AIzaSy...",
            help="在此輸入您的金鑰。儲存後此欄位將自動隱藏以確保安全。"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✔️ 驗證並儲存", type="primary"):
                if new_key_input:
                    try:
                        # 簡單驗證 API Key (使用 google-genai SDK 輕量測試)
                        from google import genai
                        client = genai.Client(api_key=new_key_input)
                        client.models.list()

                        # 驗證成功，覆寫 .env 檔案
                        from dotenv import set_key
                        env_path = ".env"
                        if not os.path.exists(env_path):
                            open(env_path, 'w').close()
                        set_key(env_path, "GEMINI_API_KEY", new_key_input)

                        # 同步更新當下環境變數
                        os.environ["GEMINI_API_KEY"] = new_key_input
                        
                        # 驗證成功後，關閉輸入介面
                        st.session_state.show_api_input = False
                        st.success("✅ API Key 設定並驗證成功！")
                        import time
                        time.sleep(1) # 讓成功訊息顯示一秒鐘再重整
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 驗證失敗，請確認 Key 是否正確：{str(e)}")
                else:
                    st.warning("請先輸入 API Key")
        with col2:
            if st.button("❌ 取消", type="secondary"):
                st.session_state.show_api_input = False
                st.rerun()
        st.markdown("---")

    # 確保在主程式中使用最新或已設定的 Key
    active_api_key = os.environ.get("GEMINI_API_KEY", "")

    st.header("🔍 篩選設定")
    available_keywords = ["AI 科技", "科技產業", "財經", "股票", "投資", "理財", "棒球", "半導體", "Web3", "總體經濟"]
    selected_keywords = st.multiselect("選擇抓取主題", available_keywords, default=["AI 科技", "半導體"])
    
    max_results = st.slider("每個主題抓取篇數", min_value=1, max_value=20, value=3)
    
    if st.button("🚀 立即啟動抓取", type="primary", use_container_width=True):
        if not active_api_key:
            st.error("請先輸入 Gemini API Key")
        elif not selected_keywords:
            st.warning("請選擇至少一個主題")
        else:
            with st.spinner("正在執行自動化抓取與摘要...這可能需要幾分鐘的時間。"):
                # 在開始新抓取前，先清空舊的資料庫紀錄
                clear_all_news()
                
                total_new_items = 0
                for keyword in selected_keywords:
                    # 使用 st.toast 或 st.write 顯示進度
                    st.toast(f"開始抓取主題: {keyword}")
                    news_list = fetch_google_news(keyword, max_results)
                    
                    for news in news_list:
                        # 1. 抓取內文
                        content = extract_article_content(news['url'])
                        
                        # 2. 生成摘要
                        summary = generate_summary(content, active_api_key)
                        news['summary'] = summary
                        
                        # 3. 儲存至資料庫
                        success = save_news_item(news)
                        if success:
                            total_new_items += 1
                
                st.success(f"抓取完成！共新增 {total_new_items} 篇新聞。")
                st.rerun()

# --- 主內容區 (Main Dashboard) ---
st.title("📰 當日新聞簡報儀表板")

# 取得所有資料庫中的新聞
all_news = get_all_news()

# 取得目前已有的分類
categories = list(set([n.category for n in all_news]))
# 為了顯示順序一致，進行排序
categories.sort()

if not categories:
    st.info("目前資料庫中沒有新聞，請從左側邊欄設定並點擊「立即啟動抓取」按鈕。")
else:
    # 建立 Tabs 標籤頁
    tabs = st.tabs(["全覽"] + categories)
    
    # [全覽] Tab
    with tabs[0]:
        st.subheader(f"所有新聞 (共 {len(all_news)} 篇)")
        for news in all_news:
            with st.expander(f"[{news.category}] {news.title}"):
                st.markdown(f"**來源:** {news.source} | **發布時間:** {news.published_at}")
                st.markdown("**AI 摘要:**")
                st.markdown(news.summary)
                st.markdown(f"[🔗 閱讀原文]({news.url})")
                
    # [個別分類] Tabs
    for i, category in enumerate(categories):
        with tabs[i+1]:
            category_news = get_news_by_category(category)
            st.subheader(f"{category} 焦點新聞 (共 {len(category_news)} 篇)")
            for news in category_news:
                with st.container():
                    st.markdown(f"#### {news.title}")
                    st.caption(f"來源: {news.source} | 時間: {news.published_at}")
                    st.markdown(news.summary)
                    st.markdown(f"[🔗 閱讀原文]({news.url})")
                    st.divider()

    # --- 底部發佈區 ---
    st.divider()
    st.subheader("📤 產出與發佈")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 產生並準備下載 PPTX 簡報"):
            with st.spinner("正在產生簡報..."):
                file_path = create_pptx(all_news)
                # 產生完成後，提供下載按鈕
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="📥 點擊下載簡報檔案 (.pptx)",
                        data=file,
                        file_name=os.path.basename(file_path),
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                st.success("簡報產生成功！請點擊上方按鈕下載。")

    with col2:
         st.button("✉️ 發送至郵件草稿 (MVP 未實作)", disabled=True)
