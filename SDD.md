這是一份根據您提供的 PRD 所撰寫的 **精簡版系統設計文件 (SDD)**。這份文件專為初學者設計，採用 Python 生態系中最簡易且強大的工具組合，旨在讓開發者能透過 AI 輔助，在最短時間內完成功能驗證。

---

# 系統設計文件 (SDD)：AI 自動化新聞簡報系統 (MVP 快速開發版)

| 文件版本 | 狀態 | 作者 | 日期 |
| :--- | :--- | :--- | :--- |
| v1.0 | 實作指引 | 技術架構師 | 2023-10-27 |

---

## 1. 簡介

### 1.1 專案概述
本專案旨在開發一個自動化的新聞處理工具，能夠每日從 Google News 抓取指定主題的新聞，利用 OpenAI 的 GPT 模型生成繁體中文摘要，並自動產出專業的 PPTX 簡報與郵件草稿。系統透過圖形化介面提供「自動化抓取、人工審核、一鍵發佈」的流暢體驗。

### 1.2 系統目標
*   **自動化資訊整合**：取代手動搜尋，自動彙整 10 個以上自定義主題的新聞。
*   **高品質摘要生成**：利用 AI 將長篇文章濃縮為 3-5 個關鍵要點，節省閱讀時間。
*   **即時文件產出**：實現一文一頁的 PPTX 自動生成技術，省去排版工作。
*   **可控的發佈流程**：提供網頁預覽介面，確保資訊在寄出前經過人工確認。
*   **低門檻部署**：無需複雜環境，可在個人電腦透過 Python 環境直接執行。

### 1.3 技術選型
*   **程式語言**：Python 3.9+ (適合資料處理與 AI 整合)
*   **Web UI 框架**：**Streamlit** (無需前端知識即可建構互動式網頁應用)
*   **資料處理**：Pandas (表格數據處理) 與 Beautiful Soup 4 / Feedparser (網頁爬取)
*   **資料庫**：**SQLite** (單一檔案，無需安裝與配置資料庫伺服器)
*   **資料庫 ORM**：**SQLAlchemy** (簡化資料 CRUD 操作)
*   **AI 引擎**：OpenAI API (GPT-4o / GPT-4-turbo)
*   **簡報生成**：`python-pptx`
*   **郵件處理**：`smtplib` 與 `email.mime` (支援 Gmail/Outlook)

---

## 2. 系統架構與運作流程

### 2.1 整體架構
系統採用全棧式單體架構 (Monolithic Architecture)，所有元件運行於本地 Python 環境。

```
[ 使用者瀏覽器 ] <-> [ Streamlit Web UI ]
                         |
                [ Python 核心邏輯層 ]
                         |
    -------------------------------------------
    |            |            |               |
[ 爬蟲模組 ]  [ AI 模組 ]  [ PPT/郵件模組 ]  [ SQLAlchemy ]
    |            |            |               |
[ Google News] [ OpenAI ]  [ 檔案系統 ]     [ SQLite DB ]
```

### 2.2 運作流程詳解
1.  **觸發任務**：使用者在 Streamlit 介面點擊「開始抓取」或系統排程啟動。
2.  **數據採集**：爬蟲模組根據關鍵字清單從 Google News RSS 抓取新聞標題與連結。
3.  **內容解析與摘要**：
    *   系統提取新聞內文。
    *   將內文傳送至 OpenAI API 進行繁體中文摘要。
4.  **資料持久化**：將標題、摘要、連結、發布時間存入 SQLite 資料庫。
5.  **檢視與預覽**：使用者在 Web UI 瀏覽各主題新聞，系統即時生成 PPTX 預覽。
6.  **產出與發佈**：
    *   使用者點擊「產出簡報」，系統生成 `.pptx` 檔提供下載。
    *   使用者點擊「確認寄送」，系統透過 SMTP 或 API 發送郵件或存入草稿。

---

## 3. 核心模組設計

