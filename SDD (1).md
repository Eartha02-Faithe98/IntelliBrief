這是一份專為 **AI Coding Agent (如 Claude Code, Cursor)** 優化的軟體設計文件 (SDD)。我們將採用 **Next.js (App Router)** 作為核心框架，搭配 **SQLite** 與 **Prisma**，確保開發效率與部署的輕量化。

---

# 軟體設計文件 (SDD)：AI 自動化新聞簡報系統

## 1. 系統架構概述 (System Overview)
本系統採單一程式庫 (Monorepo-style) 架構，利用 Next.js 的全端特性處理前端 UI、後端 API 與排程觸發。

*   **前端**：Next.js (React) + Tailwind CSS + Shadcn UI。
*   **後端**：Next.js Server Actions & API Routes。
*   **資料層**：Prisma ORM + SQLite (在地檔案)。
*   **外部整合**：OpenAI API (摘要)、Google News RSS (來源)、Nodemailer/Gmail API (郵件)。

---

## 2. 技術堆疊 (Tech Stack)

| 組件 | 技術選擇 | 備註 |
| :--- | :--- | :--- |
| **框架** | Next.js 14+ (App Router) | 全端開發環境 |
| **資料庫** | SQLite | 輕量、無需伺服器、單一檔案 |
| **ORM** | Prisma | 強型別資料存取 |
| **內容擷取** | Axios + JSDOM + Readability.js | 解析新聞內文精華 |
| **AI 引擎** | OpenAI SDK (GPT-4o) | 負責摘要與關鍵字提取 |
| **簡報生成** | PptxGenJS | 產出標準 .pptx 檔案 |
| **樣式** | Tailwind CSS | 實現 16:9 模擬預覽與響應式介面 |

---

## 3. 資料庫 Schema 設計 (Prisma)

```prisma
// schema.prisma

datasource db {
  provider = "sqlite"
  url      = "file:./dev.db"
}

generator client {
  provider = "prisma-client-js"
}

model Topic {
  id        String   @id @default(cuid())
  name      String   @unique // 例如：AI科技, 財經, 棒球
  keywords  String   // 存儲 RSS 查詢關鍵字
  news      News[]
  createdAt DateTime @default(now())
}

model News {
  id          String   @id @default(cuid())
  title       String
  url         String   @unique
  source      String?  // 來源媒體
  publishDate DateTime?
  content     String?  // 原始抓取的內文
  summary     String?  // AI 生成的摘要 (JSON 格式或 Markdown)
  topicId     String
  topic       Topic    @relation(fields: [topicId], references: [id])
  status      String   @default("PENDING") // PENDING, PROCESSED, FAILED
  isIncluded  Boolean  @default(true)      // 是否包含在簡報中
  createdAt   DateTime @default(now())
}

model Briefing {
  id          String   @id @default(cuid())
  date        DateTime @default(now())
  pptxUrl     String?  // 生成的檔案路徑
  status      String   @default("DRAFT") // DRAFT, SENT
}
```

---

## 4. 核心模組邏輯

### 4.1 採集與 AI 加工流水線 (Scraper & AI Pipeline)
1.  **Trigger**: 透過 `/api/cron` 或手動按鈕觸發。
2.  **Fetch**: 讀取 `Topic` 表，循環請求 Google News RSS。
3.  **Extract**: 對於新連結，使用 `Axios` 抓取 HTML，並透過 `Readability.js` 提取純文字。
4.  **AI Summary**: 將文字傳送至 GPT-4o，Prompt 要求輸出：
    *   3-5 點繁體中文摘要。
    *   媒體名稱提取。
5.  **Save**: 更新 `News` 資料表，狀態設為 `PROCESSED`。

### 4.2 16:9 模擬預覽 (Preview Engine)
*   **組件**：`SlidePreview.tsx`
*   **實作**：使用 CSS 容器 `aspect-video` (16:9)，內建 `padding: 5%`。
*   **內容佈局**：
    *   左側/上方：新聞標題 (Bold, Extra Large)。
    *   中央：Bullet points (AI 摘要)。
    *   右下：來源名稱與日期。

---

## 5. API 路由設計 (Server Actions)

| 行動 (Action) | 描述 | 輸入參數 |
| :--- | :--- | :--- |
| `fetchLatestNews` | 觸發爬蟲與 AI 摘要任務 | `topicId?` |
| `getNewsByTopic` | 獲取特定主題的當日新聞清單 | `topicId, date` |
| `updateNewsStatus` | 手動勾選是否將該新聞納入簡報 | `newsId, isIncluded` |
| `generatePPTX` | 調用 PptxGenJS 生成檔案並回傳下載連結 | `newsIds[]` |
| `sendEmail` | 執行 SMTP 寄送或建立 Gmail 草稿 | `mode, content, attachmentId` |

---

## 6. 實作路徑 (Implementation Roadmap)

這是為 AI Coding Agent 準備的開發指令順序。請依序執行：

### 第一階段：環境初始化與模型建立
1.  **Step 1**: 初始化 Next.js 專案，安裝 `prisma`, `@prisma/client`, `lucide-react`, `clsx`, `tailwind-merge`。
2.  **Step 2**: 建立 `schema.prisma` 並執行 `npx prisma db push`。
3.  **Step 3**: 撰寫 Seed Script，預設 PRD 提到的 10 個主題 (AI, 財經等) 進入 `Topic` 表。

### 第二階段：爬蟲與 AI 核心
4.  **Step 4**: 實作 `lib/scraper.ts`，結合 `jsdom` 與 `readability` 解析 URL 內文。
5.  **Step 5**: 實作 `lib/openai.ts`，封裝 GPT-4o 請求，處理新聞摘要 Prompt。
6.  **Step 6**: 建立 API Route `app/api/tasks/scrape/route.ts` 串接上述流程。

### 第三階段：後台管理介面
7.  **Step 7**: 建立 Layout，左側為主題 Tabs，中央為新聞卡片清單。
8.  **Step 8**: 實作「手動刷新」按鈕，呼叫抓取任務並顯示進度條。

### 第四階段：簡報生成與預覽
9.  **Step 9**: 實作 `components/SlidePreview.tsx`，使用 Tailwind 製作 16:9 的卡片視窗。
10. **Step 10**: 整合 `pptxgenjs`，實作 `lib/pptx-service.ts`，確保樣式與網頁預覽一致。

### 第五階段：郵件與發布
11. **Step 11**: 實作郵件預覽彈窗 (Dialog)。
12. **Step 12**: 整合 `nodemailer`，實作發送功能，並串接主題選擇與附件。

---

## 7. 關鍵 Prompt 參考 (給 AI Agent 使用)

**當執行 AI 摘要時，請使用以下 Prompt：**
> "請將以下新聞內容總結為 3 到 5 個關鍵要點。要求：1. 使用繁體中文。2. 語氣專業、客觀。3. 提取新聞來源媒體名稱。4. 格式請嚴格遵守 JSON：{ 'summary': ['要點1', '要點2'], 'source': '媒體名' }。新聞內容：{{content}}"

**當生成 PPTX 時，請使用以下規格：**
> "Slide 尺寸為 16:9。標題字體大小 32pt, 顏色 #333333。內文摘要字體 18pt，使用項目符號。右下角標註來源與 URL。"

---

**下一步建議：**
您現在可以將此文件貼給您的 AI Coding Agent (例如 Cursor)，並要求它從 **「第一階段：環境初始化」** 開始執行。如果您需要我針對某個模組（例如爬蟲邏輯）提供更詳細的程式碼範例，請隨時告訴我！