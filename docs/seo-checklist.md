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

**如果狀態是「無法擷取」**，先看另外兩欄再決定要不要動手：

| 類型 | 上次讀取時間 | 判讀 | 處理 |
| --- | --- | --- | --- |
| 未知 | 空白 | Google 還沒真的讀過，不是抓失敗 | 等 1–2 天，不要刪掉重送 |
| 未知 | 有時間 | 真的抓失敗 | 先自己開 sitemap 網址確認回 200 |
| Sitemap 索引 | 有時間 | 已成功讀取 | 無事 |

新資源剛驗證完就送 sitemap，幾乎都會先停在第一種狀態。反覆刪除重送不會加速，只會讓紀錄變亂。超過 3 天仍未讀取才刪掉重送。

順手可以多送一筆 `sitemap-0.xml`（實際含網址的那份），等於給 Google 第二條路徑，無副作用。

### Step 4：手動要求索引首頁

**這一步和 Step 3 完全獨立，不必等 sitemap 讀取成功。** Google 官方文件明講，網址審查的即時測試「不會檢查該網址是否存在於任何 sitemap 或任何引導連結中」。只要資源驗證通過就能用。

上方搜尋列貼 `https://zihjyunderek.github.io/` → 進入網址審查 → **要求建立索引**。

每日配額約 10 筆，優先順序：

1. 首頁 `/`
2. `/projects/`
3. 最想被搜到的 2–3 個專案頁（例如 `/projects/decoding-the-city-mgwr/`、`/projects/implied-vol-var/`）

> 這個站只有 18 頁，而且每一頁都能從首頁點得到。依 Google 的說法，500 頁以下且能從首頁走到的網站「其實不需要 sitemap」。送出首頁之後，爬蟲會沿著導覽列和專案連結自己走完其餘 17 頁。sitemap 是加速用的保險，不是前提。

### Step 5：Bing Webmaster Tools

1. 開 <https://www.bing.com/webmasters>
2. 選 **從 Google Search Console 匯入** → 授權
3. 驗證與 sitemap 自動帶入，**不用再放第二個檔案**

Bing 的索引同時供給 DuckDuckGo、Yahoo 及部分 AI 搜尋產品，五分鐘的投報率很高。

### Step 6：外部連結

「外部連結」不是 SEO 工具裡的某個設定，也不是要改網站程式碼。它的字面意思就是：**在別人的網站上，放一條指向 `zihjyunderek.github.io` 的連結**。做法是去那些平台的個人資料頁，把網址填進「Website」之類的欄位，或在文章正文裡貼一行連結。全部都在站外操作。

| 位置 | 怎麼做 | 連結類型 |
| --- | --- | --- |
| GitHub 個人 profile | 個人頁 → Edit profile → Website 欄位貼網址 | nofollow |
| 每個公開 repo | repo 首頁右側 About 的齒輪 → Website 欄位貼網址 | nofollow |
| GitHub profile README | `zihjyunderek/zihjyunderek` repo 的 `README.md` 正文加一行 Markdown 連結 | nofollow |
| LinkedIn | 個人檔案 → 編輯 → 聯絡資訊 → 網站 | nofollow |
| ORCID / Google Scholar | 個人頁的 Websites 欄位 | 視平台而定 |
| NCCU 系所頁、論文頁 | 能請系辦加就加 | 多為 dofollow，價值最高 |
| Email 簽名檔 | 加一行網址 | 不是連結，但帶真人流量 |

**誠實的期望值**：GitHub 與 LinkedIn 的連結全部帶 `nofollow`，不會直接傳遞排名權重。它們的價值在於「被爬蟲發現」和「真人點進來」，不在於衝排名。

所以不要把外部連結當成排名的主要槓桿。對「Zih-Jyun Huang」「黃子竣」這種競爭極低的姓名查詢，真正的門檻是**有沒有被收錄**（Step 4），不是權重高低。頁面本身已經把姓名寫在 `<title>`、`<h1>` 和 JSON-LD 的 `alternateName` 裡，收錄之後自然會排在前面。

外部連結仍然值得花二十分鐘做完，因為它是少數在你不在時還能持續作用的事情。但它是輔助，不是關鍵。

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

## 服役期間（2026/08 – 2026/12）

網站是純靜態、部署在 GitHub Pages，沒有任何會過期的東西。人不在也不會壞。但要區分兩件事：

| | 會自己發生 | 需要人動手 |
| --- | --- | --- |
| 被 Google 收錄 | 是，要求索引送出後自動爬取 | 否 |
| 爬完其餘 17 頁 | 是，沿站內連結自己走 | 否 |
| 外部連結累積 | 否 | 是，Step 6 |

**入營前唯一非做不可的是 Step 4（要求索引首頁）**，五分鐘，而且不必等 sitemap。Step 5 和 Step 6 有時間就做，做了更好。

離營期間不會發生的壞事：

- 驗證不會失效，只要 `public/google*.html` 還在 repo 裡
- 沒有 push 就不會觸發部署，網站維持在最後一次成功的版本
- 就算之後某次 build 失敗，Pages 也只是不更新，舊版仍在線

