# IBM Bob workshop

**SP／OP：Liberty 憑證自動化｜四個獨立情境，每組選一個｜60 分鐘**

[開啟分頁式教材 →](topics/vault-liberty-clm/index.html)

## Workshop 目標

**課內實作：**

- 用 Bob 理解 TLS 憑證生命週期：申請 → 部署 → 監控 → 輪換。
- 使用 Vault PKI，或自行建立 OpenSSL 測試 CA 並簽發憑證。
- 用 Bob 產生 Agent 設定、Shell 或 Ansible，自動部署至 Liberty。
- 驗證線上憑證，並確認重複執行結果。

**延伸練習：** 用 Bob 建立完整 PKI、AGENTS.md、`/check-cert` Slash Command、可重用 Skill。

**成果簡報：** 統整報告員用 Frontend Slides Skill 製作，安裝與使用步驟見下方〈統整報告員〉。

## 實作環境與各組分配

**IBM TechZone｜1 台共用 Vault＋8 台 Liberty。各組只操作自己的 Liberty。**

| VM 編號 | 用途與組別分配 | 規格（每台） | Bob IDE Terminal 連線指令 |
|---|---|---|---|
| `vault-server` | 各組共用 Vault Server，由講師管理 | RHEL 9.6／4 vCPU／16 GB RAM／100 GB 磁碟 | `ssh vault` |
| `liberty1` | 第 1 組專用 Liberty | RHEL 9.6／2 vCPU／8 GB RAM／100 GB 磁碟 | `ssh liberty1` |
| `liberty2` | 第 2 組專用 Liberty | RHEL 9.6／2 vCPU／8 GB RAM／100 GB 磁碟 | `ssh liberty2` |
| `liberty3` | 第 3 組專用 Liberty | RHEL 9.6／2 vCPU／8 GB RAM／100 GB 磁碟 | `ssh liberty3` |
| `liberty4` | 第 4 組專用 Liberty | RHEL 9.6／2 vCPU／8 GB RAM／100 GB 磁碟 | `ssh liberty4` |
| `liberty5` | 第 5 組專用 Liberty | RHEL 9.6／2 vCPU／8 GB RAM／100 GB 磁碟 | `ssh liberty5` |
| `liberty6` | 第 6 組專用 Liberty | RHEL 9.6／2 vCPU／8 GB RAM／100 GB 磁碟 | `ssh liberty6` |
| `liberty7` | 第 7 組專用 Liberty | RHEL 9.6／2 vCPU／8 GB RAM／100 GB 磁碟 | `ssh liberty7` |
| `liberty8` | 第 8 組專用 Liberty | RHEL 9.6／2 vCPU／8 GB RAM／100 GB 磁碟 | `ssh liberty8` |

Bob 在學員電腦使用；Vault Agent、Shell 或 Ansible 在該組 Liberty VM 執行。OpenSSL 情境不使用 Vault。

