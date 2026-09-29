<!-- Created: 2026-09-29 14:25:57 +0800 -->
<!-- Updated: 2026-09-29 16:58:48 +0800 -->
# Vault + Liberty 憑證生命週期管理（CLM）

> **用途**：IBM Bob Workshop — 兆豐銀行 MEGA 專場（SP / OP 人員統一題目）
> **難度**：⭐⭐⭐ 中等 ～ ⭐⭐⭐⭐ 進階（依模組組合而定）
> **時長**：2 小時
> **角色**：SP（系統平台）/ OP（維運操作）人員

---

## 📋 專案簡介

憑證到期是銀行維運最高頻的緊急事件之一。手動置換流程冗長、容易出錯，一旦漏掉就可能造成服務中斷。

在本 Workshop 中，你將以 **IBM Bob** 作為 AI 輔助工具，從零開始建立一套 **WAS Liberty TLS 憑證生命週期管理（CLM）** 機制。題目採用**模組化設計**：先選擇你的「憑證來源」，再選擇你的「部署方式」，自由組合出最符合你環境需求的實作路徑。

---

## 🎯 Workshop 目標

完成本 Workshop 後，你將能夠：

- ✅ 使用 Bob 理解 TLS 憑證的生命週期（申請 → 部署 → 監控 → 輪換）
- ✅ 使用 Bob 建立 HashiCorp Vault PKI Secrets Engine，或使用 OpenSSL 自簽憑證
- ✅ 使用 Bob 透過 Vault Agent、Shell Script 或 Ansible 自動部署憑證至 Liberty
- ✅ 使用 Bob 建立 AGENTS.md 記錄環境特性，避免重複踩坑
- ✅ 使用 Bob 產生 Slash Command，一鍵檢查憑證狀態
- ✅ 使用 Bob 建立並安裝自己的 SKILL，將 CLM 流程封裝為可重用工具
- ✅ 使用 Bob + Frontend Slides Skill 製作技術簡報，展示實作成果

---

## 🏗️ 環境說明

| 元件 | 說明 |
|------|------|
| **WAS Liberty 版本** | IBM WebSphere Liberty 26.0.0.9（Jakarta EE 11）|
| **JDK** | OpenJDK 17 |
| **作業系統** | RHEL 9 |
| **連線方式** | SSH（講師提供帳號密碼）|
| **Liberty 安裝路徑** | `/opt/ibm/wlp` |
| **Server 名稱** | `defaultServer` |
| **Vault 版本** | HashiCorp Vault 2.0（已預裝，`http://127.0.0.1:8200`）|
| **Vault Token** | 由講師預先申請，每組一組（共 5～6 組）|

> 環境已預裝：`openssl`、`keytool`、`curl`、`vault` CLI、`ansible`

---

## 🗺️ 模組化學習路徑

本題目分為兩個階段，**每個階段各選一個模組**，組合出你的實作路徑：

```
┌─────────────────────────────────────────────┐
│           Stage 1：憑證來源模組               │
│                                             │
│  [模組 A] Vault PKI Secrets Engine          │
│  [模組 B] OpenSSL 自簽憑證                   │
└─────────────────────┬───────────────────────┘
                      │ 取得憑證檔案後
                      ▼
┌─────────────────────────────────────────────┐
│           Stage 2：部署模組                  │
│                                             │
│  [模組 1] Vault Agent（自動 sidecar）        │
│  [模組 2] Shell Script + crontab            │
│  [模組 3] Ansible Playbook                  │
└─────────────────────────────────────────────┘
```

### 推薦組合

| 你的背景 | 推薦路徑 | 難度 |
|---------|---------|------|
| 想學 Vault 完整流程 | 模組 A → 模組 1 | ⭐⭐⭐⭐ |
| 維運導向、想快速自動化 | 模組 A → 模組 2 | ⭐⭐⭐ |
| 熟悉 Ansible 的平台工程師 | 模組 B → 模組 3 | ⭐⭐⭐⭐ |
| 第一次接觸 CLM | 模組 B → 模組 2 | ⭐⭐ |

