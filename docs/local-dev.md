# 本機開發手冊（Local Development）

這份文件說明如何**在自己電腦上預覽與修改網站，確認沒問題後才推上 GitHub**。

> 路徑說明：`dev.bat` 與 `preview.bat` 都在 `scripts/`，兩者都會自動切回 repo 根目錄執行。

## 一次性安裝（只做一次）

安裝 [Node.js LTS 版](https://nodejs.org/)（建議 v22）。安裝完成後，雙擊 `scripts/dev.bat`，第一次會自動執行 `npm install` 安裝相依套件（1–2 分鐘），之後不會再裝。

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

## 最常改的三個地方

1. **新增/修改專案** → `src/content/projects/*.md`（一個檔＝一個專案，frontmatter 規格見 README）
2. **個人資料、連結** → `src/config.ts`
3. **經歷、學歷、技能條** → `src/data/profile.ts`

## 檔案保留原則：Only public

repo 內**所有被 git 追蹤的檔案都是可公開的**，沒有 private/public 分流。`.gitignore` 只排除三類：產生物（`dist/`、`node_modules/`）、機密（`.env`、金鑰），以及本機的 agent 設定（`CLAUDE.md`）。若某個檔案不能公開，它就不該進這個 repo。

## 常見問題

**Port 4321 被占用** — 前一個伺服器沒關。關掉舊的視窗，或改用 `npm run dev -- --port 4322`。

**畫面怪怪的/套件壞掉** — 刪掉 `node_modules` 資料夾後重新雙擊 `scripts/dev.bat`（會自動重裝）。

**改了 `src/content/` 的 frontmatter 後 build 失敗** — 這是設計好的保護：欄位有 schema 驗證（`src/content.config.ts`），錯誤訊息會指出哪個檔案哪個欄位打錯。

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