| 軟體與位置 | 說明 |
|---|---|
| 作業系統 | RHEL 9.6 |
| Java | OpenJDK 21.0.13 |
| Liberty | `/opt/ibm/wlp`；Server：`defaultServer`；HTTPS：9443；已啟用 HTTPS，預設為自簽 `localhost` 憑證 |
| 登入帳號與權限 | `vpcuser`，可免密碼 `sudo`；Liberty 以 root 執行，`server.xml` 與 keystore 為 root 所有，修改與重啟需用 `sudo` |
| Liberty AdminCenter | `https://<IP>:9443/adminCenter/`（`<IP>` 換成自己 Liberty VM 的 IP）；帳號／密碼：`admin`／`admin123456` |
| Vault Server | 位於 `vault` VM，API Port：8200；Web UI：[https://128.168.136.176:8200/ui](https://128.168.136.176:8200/ui)；帳號／密碼：`admin`／`admin123456` |
| 預裝工具 | OpenSSL、keytool、curl、Vault CLI、Ansible、Python 3；Agent 情境使用 Vault Agent |

### 如何連線

IP、帳號與 SSH key 已匯入 Bob 的 SSH config。在 **Bob IDE Terminal** 輸入表格中的 SSH 指令即可登入。

```bash
ssh liberty1   # 第 1 組；其他組改用自己的編號
```

需要登入共用 Vault 時，在學員電腦的另一個 Terminal 執行 `ssh vault`。輸入 `exit` 離開遠端主機。Vault API 位址與憑證路徑依各 Scenario 步驟確認。

## 組內角色分工

每組 **5 人**，建議分配為 **1＋3＋1**，也可採 **2＋2＋1**。

| 角色 | 人數 | 任務與交付 |
|---|---|---|
| 🔐 憑證管理者 | 1～2 人 | 申請或簽發憑證（Vault 或 OpenSSL）、檢查 SAN／效期／信任鏈，交付憑證與設定檔位置 |
| 🤖 AP／維運 | 2～3 人 | 把憑證部署到 Liberty（keystore、重啟腳本）、線上驗證、排程與重跑檢查，交付執行結果 |
| 📑 統整報告員（Presenter） | 1 人 | 記錄架構、前後憑證序號與修復方式，整理交接；用 Frontend Slides Skill 產生成果簡報（安裝步驟見[下方](#統整報告員用-frontend-slides-做成果簡報)） |

各 Scenario 每個步驟標題下方會標示「主責角色」與「協作」，由該角色在組內主導該步驟。

由一位操作員負責部署，避免同時修改 keystore；共用 Vault 設定由講師管理。Token、私鑰與密碼不要貼進 Bob 對話。


## 統整報告員：用 Frontend Slides 做成果簡報

統整報告員（Presenter）要在課程結束前，用 **Frontend Slides Skill** 讓 Bob 產生一份 HTML 成果簡報（單一檔案，瀏覽器直接開啟）。Skill 檔案放在本 repo 的 [`skills/frontend-slides/`](https://github.com/icewater30012/bob-workshop-spop/tree/dev/skills/frontend-slides)。

### 1. 安裝 Skill（約 3 分鐘，在學員電腦做，不是 Liberty VM）

Bob 會從 `~/.bob/skills/`（全域）或專案的 `.bob/skills/` 載入 Skill；每個 Skill 是一個資料夾，裡面要有 `SKILL.md`。

**macOS／Linux：**

```bash
git clone -b dev https://github.com/icewater30012/bob-workshop-spop.git
mkdir -p ~/.bob/skills
cp -R bob-workshop-spop/skills/frontend-slides ~/.bob/skills/
ls ~/.bob/skills/frontend-slides   # 應看到 SKILL.md、STYLE_PRESETS.md、viewport-base.css 等
```

**Windows（PowerShell）：**

```powershell
git clone -b dev https://github.com/icewater30012/bob-workshop-spop.git
New-Item -ItemType Directory -Force "$HOME\.bob\skills" | Out-Null
Copy-Item -Recurse bob-workshop-spop\skills\frontend-slides "$HOME\.bob\skills\"
dir "$HOME\.bob\skills\frontend-slides"
```

沒有 `git` 或連不到 GitHub：向講師索取 `frontend-slides` 資料夾，整個放進 `~/.bob/skills/` 即可。

### 2. 確認 Bob 已載入

1. 重新開啟 Bob 的聊天視窗（必要時重啟 Bob IDE），切到 **Agent mode**。
2. 在聊天輸入框打 `/`，選單中應出現 `frontend-slides`；或到 **Bob Settings → Skills** 查看是否在清單中。
3. 看不到時，確認路徑是 `~/.bob/skills/frontend-slides/SKILL.md`（不要多一層資料夾）。

### 3. 蒐集簡報素材

在學員電腦的專案資料夾建立 `slides/`，把素材放進去（**不要放 Token、私鑰、密碼**）：

```bash
mkdir -p slides && cd slides
scp liberty1:~/clm-workshop/before.txt .   # 第 1 組；其他組換編號
scp liberty1:~/clm-workshop/after.txt .
```

另外準備：AdminCenter 憑證畫面的截圖（換證前後各一張）、本組選的 Scenario、遇到的問題與解法。

### 4. 讓 Bob 產生簡報

在 Bob 聊天輸入下面的提示（把括號內換成本組資訊）：

```text
/frontend-slides
請為我們組做 5 分鐘的成果簡報，約 6～8 張，內容依序：
1. 我們選的情境（Scenario N）與架構。
2. 換證前後的憑證序號與到期日（讀取 slides/before.txt、slides/after.txt）。
3. 驗證方式與結果（check_cert、AdminCenter 瀏覽器畫面，截圖放在 slides/）。
4. 遇到的問題與解法。
5. 後續維運建議（Token 到期、cron 排程）。
風格偏專業、清楚；產出單一 HTML 檔放在 slides/。
```

Skill 會先問長度、風格等問題，並產生 3 個風格預覽讓你挑選，再產出完整簡報；完成後用瀏覽器開啟，方向鍵翻頁。

### 5. 注意事項

- 簡報裡**不要出現** Vault Token、Secret ID、私鑰或密碼；截圖前先確認畫面沒有這些資訊。
- Skill 的「部署到 Vercel」與「匯出 PDF」是選用功能，不需要完成；課堂以瀏覽器直接簡報即可。

## 選擇情境

**四個 Scenario 各自獨立、互不相依，沒有先後順序；每組只選一個，60 分鐘完成。** 星等代表本課相對難度。

| 獨立情境 | 難度 | 適合對象 | 時間 |
|---|---|---|---|
| [Scenario 1：Vault PKI ＋ Vault Agent](topics/vault-liberty-clm/parts/part-1-vault-agent.md) | ⭐⭐⭐⭐ 進階 | 想理解 Vault 持續換證與事件觸發的 SP／OP | 60 分鐘 |
| [Scenario 2：Vault PKI ＋ Shell／crontab](topics/vault-liberty-clm/parts/part-2-vault-shell.md) | ⭐⭐ 中階 | 熟悉 Shell、想串接集中式簽發的維運人員 | 60 分鐘 |
| [Scenario 3：OpenSSL ＋ Ansible](topics/vault-liberty-clm/parts/part-3-openssl-ansible.md) | ⭐⭐⭐ 中高階 | 有基本 YAML／Ansible 經驗的平台工程師 | 60 分鐘 |
| [Scenario 4：OpenSSL ＋ Shell／crontab](topics/vault-liberty-clm/parts/part-4-openssl-shell.md) | ⭐ 入門 | 第一次接觸 CLM、具備基本 Linux 操作經驗者 | 60 分鐘 |
