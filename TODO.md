# AI 自動化新聞簡報系統 - 開發任務清單 (TODO)

## 階段一：專案初始化與環境設置 (完成)
- [x] 建立基本的專案資料夾與檔案結構。
- [x] 建立 `.env.example` 檔案，定義所需的環境變數（如 `OPENAI_API_KEY`）。
- [x] 提供使用者 Python 虛擬環境建立與套件安裝的完整指令（因規範限制，將由使用者手動執行 `pip install`）。

## 階段二：資料庫模組開發 (`database.py`) (完成)
- [x] 引入 SQLAlchemy 建立 SQLite 資料庫連線。
- [x] 定義 `NewsItem` 資料表模型（包含 id, title, summary, category, url, source, published_at, created_at, is_selected）。
- [x] 定義 `Settings` 資料表模型（儲存系統設定）。
- [x] 實作資料庫初始化函數 `init_db()`。
- [x] 實作新聞儲存函數 `save_news_item()`（包含基於 URL 的去重邏輯）。
- [x] 實作新聞查詢函數 `get_news_by_category()` 與 `get_all_news()`。

## 階段三：爬蟲模組開發 (`scraper.py`) (完成)
- [x] 實作 `fetch_google_news(keyword)`，使用 `feedparser` 解析 Google News RSS 獲取新聞列表。
- [x] 實作 `extract_article_content(url)`，使用 `requests` 與 `BeautifulSoup4` 抓取新聞正文。
- [x] 加入錯誤處理與超時機制，確保爬蟲穩定性。

## 階段四：AI 處理模組開發 (`ai_processor.py`) (完成)
- [x] 整合 OpenAI API (使用新版 `openai` 套件)。
- [x] 實作 `generate_summary(text)` 函數，設計 Prompt 要求輸出 3-5 點繁體中文摘要。
- [x] 加入 API 錯誤與例外處理機制。

## 階段五：簡報與功能模組開發 (`generator.py` 等) (完成)
- [x] 實作 `create_pptx(news_list)` 函數，使用 `python-pptx` 自動套用樣式生成「一文一頁」的新聞簡報。
- [x] （選配/後續）實作郵件寄送邏輯。

## 階段六：Web 介面開發與系統整合 (`app.py`) (完成)
- [x] 使用 Streamlit 建構側邊欄，包含 API Key 設定與主題選擇。
- [x] 實作主內容區，使用 Tabs 分類顯示新聞。
- [x] 串接「開始抓取」流程：呼叫 scraper -> ai_processor -> database。
- [x] 實作「下載簡報」功能，將查詢結果傳入 generator 產生檔案並提供下載按鈕。
- [x] 進行整體測試與 UI 微調。