### 3.1 數據中心模組 (`database.py`)
*   **職責**：管理與資料庫的所有互動。
*   **核心功能**：
    *   `init_db()`: 初始化 SQLite 資料表。
    *   `save_news_item()`: 儲存單筆新聞，具備去重邏輯（基於 URL）。
    *   `get_news_by_category()`: 按主題提取當日新聞。

### 3.2 智能爬蟲模組 (`scraper.py`)
*   **職責**：從網路獲取原始數據。
*   **核心功能**：
    *   `fetch_google_news(keyword)`: 使用 `feedparser` 抓取 RSS 內容。
    *   `extract_article_content(url)`: 使用 `requests` 與 `BeautifulSoup` 抓取新聞正文。

### 3.3 AI 加工模組 (`ai_processor.py`)
*   **職責**：調用 LLM 處理文本。
*   **核心功能**：
    *   `generate_summary(text)`: 將新聞內文轉化為 3-5 點繁體中文摘要。
    *   `categorize_news(title)`: (選配) 二次校對新聞分類。

### 3.4 文件生成模組 (`generator.py`)
*   **職責**：將數據轉換為 PPTX 格式。
*   **核心功能**：
    *   `create_pptx(news_list)`: 讀取新聞列表，套用模板，生成 `Slide` 對象並匯出檔案。

### 3.5 介面控制中心 (`app.py`)
*   **職責**：系統入口，負責渲染 UI 與調度其他模組。
*   **核心功能**：
    *   `render_sidebar()`: 設定關鍵字與 API Key。
    *   `main_dashboard()`: 展示新聞卡片與摘要內容。
    *   `action_buttons()`: 處理抓取、下載與寄送的點擊事件。

---

## 4. 資料庫設計

### 4.1 資料庫選型
選用 **SQLite**。
*   **原因**：零配置、檔案型資料庫，方便初學者備份（直接複製檔案）與遷移。

### 4.2 資料表設計

**表名：`news_items` (新聞內容表)**

| 欄位名稱 | 資料型態 | 說明 | 備註 |
|----------|----------|------|------|
| id | INTEGER | 唯一識別碼 | 主鍵，自動遞增 |
| title | TEXT | 新聞原始標題 | |
| summary | TEXT | AI 生成的繁體中文摘要 | |
| category | VARCHAR | 新聞主題分類 | 如：AI 科技、財經 |
| url | TEXT | 原始新聞連結 | 唯一約束 (Unique)，防止重複抓取 |
| source | VARCHAR | 媒體來源名稱 | 如：經濟日報、TechCrunch |
| published_at | DATETIME | 新聞發布時間 | |
| created_at | DATETIME | 系統抓取存檔時間 | 預設為當前時間 |
| is_selected | BOOLEAN | 是否選入簡報/郵件 | 預設為 True |

**表名：`settings` (系統配置表)**

| 欄位名稱 | 資料型態 | 說明 | 備註 |
|----------|----------|------|------|
| key | VARCHAR | 設定名稱 | 如：openai_api_key, keywords |
| value | TEXT | 設定數值 | |

---

## 5. 使用者介面與互動規劃

### 5.1 頁面結構 (Streamlit)
1.  **側邊欄 (Sidebar)**：
    *   OpenAI API Key 輸入框 (支援載入環境變數)。
    *   新聞主題勾選清單 (AI, 財經, 棒球等)。
    *   「立即啟動抓取」大按鈕。
2.  **主內容區 (Main Panel)**：
    *   **Tabs 標籤頁**：按主題區分 (例如：[全覽], [AI 科技], [財經動態])。
    *   **新聞卡片流**：每張卡片顯示標題、AI 摘要要點、來源與連結。
    *   **操作列**：每條新聞旁有「剔除」按鈕，不想要的內容不進入簡報。
3.  **底部發佈區**：
    *   PPTX 預覽圖 (展示第一頁與範例頁)。
    *   「下載本日簡報 (.pptx)」按鈕。
    *   「發送至郵件草稿」按鈕。