> **注意**：模組 B（OpenSSL）不建議搭配模組 1（Vault Agent），因為 Vault Agent 設計上需要 Vault PKI 作為憑證來源。

---

## 🔧 共用前置作業（所有人必做）

在選擇模組之前，先完成以下共用步驟。

### Step 0｜理解憑證生命週期

在 Bob 中輸入：
```
我是銀行 SP/OP 人員，需要了解 TLS 憑證生命週期管理（CLM）。
請解釋：
1. 憑證生命週期的各個階段（申請、核發、部署、監控、輪換、撤銷）
2. HashiCorp Vault PKI Secrets Engine 在 CLM 中的角色
3. WAS Liberty 使用哪種 Keystore 格式（JKS vs PKCS12）
4. 自動輪換 vs 手動置換的風險差異
```

### Step 0.1｜準備 Liberty 環境

```bash
# 確認 Liberty 運行中
/opt/ibm/wlp/bin/server status defaultServer

# 確認目前憑證狀態
echo | openssl s_client -connect localhost:9443 2>/dev/null \
  | openssl x509 -noout -dates 2>/dev/null || echo "尚未設定 HTTPS"

# 建立憑證工作目錄
sudo mkdir -p /opt/certs && sudo chown $USER:$USER /opt/certs
sudo mkdir -p /opt/scripts
```

---

## 📦 Stage 1 — 憑證來源模組

---

### 模組 A｜Vault PKI Secrets Engine

> 使用 HashiCorp Vault 建立 PKI CA，讓 Vault 成為你的內部憑證中心。

**時間**：40 分鐘

#### Step A-1｜請 Bob 解釋 Vault PKI 架構

在 Bob 中輸入：
```
請解釋 HashiCorp Vault PKI Secrets Engine 的架構：
1. Root CA 和 Intermediate CA 的差異與為何要分層
2. Vault Role 的用途（限制 CN、TTL、允許的網域）
3. 申請憑證的 API 端點（vault write pki/issue/...）
4. 憑證到期前如何透過 Vault 自動 renew
請用銀行內部 CA 的場景舉例說明。
```

#### Step A-2｜啟用 PKI Secrets Engine 並建立 Root CA

```bash
# 設定 Vault 環境變數
export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="<講師提供的 Root Token>"

# 啟用 PKI Secrets Engine
vault secrets enable pki

# 設定最長 TTL（Root CA 10 年）
vault secrets tune -max-lease-ttl=87600h pki
```

把以上步驟貼給 Bob，請它產生建立 Root CA 的完整指令：
```
我已啟用 Vault PKI Engine。
請幫我產生以下指令：
1. 建立 Root CA（CN: MEGA-Root-CA，TTL 10 年）
2. 設定 CRL 和 Issuing Certificate URL（Base URL: http://127.0.0.1:8200）
3. 建立 Intermediate CA（CN: MEGA-Intermediate-CA，TTL 5 年）
4. 用 Root CA 簽署 Intermediate CA 的 CSR

Vault 位址：http://127.0.0.1:8200
```

#### Step A-3｜建立 Liberty 專用 Role

在 Bob 中輸入：
```
我的 Vault PKI Intermediate CA 已建立完成。
請幫我建立一個 Vault PKI Role，名稱為 "liberty-server"，限制：
- 允許的 Common Name：*.bank.local
- 允許的 SAN（DNS）：mega-liberty.bank.local、localhost
- 憑證 TTL：30 天（max 90 天）
- 允許 IP SAN：127.0.0.1
- 憑證用途：server auth

請提供 vault write 指令。
```

#### Step A-4｜測試申請憑證

```bash
# 向 Vault 申請 Liberty 憑證
vault write pki_int/issue/liberty-server \
  common_name="mega-liberty.bank.local" \
  ttl="30d" \
  -format=json > /opt/certs/vault-cert.json

# 拆分憑證檔案
cat /opt/certs/vault-cert.json | python3 -c "
import sys, json
data = json.load(sys.stdin)['data']
open('/opt/certs/server.crt', 'w').write(data['certificate'])
open('/opt/certs/server.key', 'w').write(data['private_key'])
open('/opt/certs/ca-chain.crt', 'w').write(data['ca_chain'][0])
print('憑證到期日：', data['expiration'])
"

# 驗證憑證
openssl x509 -in /opt/certs/server.crt -text -noout | grep -A3 "Validity"
```

