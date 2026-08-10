# SEO 上線手冊（SEO Onboarding）

這份文件說明**網站已經部署之後，要做哪些站外動作才會被 Google 搜尋到**。

> 前提結論：**repo 內的 SEO 已經做完了，不需要改任何一行程式碼。**
> 唯一會碰到 repo 的動作是往 `public/` 丟一個 Google 給的驗證檔（純靜態檔，非 code）。

## 現況盤點：已經完成的部分

| 項目 | 由誰產生 | 線上位置 | 狀態 |
| --- | --- | --- | --- |
| Sitemap | `@astrojs/sitemap` | `/sitemap-index.xml`（含 18 頁） | 已完成 |
| robots.txt | `public/robots.txt` | `/robots.txt`，已宣告 sitemap | 已完成 |
| Canonical URL | `src/layouts/Base.astro` | 每頁自動產生 | 已完成 |
| Meta description | `src/config.ts` | 每頁 | 已完成 |
| Open Graph / Twitter card | `Base.astro` + `og-default.png` | 每頁 | 已完成 |
| JSON-LD 結構化資料 | `Base.astro` + 各頁 | Person、WebSite、SoftwareSourceCode | 已完成 |
| 中英文關鍵字 | `src/config.ts` | 含「黃子竣」等高價值查詢 | 已完成 |

技術面沒有缺口。Google 找不到你，**唯一原因是它還不知道這個網址存在**。以下六步解決這件事。

## 步驟

### Step 1：在 Google Search Console 建立資源

1. 開 <https://search.google.com/search-console>，用 Google 帳號登入
2. 左上角資源選單 → **新增資源**
3. 選 **網址前置字元（URL prefix）**，右邊那欄
4. 填入 `https://zihjyunderek.github.io/`（結尾斜線要留）

> 為什麼不能選「網域」：網域驗證要改 DNS TXT 紀錄，而 `github.io` 的 DNS 在 GitHub 手上，你沒有權限。
>
> 附帶好處：`github.io` 在 Public Suffix List 上，Google 把 `zihjyunderek.github.io` 視為獨立網站，你的排名不會被其他人的 github.io 頁面稀釋。

### Step 2：驗證所有權

這是唯一會動到 repo 的一步。選 **HTML 檔案（HTML file）** 方式，不要選 HTML 標記（那要改 `Base.astro`）。

1. 下載 Google 給的 `googleXXXXXXXXXXXX.html`
2. 放進 **`public/`** 資料夾（不是 `src/`）。Astro 會把 `public/` 原樣複製到網站根目錄
3. `git push` 到 `main`，等 GitHub Actions 跑完（約 1 分鐘，repo 的 Actions 頁籤出現綠勾）
4. 瀏覽器開 `https://zihjyunderek.github.io/googleXXXXXXXXXXXX.html`，確認看得到內容
5. 回 Search Console 按 **驗證**

> 這個檔案**永久保留**。Google 會定期回頭檢查，刪掉會掉驗證狀態。

**如果第 4 步開起來是 404**，先不要動 Google，去 repo 的 Actions 頁看那次 run 的狀態：

| 狀態 | 意思 | 處理 |
| --- | --- | --- |
| Success（綠勾） | 已上線，是邊緣快取 | 網址後加 `?x=1` 重試，或等 10 分鐘 |
| Cancelled（灰） | build 成功但 deploy 被取消，網站仍停在舊版 | 進該次 run → 右上 **Re-run all jobs** |
| Failure（紅叉） | build 失敗 | 點進 build job 看錯誤，本機跑 `npm ci && npm run build` 重現 |

Cancelled 的典型訊息是 `Canceling since a higher priority waiting request for pages exists`，來自 `deploy.yml` 的 `concurrency.cancel-in-progress`。已設為 `false`，不應再發生。

### Step 3：提交 sitemap

Search Console 左側 → **索引 → Sitemap** → 輸入 `sitemap-index.xml` → 提交。

狀態顯示「成功」即可。18 個頁面（首頁、4 個列表頁、13 個專案頁）會被自動帶入，之後新增專案不用再提交一次。

### Step 4：手動要求索引首頁

上方搜尋列貼 `https://zihjyunderek.github.io/` → 進入網址審查 → **要求建立索引**。

