# 本機開發手冊（Local Development）

這份文件說明如何**在自己電腦上預覽與修改網站，確認沒問題後才推上 GitHub**。

> 路徑說明：`dev.bat` 與 `preview.bat` 都在 `scripts/`，兩者都會自動切回 repo 根目錄執行。

## 一次性安裝（只做一次）

安裝 [Node.js LTS 版](https://nodejs.org/)（建議 v24，與 GitHub Actions 相同；目前安裝的 Astro 7.4 最低需要 v22.23.4）。安裝完成後，雙擊 `scripts/dev.bat`，第一次會自動執行 `npm install` 安裝相依套件（1–2 分鐘），之後不會再裝。

## 日常工作流程

```text
雙擊 scripts/dev.bat ──> 瀏覽器自動開 http://localhost:4321
      │
      ▼
編輯 src/ 內的檔案 ──> 存檔後瀏覽器即時更新（熱重載，不用重開）
      │
      ▼
改完想最後確認 ──> 雙擊 scripts/preview.bat（產出正式版 dist/ 並預覽，
      │             內容與 GitHub Pages 上線版完全一致）
      ▼
滿意了 ──> git push 到 main，GitHub Actions 自動部署上線
```

重點：**所有修改在 push 之前都只存在你的電腦上**，外界看不到。localhost 預覽不需要網路。

## 兩個指令的差別

| 指令 | 用途 | 何時用 |
| --- | --- | --- |
| `scripts/dev.bat`（= `npm run dev`） | 開發伺服器，存檔即時更新 | 平常修改時 |
| `scripts/preview.bat`（= `npm run build` + `npm run preview`） | 產出並預覽正式靜態檔 | push 前的最終檢查 |

dev 模式為了即時性會跳過部分優化；preview 才是 GitHub Pages 真正會發布的內容。**push 前跑一次 preview.bat，build 失敗就代表 GitHub Actions 也會失敗**，在本機先修好。

> 習慣用終端機的話，在 repo 資料夾執行 `npm run dev` / `npm run build` / `npm run preview` 效果相同；`-- --open` 可自動開瀏覽器。

## 最常改的四個地方

1. **新增/修改專案** → `src/content/projects/`（一個檔＝一個專案，frontmatter 規格見 README）
2. **個人資料、連結** → `src/config.ts`
3. **經歷、學歷、技能條** → `src/data/profile.ts`
4. **在專案頁加圖或表** → 三步驟，完整規格見 README 的「Add a figure」：
   - 把該專案檔的副檔名改成 `.mdx`，frontmatter 加一行 `basis`（`published`、`public-data` 或 `simulated`）
   - CSV 放進 `src/data/figures/<專案檔名>/`，並在 `src/data/figures/README.md` 記一行來源
   - 在內文兩段文字之間插入 `<Figure ... />`

圖表在 build 時畫成 SVG 與 HTML，網頁不載入任何 JavaScript。要改圖上的數字就改 CSV，要改顏色就改 `src/styles/global.css` 的 `--data-*`、`--seq-*`、`--pos-*`、`--neg-*`、`--cat-*`。版面、間距、用色與文字的規則寫在 `docs/figure-guidelines.md`。

## 重新產生圖表資料

受 NDA 保護的專案頁，圖表改用公開的 ACS（美國社區調查）資料重跑同一套方法。資料與分析腳本都在 repo 裡：

```text
python scripts\fetch_acs.py                       只需一次；API key 放在 repo 根目錄的 .env（已被 .gitignore 排除）
python scripts\extract_tracts.py <tract 圖層路徑>  只需一次；從 tract 邊界圖層只取 GEOID 和多邊形
python scripts\draw_study_cities.py <shapefiles 資料夾>  只需一次；CDI-Milestone 的 15 城市示意圖，只用邊界
pip install -r scripts\requirements-figures.txt   分析用的 Python 套件（網站本身不需要）
python scripts\build_figures.py                   重跑全部分析，覆寫 src/data/figures/ 的 CSV 與地圖形狀
```

- `.env` 內容只有一行：`CENSUS_API_KEY=你的key`。這個檔案不會進 commit，也不要貼到別處。
- 分析的設定（變數、K、亂數種子、地圖的繪製精度）集中在 `scripts/figures/config.py`。
- 地圖的 tract 邊界在 `scripts/figures/data/geometry/`：Census TIGER/Line 2023 的 tract，已裁掉水域，只保留 GEOID 一個欄位。不要加入任何其他屬性；邊界以外的資料一律不放進來。
- MGWR 那一段約需十五分鐘。重跑後，頁面內文引用的數字要對照新的 CSV 檢查一次。

## 檔案保留原則：Only public

repo 內**所有被 git 追蹤的檔案都是可公開的**，沒有 private/public 分流。`.gitignore` 只排除三類：產生物（`dist/`、`node_modules/`）、機密（`.env`、金鑰），以及本機的 agent 設定（`CLAUDE.md`）。若某個檔案不能公開，它就不該進這個 repo。

## 常見問題

**Port 4321 被占用** — 前一個伺服器沒關。關掉舊的視窗，或改用 `npm run dev -- --port 4322`。

**畫面怪怪的/套件壞掉** — 刪掉 `node_modules` 資料夾後重新雙擊 `scripts/dev.bat`（會自動重裝）。

**`git pull` 或切換分支後套件有變動（Dependabot 更新，或加入圖表功能的那次 commit）** — 執行一次 `npm ci`，本機才會換成新版套件。`dev.bat` 與 `preview.bat` 只在 `node_modules` 不存在時安裝，不會自動更新；沒同步的話，本機 preview 跑的是舊版 Astro，結果不等於線上版。用 `npm ci` 而不是 `npm install`，才不會改動 `package-lock.json`。

**出現 `Node.js vXX is not supported by Astro!`** — 本機或 CI 的 Node 版本低於 Astro 的最低需求（Astro 7.4 為 v22.23.4，可用 `node -v` 確認）。本機請安裝 v24 LTS 後重開終端機；CI 的版本在 `.github/workflows/deploy.yml` 的 `node-version`。

**改了 `src/content/` 的 frontmatter 後 build 失敗** — 這是設計好的保護：欄位有 schema 驗證（`src/content.config.ts`），錯誤訊息會指出哪個檔案哪個欄位打錯。

**圖表造成 build 失敗** — 訊息開頭是 `Figure <專案>/<檔名>:`，後面直接寫缺了哪個檔案、哪個欄位，或是 frontmatter 少了 `basis`。照訊息補上即可。

**`node_modules/` 和 `dist/` 要不要 commit？** — 不要，`.gitignore` 已自動排除，正常 `git add -A` 即可。

## 部署

repo 為**公開**，部署全自動：push 到 `main` 後 GitHub Actions 會自動 build 並發布到 GitHub Pages。

一次性設定：GitHub → **Settings → Pages → Source → GitHub Actions**。

```bash
git add -A
git commit -m "..."
git push          # → CI 自動 build & 部署，約 1–2 分鐘上線
```

也可到 GitHub → Actions → *Deploy to GitHub Pages* → Run workflow 手動觸發。