把輸出貼給 Bob 確認憑證內容是否符合預期。

**完成後**：繼續到 Stage 2 選擇部署模組。

---

### 模組 B｜OpenSSL 自簽憑證

> 使用 OpenSSL 建立自簽 CA，適合快速驗證或無 Vault 環境的場景。

**時間**：25 分鐘

#### Step B-1｜請 Bob 產生建立自簽 CA 的腳本

在 Bob 中輸入：
```
請幫我寫一個 Shell Script，使用 OpenSSL 完成以下步驟：
1. 建立 Root CA（私鑰 + 自簽憑證，CN: MEGA-Root-CA，有效期 3650 天）
2. 建立 Server 私鑰
3. 建立 Server CSR（CN: mega-liberty.bank.local，SAN: localhost, 127.0.0.1）
4. 用 Root CA 簽署 Server 憑證（有效期 90 天）
5. 驗證憑證並顯示到期日

所有檔案輸出到 /opt/certs/
腳本執行完畢後顯示「憑證建立完成」和到期日。
```

#### Step B-2｜執行並驗證

```bash
chmod +x /opt/certs/create-certs.sh && /opt/certs/create-certs.sh

# 驗證憑證鏈
openssl verify -CAfile /opt/certs/ca.crt /opt/certs/server.crt

# 顯示到期日
openssl x509 -in /opt/certs/server.crt -noout -dates
```

把輸出貼給 Bob 確認憑證鏈是否正確。

#### Step B-3｜轉換為 PKCS12 格式（Liberty 需要）

在 Bob 中輸入：
```
我已建立 PEM 格式的憑證（/opt/certs/server.crt + server.key + ca.crt）。
請提供 openssl 指令，將其打包為 PKCS12 格式：
- 輸出檔案：/opt/certs/keystore.p12
- keystore 密碼：changeit
- 別名：mega-liberty
- 包含完整憑證鏈
```

```bash
# 執行 Bob 產生的轉換指令
# 驗證 PKCS12 內容
keytool -list -v -keystore /opt/certs/keystore.p12 \
  -storetype PKCS12 -storepass changeit | grep -E "Alias|Valid|Owner"
```

**完成後**：繼續到 Stage 2 選擇部署模組。

---

## 🚀 Stage 2 — 部署模組

> 以下三個模組均假設你已完成 Stage 1，並取得 `/opt/certs/keystore.p12`（或等效憑證檔案）。

---

### 模組 1｜Vault Agent 自動部署

> Vault Agent 以 sidecar 方式持續監控憑證狀態，到期前自動 renew 並重新載入 Liberty。
> **前置條件**：必須完成 Stage 1 模組 A（Vault PKI）。

**時間**：45 分鐘

#### Step 1-1｜請 Bob 解釋 Vault Agent 運作原理

在 Bob 中輸入：
```
請解釋 HashiCorp Vault Agent 的憑證自動更新流程：
1. Vault Agent 如何使用 auto-auth 取得 Vault Token
2. Template 功能如何將 Vault Secret 寫入本地檔案
3. exec 或 command 如何在憑證更新後觸發 Liberty reload
4. Vault Agent 的設定檔結構（HCL 格式）
請提供一個適用於 WAS Liberty 憑證輪換的完整範例。
```

#### Step 1-2｜建立 Vault Agent AppRole 認證

```bash
# 啟用 AppRole auth method
vault auth enable approle

# 建立 Liberty 專用 Policy
vault policy write liberty-clm - <<EOF
path "pki_int/issue/liberty-server" {
  capabilities = ["create", "update"]
}
path "pki_int/renew" {
  capabilities = ["create", "update"]
}
EOF

# 建立 AppRole
vault write auth/approle/role/liberty-agent \
  token_policies="liberty-clm" \
  token_ttl=1h \
  token_max_ttl=4h

# 取得 Role ID 和 Secret ID
vault read auth/approle/role/liberty-agent/role-id
vault write -f auth/approle/role/liberty-agent/secret-id
```