每日配額約 10 筆，優先順序：

1. 首頁 `/`
2. `/projects/`
3. 最想被搜到的 2–3 個專案頁（例如 `/projects/decoding-the-city-mgwr/`、`/projects/implied-vol-var/`）

其餘交給 sitemap 自然爬取，不用一頁一頁送。

### Step 5：Bing Webmaster Tools

1. 開 <https://www.bing.com/webmasters>
2. 選 **從 Google Search Console 匯入** → 授權
3. 驗證與 sitemap 自動帶入，**不用再放第二個檔案**

Bing 的索引同時供給 DuckDuckGo、Yahoo 及部分 AI 搜尋產品，五分鐘的投報率很高。

### Step 6：外部連結（新站最關鍵的一步）

`github.io` 子網域沒有繼承任何權重。Google 判斷這站值不值得排，主要看**有多少地方連過來**。這一步比前五步加起來更影響排名。

| 位置 | 動作 |
| --- | --- |
| GitHub 個人 profile | Edit profile → Website 欄位填網址 |
| 每個公開 repo | About 齒輪 → Website 欄位填網址 |
| GitHub profile README | 正文放一行連結 |
| LinkedIn | 個人檔案 → 聯絡資訊 → 網站 |
| ORCID / Google Scholar | 個人頁加連結 |
| NCCU 系所頁、論文頁 | 可放的話就放 |
| Email 簽名檔 | 加一行 |

## 時程預期

| 階段 | 生效時間 |
| --- | --- |
| 驗證通過 | 立即 |
| sitemap 被讀取 | 數小時 – 2 天 |
| 首頁被索引 | 2 天 – 2 週 |
| 搜「Zih-Jyun Huang」「黃子竣」找得到 | 2 週 – 2 個月，視外部連結多寡 |

## 驗收方式

- Google 搜尋 `site:zihjyunderek.github.io` → 看實際收錄幾頁
- Search Console → **索引 → 網頁** → 已建立索引數量應逐步逼近 18
- Search Console → **成效** → 開始出現曝光與點擊
- 用 <https://opengraph.xyz> 或 <https://metatags.io> 貼網址，確認社群縮圖與標題正確

## 不要做的事

- 不要買外部連結，不要參加連結交換
- 不要在頁面塞隱藏關鍵字或重複堆疊人名
- `meta keywords` 標籤 Google 自 2009 年起完全忽略。`config.ts` 裡那串留著無害（Bing 與少數引擎仍讀），但不用再擴充
- 不要用 sitemap ping 網址（`google.com/ping?sitemap=`）。Google 已於 2023 年停用該端點
- 不要為了 SEO 加第三種字型或改動版面。內容與外部連結才是變數

## 社群縮圖（OG image）快取

縮圖檔案已就地更新（`public/og-default.png`，同檔名，未改程式碼）。各平台的舊快取需要分別處理：

| 平台 | 強制刷新方式 |
| --- | --- |
| Discord | 無官方工具。貼連結時在網址後加 `?v=2` 可立刻看到新圖；一般對話等快取自然過期（數小時至 7 天） |
| LinkedIn | <https://www.linkedin.com/post-inspector/> 貼網址 → 立即重抓 |
| Facebook | Sharing Debugger → Scrape Again |
| X | Card Validator 功能已縮減，通常只能等快取 |
| 瀏覽器 favicon | `Ctrl+Shift+R` 常常不夠。用無痕視窗確認，或清除「快取圖片和檔案」 |

> Discord 的文字與圖片是**兩套獨立快取**，會出現「標題已更新但圖還是舊的」，屬正常現象。

## 檢查清單

- [ ] Search Console 建立 URL prefix 資源
- [ ] `public/googleXXXX.html` 已 push 且線上可存取
- [ ] 驗證通過
- [ ] `sitemap-index.xml` 已提交且狀態為成功
- [ ] 首頁 + 2–3 個重點頁已要求索引
- [ ] Bing Webmaster Tools 已從 GSC 匯入
- [ ] GitHub profile、各 repo About、LinkedIn 都已填網址
- [ ] `site:zihjyunderek.github.io` 搜得到結果
- [ ] opengraph.xyz 顯示新版縮圖