唯一要避免的：**不要開啟 Dependabot PR 的 auto-merge**。人不在時自動合併相依套件更新，build 掛掉你不會知道。

回來後第一件事：打開 Search Console 的「成效」與「索引 → 網頁」，看四個月累積了多少曝光與收錄數，再決定要不要補內容。

## 2026-08-21 稽核（離營放假後的第一次驗收）

### 線上實測

| 檢查項 | 實測結果 | 判定 |
| --- | --- | --- |
| `/robots.txt` | 200，`Allow: /`，已宣告 sitemap | 正常 |
| `/sitemap-index.xml` | 200，指向 `sitemap-0.xml` | 正常 |
| `/sitemap-0.xml` | 200，18 筆 `<loc>` 全部正確 | 正常 |
| 各頁 canonical | 自我指向，無交叉錯置 | 正常 |
| `/projects/` 站內連結 | 13 個專案頁全在靜態 HTML 裡，不靠 JS | 正常 |
| GitHub Actions | 最後一次成功部署 `bc7a232`，線上版本即為 main | 正常 |

結論：**sitemap 不是抓不到，是 Google 還沒回來讀。** 伺服器端沒有任何一項需要修。

### GSC 數字判讀

| 指標 | 數值 | 判讀 |
| --- | --- | --- |
| 已建立索引 | 7 | Google 只認識 18 頁裡的 7 頁 |
| 未建立索引 | 0 | 沒有任何一頁被判定有問題，剩下 11 頁是「尚未被發現」 |
| Sitemap 狀態 | 無法擷取／類型未知／上次讀取時間空白 | 對照 Step 3 的表，屬第一種：還沒真的讀過 |
| 曝光 | 三個月每日約 2–4 次 | 新站加零外部連結的正常值 |
| 點擊 | 0 | 曝光基數太小，還談不上點閱率問題 |

Sitemap 送出日為 2026/8/10，已超過本文件自訂的 3 天門檻，因此這次改為刪除後重送。

### 這次動到的程式碼

技術面本來就沒有缺口，這批改動全部是**實體訊號（entity signal）**與**慣例路徑**的補強，不是修 bug。

| 改動 | 檔案 | 為什麼 |
| --- | --- | --- |
| Person / WebSite / ProfilePage 以固定 `@id` 串成一張圖 | `src/config.ts`、`src/pages/index.astro` | 讓爬蟲把「Zih-Jyun Huang」「Derek Huang」「黃子竣」收斂成同一個實體，而不是三個長得像的節點 |
| Person 補 `image`、`description`、`address`、`knowsLanguage` | `src/pages/index.astro` | 知識面板取用的欄位，缺一項就少一個佐證 |
| 專案頁的 `author` 指回同一個 `@id` | `src/pages/projects/*.astro` | 13 個專案頁的作者訊號回流到首頁那個 Person |
| 中文本名進 `<h1>` | `src/pages/index.astro`、`src/styles/global.css` | 改動前「黃子竣」只出現在 footer 一處可見文字。CLAUDE.md 早就寫「hero、footer、title、JSON-LD 都要有」，實作漏了 hero |
| 新增 `/sitemap.xml` | `src/pages/sitemap.xml.ts`、`astro.config.mjs` | 慣例路徑，之前是 404。不讀 robots.txt 的爬蟲與檢測工具只探這個網址 |
| 404 頁加 `noindex` | `src/layouts/Base.astro`、`src/pages/404.astro` | GitHub Pages 本來就回 HTTP 404，這是給不看狀態碼的爬蟲的保險 |

### 評估過但刻意不做

| 沒做 | 理由 |
| --- | --- |
| sitemap 加 `lastmod` | 靜態站唯一能填的是 build 時間，18 頁會全部相同且每次部署都變。Google 判定 `lastmod` 不可信時就整個忽略，填了反而是雜訊 |
| 改首頁 `<title>` 加職稱 | 姓名查詢的競爭度本來就接近零，`<title>` 已含中英文全名。改文案的風險大於收益 |
| 把 CV PDF 塞進 sitemap | PDF 已從首頁與 `/contact/` 連得到，爬得到。刻意推 PDF 反而可能讓它排在 HTML 頁前面，那是比較差的著陸體驗 |
| `meta keywords` 擴充 | 見上文「不要做的事」，Google 自 2009 年起完全忽略 |

### 回營前的動作順序

1. GSC → Sitemap → 把 `/sitemap-0.xml` 與 `/sitemap-index.xml` 兩筆**刪除**，重新送出 `sitemap-index.xml`（順手可再送 `sitemap.xml`）
2. GSC → 網址審查 → 對尚未收錄的 11 頁**要求建立索引**，每日配額 10 筆，兩天送完
3. Step 6 的外部連結：GitHub profile、各 repo About、LinkedIn，二十分鐘做完
4. 兩週後回頭看「索引 → 網頁」的已建立索引數是否往 18 靠

第 1 步和第 2 步互相獨立，不必等 sitemap 讀取成功才做第 2 步。

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