#### Step 1-3｜建立 Vault Agent 設定檔

把上一步取得的 Role ID 和 Secret ID 提供給 Bob：
```
請幫我建立 Vault Agent 的設定檔 /etc/vault-agent/liberty-agent.hcl：

Vault 位址：http://127.0.0.1:8200
認證方式：AppRole
Role ID：<上一步取得>
Secret ID 檔案：/etc/vault-agent/secret-id

Template 需求：
- 從 pki_int/issue/liberty-server 申請憑證（TTL 30d）
- 將憑證寫入 /opt/certs/server.crt
- 將私鑰寫入 /opt/certs/server.key
- 憑證更新後執行：/opt/scripts/reload-liberty.sh

請同時提供 /opt/scripts/reload-liberty.sh 的內容（重新載入 Liberty 的腳本）。
```

#### Step 1-4｜啟動 Vault Agent 並驗證

```bash
sudo mkdir -p /etc/vault-agent
# 將 Bob 產生的設定寫入檔案後：

# 啟動 Vault Agent
vault agent -config=/etc/vault-agent/liberty-agent.hcl &

# 觀察憑證是否被自動寫入
watch -n 5 'openssl x509 -in /opt/certs/server.crt -noout -dates 2>/dev/null'

# 確認 Liberty 使用新憑證
echo | openssl s_client -connect localhost:9443 2>/dev/null \
  | openssl x509 -noout -subject -dates
```

把 Vault Agent 的 log 輸出貼給 Bob 確認是否正常運行。

#### Step 1-5（進階）｜設定 systemd 服務

在 Bob 中輸入：
```
請幫我為 Vault Agent 建立 systemd service unit 檔案 /etc/systemd/system/vault-agent-liberty.service，
需求：
- 開機自動啟動
- 失敗後自動重試（Restart=on-failure，重試間隔 30 秒）
- 以非 root 用戶執行（User=vault）
請同時提供啟用和驗證服務狀態的指令。
```

---

### 模組 2｜Shell Script + crontab 自動部署

> 使用 Shell Script 整合憑證申請（來源可選 Vault PKI 或 OpenSSL）與 Liberty 重啟，並設定 crontab 定期檢查輪換。

**時間**：40 分鐘

#### Step 2-1｜請 Bob 設計完整的 cert-rotate.sh

在 Bob 中輸入（依你選擇的 Stage 1 模組調整「憑證來源」那段）：
```
請幫我撰寫一支 /opt/scripts/cert-rotate.sh，實現以下邏輯：

1. 檢查現有憑證到期日，若距到期 > 30 天則結束（無需輪換）
2. 憑證來源：[選 A: 呼叫 Vault API 申請新憑證] 或 [選 B: 執行 OpenSSL 產生新自簽憑證]
3. 將新憑證轉換為 PKCS12 格式（/opt/certs/keystore.p12）
4. 備份舊的 keystore 和 server.xml（備份路徑加日期戳記）
5. 更新 Liberty server.xml 中的 keyStore 設定
6. 重啟 Liberty（/opt/ibm/wlp/bin/server stop + start）
7. 等待 Liberty 啟動完成後，用 openssl s_client 驗證新憑證已生效
8. 若驗證失敗，自動 rollback 到備份版本並重啟
9. 所有步驟寫入 /var/log/cert-rotate.log（含時間戳記）

Liberty 路徑：/opt/ibm/wlp/usr/servers/defaultServer
Keystore 路徑：/opt/certs/keystore.p12
Keystore 密碼：changeit
```

#### Step 2-2｜請 Bob 撰寫 Liberty server.xml 設定

在 Bob 中輸入：
```
請幫我撰寫 WAS Liberty 23.0 的 server.xml SSL 設定片段，需求：
- Keystore 路徑：/opt/certs/keystore.p12（PKCS12 格式）
- Keystore 密碼：changeit（建議改用環境變數方式）
- 只允許 TLSv1.2、TLSv1.3
- 停用弱加密套件
- HTTPS 監聽 Port：9443
請說明每個設定項目的用途。
```