### 5.2 核心互動流程
1.  使用者打開瀏覽器訪問本地地址。
2.  確認 API Key 無誤後，點擊「啟動抓取」。
3.  畫面上方出現進度條，顯示「正在抓取主題：AI... 正在生成摘要...」。
4.  完成後，頁面自動刷新顯示當日摘要。
5.  使用者閱讀後，對不感興趣的新聞點擊「隱藏」。
6.  點擊「下載簡報」，系統即時生成檔案並彈出下載視窗。

---

## 6. 功能函數說明

| 函數名稱 | 輸入 | 輸出 | 職責 |
|----------|------|------|------|
| `fetch_and_process()` | 關鍵字清單 | 無 | 調度 scraper 與 ai_processor，並將結果寫入 DB |
| `get_summary_prompt(content)` | 原始文本 | Prompt 字串 | 建構給 AI 的提示詞，規範摘要格式 |
| `build_pptx_slide(prs, item)` | PPT 對象, 新聞資料 | 更新後的 PPT | 在 PPT 中新增一頁並填入摘要內容 |
| `send_mail_via_smtp(target_email)`| 收件人地址 | 成功狀態 | 讀取 DB 中當日選中新聞，格式化後寄出 |

---

## 7. 錯誤處理策略

*   **錯誤情境 1：網路連接超時 (爬蟲階段)**
    *   **處理策略**：設定 10 秒超時，失敗時跳過該篇文章並記錄 Log。
    *   **UI 呈現**：在側邊欄顯示警告標記「有 3 篇新聞因網路問題抓取失敗」。
*   **錯誤情境 2：OpenAI API 餘額不足或 Key 錯誤**
    *   **處理策略**：捕獲 API Error。
    *   **UI 呈現**：彈出錯誤視窗，提示使用者檢查 API Key。
*   **錯誤情境 3：新聞內容過短或無法解析**
    *   **處理策略**：若內文提取失敗，摘要欄位顯示「(無法自動生成，請點擊連結閱讀原文)」。

---

## 8. 實作路徑 (Implementation Roadmap)

### 8.1 環境建置與依賴安裝
```bash
# 建立專案資料夾
mkdir ai_news_brief
cd ai_news_brief

# 建立並啟動虛擬環境
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安裝必要套件
pip install streamlit pandas sqlalchemy python-pptx openai feedparser beautifulsoup4 requests
```

**`requirements.txt` 內容：**
```text
streamlit
pandas
sqlalchemy
python-pptx
openai
feedparser
beautifulsoup4
requests
```

### 8.2 第一階段：資料庫與爬蟲開發 (`database.py`, `scraper.py`)
1.  實作 SQLAlchemy 模型 `NewsItem`。
2.  實作 `fetch_google_news`，測試是否能印出新聞標題。
3.  實作 `extract_article_content`，確保能拿回網頁正文。

### 8.3 第二階段：AI 整合開發 (`ai_processor.py`)
1.  串接 OpenAI SDK。
2.  測試 Prompt：要求 AI 以「繁體中文、條列式、專業語氣」輸出。
3.  將摘要結果更新回 SQLite。

### 8.4 第三階段：文件生成與 UI 開發 (`generator.py`, `app.py`)
1.  實作 `python-pptx` 邏輯，建立標題頁與內容頁。
2.  撰寫 Streamlit UI，使用 `st.tabs` 呈現分類。
3.  實作 `st.download_button` 讓使用者下載生成的 PPTX。

### 8.5 第四階段：測試與運行說明
1.  **測試項目**：
    *   輸入不存在的關鍵字，檢查系統是否崩潰。
    *   斷開網路，測試錯誤提示。
    *   連續運行兩次，確認資料庫不會有重複新聞。
2.  **啟動指令**：
    ```bash
    streamlit run app.py
    ```

---

## 9. 總結與後續擴展
本 SDD 優先實現了 PRD 中的核心價值：**自動化與摘要化**。透過 Python 的豐富生態系，開發者可以在不撰寫複雜前端程式碼的情況下，快速建構出具備 AI 能力的生產力工具。未來可進一步引入 Docker 容器化部署或串接 LINE Bot 進行每日自動推播。