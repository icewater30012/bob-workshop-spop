# IBM Bob workshop

**SP／OP：Liberty 憑證自動化｜每組選一條路線｜60 分鐘**

[開啟分頁式教材 →](topics/vault-liberty-clm/index.html)

## Workshop 目標

**課內實作：**

- 用 Bob 理解 TLS 憑證生命週期：申請 → 部署 → 監控 → 輪換。
- 使用 Vault PKI，或自行建立 OpenSSL 測試 CA 並簽發憑證。
- 用 Bob 產生 Agent 設定、Shell 或 Ansible，自動部署至 Liberty。
- 驗證線上憑證、重複執行結果，並確認重複執行結果。

**延伸練習：** 用 Bob 建立完整 PKI、AGENTS.md、`/check-cert` Slash Command、可重用 Skill，以及 Frontend Slides 成果簡報。 Cheat sheet 參考：[Bob Cheat Sheet](https://owhc.github.io/bob-cheatsheet/bob-lite-ver.html)

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

Bob 在學員電腦使用；Vault Agent、Shell 或 Ansible 在該組 Liberty VM 執行。OpenSSL 路線不使用 Vault。

| 軟體與位置 | 說明 |
|---|---|
| 作業系統 | RHEL 9.6 |
| Java | OpenJDK 21.0.13 |
| Liberty | `/opt/ibm/wlp`；Server：`defaultServer`；HTTPS：9443；已啟用 HTTPS，預設為自簽 `localhost` 憑證 |
| 登入帳號與權限 | `vpcuser`，可免密碼 `sudo`；Liberty 以 root 執行，`server.xml` 與 keystore 為 root 所有，修改與重啟需用 `sudo` |
| Liberty AdminCenter | `https://<IP>:9443/adminCenter/`（`<IP>` 換成自己 Liberty VM 的 IP）；帳號／密碼：`admin`／`admin123456` |
| Vault Server | 位於 `vault` VM，API Port：8200；Web UI：[https://128.168.136.176:8200/ui](https://128.168.136.176:8200/ui)；帳號／密碼：`admin`／`admin123456` |
| 預裝工具 | OpenSSL、keytool、curl、Vault CLI、Ansible、Python 3；Agent 路線使用 Vault Agent |

### 如何連線

IP、帳號與 SSH key 已匯入 Bob 的 SSH config。在 **Bob IDE Terminal** 輸入表格中的 SSH 指令即可登入。

```bash
ssh liberty1   # 第 1 組；其他組改用自己的編號
```

需要登入共用 Vault 時，在學員電腦的另一個 Terminal 執行 `ssh vault`。輸入 `exit` 離開遠端主機。Vault API 位址與憑證路徑依各 Part 步驟確認。

## 組內角色分工

每組 **5 人**，建議分配為 **1＋3＋1**，也可採 **2＋2＋1**。

| 角色 | 人數 | 任務與交付 |
|---|---|---|
| 🔐 Vault 與憑證管理 | 1～2 人 | 申請憑證、檢查 SAN／效期／信任鏈，交付憑證與設定檔位置 |
| 🤖 自動化／Liberty／維運 | 2～3 人 | 完成部署、線上驗證與重跑檢查，交付執行結果 |
| 📑 統整報告員 | 1 人 | 記錄架構、前後憑證序號與修復方式，整理交接；簡報為延伸 |

由一位操作員負責部署，避免同時修改 keystore；共用 Vault 設定由講師管理。Token、私鑰與密碼不要貼進 Bob 對話。


## 選擇組合

**四選一，每條路線 60 分鐘。** 星等代表本課相對難度。

| 獨立 Part | 難度 | 適合對象 | 時間 |
|---|---|---|---|
| [Part 1：Vault PKI ＋ Vault Agent](topics/vault-liberty-clm/parts/part-1-vault-agent.md) | ⭐⭐⭐⭐ 進階 | 想理解 Vault 持續換證與事件觸發的 SP／OP | 60 分鐘 |
| [Part 2：Vault PKI ＋ Shell／crontab](topics/vault-liberty-clm/parts/part-2-vault-shell.md) | ⭐⭐ 中階 | 熟悉 Shell、想串接集中式簽發的維運人員 | 60 分鐘 |
| [Part 3：OpenSSL ＋ Ansible](topics/vault-liberty-clm/parts/part-3-openssl-ansible.md) | ⭐⭐⭐ 中高階 | 有基本 YAML／Ansible 經驗的平台工程師 | 60 分鐘 |
| [Part 4：OpenSSL ＋ Shell／crontab](topics/vault-liberty-clm/parts/part-4-openssl-shell.md) | ⭐ 入門 | 第一次接觸 CLM、具備基本 Linux 操作經驗者 | 60 分鐘 |