#### Step 2-3｜測試腳本執行

```bash
chmod +x /opt/scripts/cert-rotate.sh

# 首次執行（強制模式，忽略到期日檢查）
FORCE=true /opt/scripts/cert-rotate.sh

# 查看執行日誌
tail -50 /var/log/cert-rotate.log

# 驗證新憑證
echo | openssl s_client -connect localhost:9443 2>/dev/null \
  | openssl x509 -noout -subject -dates
```

把日誌內容和 `openssl` 輸出貼給 Bob 確認。

#### Step 2-4｜設定 crontab 排程

在 Bob 中輸入：
```
請幫我設定 crontab 排程：
- 每天凌晨 02:00 執行 cert-rotate.sh
- 執行結果 append 到 /var/log/cert-rotate.log
- 同時說明如何查看 crontab 是否已生效，以及如何手動觸發測試
```

```bash
crontab -e  # 加入 Bob 產生的排程設定
crontab -l  # 驗證排程已設定
```

---

### 模組 3｜Ansible Playbook 自動部署

> 使用 Ansible 標準化憑證部署流程，適合多台 Liberty Server 統一管理。

**時間**：45 分鐘

#### Step 3-1｜請 Bob 設計 Ansible Playbook 架構

在 Bob 中輸入：
```
我要用 Ansible 自動化 WAS Liberty 的 TLS 憑證置換，環境如下：
- 目標主機：localhost（單台，測試用）
- Liberty 路徑：/opt/ibm/wlp/usr/servers/defaultServer
- Keystore 路徑：/opt/certs/keystore.p12
- 憑證來源：[選 A: Vault PKI API] 或 [選 B: 本機 OpenSSL 產生]

請設計一個 Ansible Playbook 的目錄結構和各檔案用途，包含：
- inventory、playbook.yml、roles/liberty_cert_rotate/
- tasks、handlers、vars、templates 各自放什麼
```

#### Step 3-2｜請 Bob 產生完整的 Playbook

```
請幫我撰寫完整的 Ansible Playbook，實現以下 tasks：

1. 檢查目前 Liberty 上的憑證到期日（openssl s_client）
2. 若距到期 < 30 天：
   a. 申請/產生新憑證（依憑證來源選擇）
   b. 轉換為 PKCS12 格式
   c. 備份舊 keystore（加日期戳記）
   d. 複製新 keystore 到 /opt/certs/
   e. 觸發 handler 重啟 Liberty
3. 若距到期 >= 30 天：輸出 skip 訊息

Handler：
- restart_liberty：執行 server stop + server start，等待啟動完成

請提供每個檔案的完整內容。
```

#### Step 3-3｜建立 Ansible 環境並執行

```bash
# 建立目錄結構
mkdir -p ~/ansible-clm/roles/liberty_cert_rotate/{tasks,handlers,vars,templates}
cd ~/ansible-clm

# 將 Bob 產生的內容依序填入各檔案

# 測試 Inventory 連線
ansible -i inventory all -m ping

# Dry run（--check 模式）
ansible-playbook -i inventory playbook.yml --check

# 正式執行
ansible-playbook -i inventory playbook.yml -v

# 查看執行結果
echo | openssl s_client -connect localhost:9443 2>/dev/null \
  | openssl x509 -noout -subject -dates
```

#### Step 3-4｜設定 ansible-pull 排程（進階）

在 Bob 中輸入：
```
請說明如何用 crontab 排程定期執行 ansible-playbook，
讓憑證輪換完全自動化。
同時說明 ansible-pull 和 ansible-playbook 的差異，
以及哪種適合銀行的 CLM 場景。
```

---

## 🎨 Frontend Slides Skill 安裝（簡報製作用）

本 Workshop 的簡報製作任務需要使用 **Frontend Slides Skill**。
Skill 檔案已內含於本 repo（`skills/frontend-slides/`），請於開始前完成安裝：

```bash
# 建立 Bob skills 目錄（如尚未建立）
mkdir -p ~/.bob/skills

# 將 skill 複製到 Bob 的 skills 目錄
cp -r ../../skills/frontend-slides ~/.bob/skills/frontend-slides
```

安裝完成後，在 Bob 中即可輸入：
```
使用 frontend-slides skill 製作技術簡報，主題：Vault + Liberty CLM 實戰

要求：
- IBM 企業風格設計
- 著重「手動置換 → CLM 自動化」的對比效益
- 加入憑證生命週期流程圖
- 展示你選擇的模組組合（憑證來源 + 部署方式）
- 10 slides 以內
```

---

## ✅ 共用收尾步驟（所有人必做）

完成 Stage 1 + Stage 2 後，執行以下共用步驟。

### 建立 Bob Slash Command `/check-cert`

在 Bob 中輸入：
```
請幫我在專案中建立 .bob/slash-commands/check-cert.md，
這個 Slash Command 的功能：
1. 連線 localhost:9443 取得憑證資訊
2. 顯示 Subject、Issuer、到期日
3. 計算距到期還有幾天
4. 若 < 30 天顯示 ⚠️ 警告；若 < 7 天顯示 🔴 緊急
```

### 建立 AGENTS.md 記錄環境

完成 Workshop 後，請建立 `.bob/AGENTS.md` 記錄環境資訊：

```markdown
# MEGA Liberty CLM 環境特性

## 環境路徑
- Liberty 安裝路徑：/opt/ibm/wlp
- Server 名稱：defaultServer
- Keystore 路徑：/opt/certs/keystore.p12（PKCS12，密碼存於 /etc/liberty/keystore.pwd）
- 憑證工作目錄：/opt/certs/
- 執行日誌：/var/log/cert-rotate.log

## Vault 資訊（如使用模組 A）
- Vault 位址：http://127.0.0.1:8200（Prod 環境請改 HTTPS）
- PKI Mount：pki_int
- Role：liberty-server（TTL 30d，允許 *.bank.local）
- Auth Method：AppRole（Role ID 存於 /etc/vault-agent/role-id）

## 憑證規範
- 格式：PKCS12
- 只允許：TLSv1.2、TLSv1.3
- 輪換觸發條件：距到期 < 30 天

## 我的實作路徑
- 憑證來源：[模組 A / 模組 B]
- 部署方式：[模組 1 / 模組 2 / 模組 3]

## Slash Command
- /check-cert：快速檢查 Liberty 憑證狀態與到期天數
```

---

## 🆘 常見問題

### Q: Vault API 回傳 403 Permission Denied？
A: 確認 Policy 設定是否正確，把錯誤訊息和 Policy 內容貼給 Bob 分析。

### Q: Liberty 啟動後 HTTPS 連不上？
A: 把 `messages.log` 中的 `CWWKS` 或 `SSL` 錯誤訊息貼給 Bob，它會幫你解讀。

### Q: PKCS12 轉換出現 "Invalid keystore format"？
A: 通常是 JDK 版本問題。把錯誤訊息給 Bob，請它提供對應 JDK 版本的指令。

### Q: Ansible Playbook 執行失敗？
A: 先用 `--check` 模式確認邏輯，再把錯誤輸出貼給 Bob Debug。

### Q: Vault Agent 一直重啟或拿不到 Token？
A: 確認 AppRole 的 Role ID 和 Secret ID 格式正確。把 Agent log 貼給 Bob 分析。

---

## 📚 參考資源

- [HashiCorp Vault PKI Secrets Engine 文件](https://developer.hashicorp.com/vault/docs/secrets/pki)
- [IBM WebSphere Liberty SSL 配置](https://www.ibm.com/docs/en/was-liberty)
- [Vault Agent 設定參考](https://developer.hashicorp.com/vault/docs/agent-and-proxy/agent)
- [Ansible 模組文件](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/)
- [IBM Bob 官方文件](https://bob.ibm.com/docs)

---

**準備好了嗎？選擇你的模組路徑，打開 Bob，開始把憑證管理從手動變全自動！** 🔐🚀
