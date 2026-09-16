<!-- Created: 2026-09-15 21:21:58 +0800 -->
# WAS Liberty 自動憑證置換

> **用途**：IBM Bob Workshop — 兆豐銀行 MEGA 專場（SP 人員專屬題目）  
> **難度**：⭐⭐⭐ 中等  
> **時長**：2 小時  
> **角色**：SP（System Platform）系統平台人員

---

## 📋 專案簡介

憑證管理是銀行資訊平台最高頻的維運痛點之一。每次憑證到期前，需要手動完成簽署、格式轉換、更新設定、重啟服務等一連串步驟，稍有差錯就會造成服務中斷。

在本 Workshop 中，你將以 **IBM Bob** 作為 AI 輔助工具，從零開始學習 WAS Liberty TLS 憑證置換的完整流程，最終把所有手動步驟整合成一支全自動化的排程腳本，讓憑證置換從「需要夜間維護視窗」變成「讓排程處理就好」。

---

## 🎯 Workshop 目標

完成本 Workshop 後，你將能夠：

- ✅ 使用 Bob 理解 TLS 憑證的簽署與格式轉換流程
- ✅ 使用 Bob 產生並修改 Shell Script，完成憑證置換自動化
- ✅ 使用 Bob 撰寫正確的 WAS Liberty `server.xml` 憑證設定
- ✅ 使用 Bob 建立 AGENTS.md 記錄環境特性，避免重複踩坑
- ✅ 使用 Bob 產生 Slash Command，一鍵驗證憑證狀態
- ✅ 使用 Bob 撰寫 crontab 排程，實現全自動憑證輪換

---

## 🏗️ 環境說明

講師已預先準備好以下環境，你只需使用 SSH 連線：

| 元件 | 說明 |
|------|------|
| **WAS Liberty 版本** | IBM WebSphere Liberty 23.0.x |
| **JDK** | IBM Semeru 17 |
| **作業系統** | RHEL 8（或 Ubuntu 22.04）|
| **連線方式** | SSH（講師提供帳號密碼）|
| **Liberty 安裝路徑** | `/opt/ibm/wlp` |
| **應用程式路徑** | `/opt/ibm/wlp/usr/servers/defaultServer` |

> **注意**：環境中已預裝 `openssl`、`keytool`、`curl`。

---

## 🔧 背景知識（Bob 幫你學）

不需要事先了解以下內容，Workshop 過程中你將請 Bob 解釋：

- PEM / PKCS12 / JKS 憑證格式的差異
- CA 自簽憑證 vs. 中繼憑證簽署
- WAS Liberty `server.xml` 中 `<ssl>` 與 `<keyStore>` 設定
- `keytool` 與 `openssl` 常用指令

---

## 📋 Workshop 任務

### 👥 團隊分工建議（3+1 模式）

本 Workshop 採用 **3 人實作 + 1 人簡報** 的協作模式。

---

### **👤 Person A：憑證產生與簽署（難度 ⭐⭐）**

**任務**：使用 OpenSSL 建立 CA 和 Server 憑證，理解憑證鏈

**時間**：35 分鐘

#### Step 1｜請 Bob 解釋憑證格式差異

在 Bob 中輸入：
```
我需要在 WAS Liberty 上替換 TLS 憑證。
請解釋 PEM、PKCS12（.p12）、JKS 三種格式的差異，
以及 WAS Liberty 使用哪種格式？
```

#### Step 2｜請 Bob 產生建立 Self-signed CA 的腳本

在 Bob 中輸入：
```
請幫我寫一個 Shell Script，完成以下步驟：
1. 建立 Root CA（私鑰 + 自簽憑證，有效期 3650 天）
2. 建立 Server 私鑰
3. 建立 Server CSR（Common Name: mega-liberty.bank.local）
4. 用 Root CA 簽署 Server 憑證（有效期 365 天）
5. 驗證憑證有效性並顯示到期日

輸出檔案放在 /opt/certs/ 目錄下。
```

#### Step 3｜執行腳本並驗證

```bash
# 建立目錄
sudo mkdir -p /opt/certs && cd /opt/certs

# 執行 Bob 產生的腳本（存成 create-certs.sh）
chmod +x create-certs.sh && ./create-certs.sh

# 驗證憑證資訊
openssl x509 -in /opt/certs/server.crt -text -noout | grep -A2 "Validity"
```

#### Step 4｜請 Bob 解釋輸出結果

把 `openssl` 的輸出貼給 Bob：
```
這是我的憑證資訊輸出，請幫我解釋每個欄位的意義，
並告訴我這張憑證是否符合銀行 TLS 最佳實踐？
[貼上 openssl 輸出]
```

**Bob 使用重點**：
```
• 使用 Bob Ask Mode 理解憑證格式與 TLS 概念
• 使用 Bob Code Mode 產生 Shell Script
• 把錯誤訊息貼給 Bob 進行 Debug
```

---

### **👤 Person B：格式轉換與 server.xml 設定（難度 ⭐⭐⭐）**

**任務**：將 PEM 憑證轉為 PKCS12，並更新 Liberty server.xml

**時間**：40 分鐘（依賴 Person A 的產出）

#### Step 1｜請 Bob 說明格式轉換指令

在 Bob 中輸入：
```
Person A 已產生 PEM 格式的憑證（server.crt + server.key）。
我需要：
1. 把 PEM 憑證轉成 PKCS12（.p12）格式
2. 再轉成 JKS keystore（供 WAS Liberty 使用）
請提供完整的 keytool 和 openssl 轉換指令，
並說明每個參數的意義。
```

#### Step 2｜執行格式轉換

```bash
cd /opt/certs

# PEM → PKCS12
openssl pkcs12 -export \
  -in server.crt -inkey server.key \
  -CAfile ca.crt -chain \
  -out keystore.p12 \
  -name "mega-liberty" \
  -passout pass:changeit

# PKCS12 → JKS（選擇性，依 Liberty 版本）
keytool -importkeystore \
  -srckeystore keystore.p12 \
  -srcstoretype PKCS12 \
  -destkeystore keystore.jks \
  -deststoretype JKS \
  -srcstorepass changeit \
  -deststorepass changeit
```

#### Step 3｜請 Bob 撰寫 server.xml SSL 設定

在 Bob 中輸入：
```
我有一個 WAS Liberty 23.0 server，需要設定 TLS。
Keystore 路徑：/opt/certs/keystore.p12
格式：PKCS12
密碼：changeit
別名：mega-liberty

請幫我撰寫 server.xml 中的 <featureManager>、<keyStore>、<ssl> 和 <httpEndpoint> 設定，
要求只允許 TLSv1.2 和 TLSv1.3，並停用弱加密套件。
```

#### Step 4｜套用設定並重啟 Liberty

```bash
# 備份原始 server.xml
cp /opt/ibm/wlp/usr/servers/defaultServer/server.xml \
   /opt/ibm/wlp/usr/servers/defaultServer/server.xml.bak.$(date +%Y%m%d)

# 更新 server.xml（將 Bob 產生的內容填入）
# 使用 vim 或 Bob 直接編輯

# 重啟 Liberty
/opt/ibm/wlp/bin/server stop defaultServer
/opt/ibm/wlp/bin/server start defaultServer

# 查看啟動日誌確認沒有憑證錯誤
tail -f /opt/ibm/wlp/usr/servers/defaultServer/logs/messages.log | grep -E "SSL|TLS|cert|CWWKS"
```

#### Step 5｜驗證 HTTPS 是否正常

```bash
# 使用 curl 驗證（忽略 CA 驗證，因為是自簽）
curl -vk https://localhost:9443/

# 或加上 CA 憑證驗證
curl -v --cacert /opt/certs/ca.crt https://mega-liberty.bank.local:9443/
```

把 `curl -v` 的輸出貼給 Bob，請它確認憑證資訊是否正確。

**Bob 使用重點**：
```
• 使用 Bob 產生 server.xml 設定片段
• 把啟動錯誤日誌貼給 Bob Debug
• 使用 Bob 解讀 curl -v 的 TLS 握手輸出
```

---

### **👤 Person C：自動化腳本 + 排程（難度 ⭐⭐⭐⭐）**

**任務**：整合 A/B 的成果，撰寫完整的一鍵置換腳本並設定 crontab

**時間**：40 分鐘（依賴 A/B 的成果）

#### Step 1｜請 Bob 整合成完整的自動化腳本

在 Bob 中輸入：
```
我們已經完成以下步驟的手動操作：
1. OpenSSL 建立 CA + Server 憑證（PEM 格式）
2. PEM 轉 PKCS12
3. 更新 WAS Liberty server.xml
4. 重啟 Liberty 服務

請幫我把以上步驟整合成一支名為 cert-rotate.sh 的 Shell Script，
需求：
- 自動偵測憑證到期日，距到期 30 天前才執行置換
- 置換前自動備份舊的 keystore 和 server.xml（含日期戳記）
- 置換失敗時自動 rollback 到備份版本
- 執行完成後，用 openssl s_client 驗證新憑證已生效
- 所有操作都寫入 /var/log/cert-rotate.log
- 腳本執行成功/失敗都用 echo 輸出明確的狀態訊息

Liberty 相關路徑：
- 安裝路徑：/opt/ibm/wlp
- Server：defaultServer
- Keystore：/opt/certs/keystore.p12
```

#### Step 2｜測試腳本

```bash
chmod +x /opt/scripts/cert-rotate.sh

# 先用 dry-run 模式測試（在腳本中加入 DRY_RUN=true 參數）
DRY_RUN=true /opt/scripts/cert-rotate.sh

# 正式執行
/opt/scripts/cert-rotate.sh

# 查看執行日誌
tail -50 /var/log/cert-rotate.log
```

#### Step 3｜請 Bob 撰寫 crontab 排程

在 Bob 中輸入：
```
我想為 cert-rotate.sh 設定 crontab 排程，需求：
1. 每天凌晨 2:00 執行（低峰時段）
2. 執行結果 append 到 /var/log/cert-rotate.log
3. 如果是 root 用戶執行，說明正確的 crontab 寫法
請同時說明如何查看 crontab 是否已生效，以及如何手動觸發測試。
```

#### Step 4｜設定並驗證排程

```bash
# 編輯 crontab
crontab -e

# 驗證已設定
crontab -l

# 模擬手動觸發（確認 log 有輸出）
/opt/scripts/cert-rotate.sh
tail -20 /var/log/cert-rotate.log
```

#### Step 5（進階挑戰）｜建立 Bob Slash Command

請 Bob 幫你建立一個 Slash Command `/check-cert`：

```markdown
# .bob/slash-commands/check-cert.md

# /check-cert

功能：快速檢查 WAS Liberty 憑證狀態

操作步驟：
1. 執行 `openssl s_client` 連接 localhost:9443
2. 顯示憑證到期日
3. 計算距到期還有幾天
4. 若 < 30 天，顯示警告訊息

執行指令：
```bash
echo | openssl s_client -connect localhost:9443 2>/dev/null \
  | openssl x509 -noout -dates
```
```

**Bob 使用重點**：
```
• 使用 Bob 整合複雜的 Shell Script 邏輯
• 把腳本錯誤貼給 Bob Debug
• 使用 Bob 建立 Slash Command 提升日後維護效率
• 使用 Bob 建立 AGENTS.md 記錄環境參數
```

---

### **📊 Person D：技術簡報製作（1 人）**

**任務**：使用 Bob + Frontend-slides SKILL 製作成果簡報

**簡報大綱（8-10 slides）**：

1. **封面** — WAS Liberty 自動憑證置換實戰
2. **問題背景** — 銀行憑證管理的痛點
3. **技術架構** — 憑證流程全景圖（CA → CSR → 簽署 → 轉換 → 設定 → 重啟）
4. **Person A 成果** — 憑證產生與 CA 建立
5. **Person B 成果** — 格式轉換與 server.xml 設定
6. **Person C 成果** — cert-rotate.sh 腳本邏輯與 crontab 排程
7. **Bob 使用技巧** — Slash Command、AGENTS.md 實作展示
8. **Demo 展示** — 憑證置換前後的 curl -v 輸出對比
9. **自動化效益** — 從 4 小時維護視窗到 0 人工介入
10. **總結** — 學習心得與 Bob 使用體驗

**Bob 使用方式**：
```
使用 Frontend-slides SKILL 製作技術簡報，主題：WAS Liberty 自動憑證置換

要求：
- IBM 企業風格設計
- 包含憑證流程架構圖（用 ASCII 或 SVG 呈現）
- 加入 Shell Script 程式碼片段
- 著重「手動 → 自動化」的對比效益
- 10 slides 以內
```

---

## 🎯 依賴關係

```
Person A（憑證產生 + PEM 格式）
    ↓
Person B（格式轉換 + server.xml）← 依賴 Person A 的憑證檔案
    ↓
Person C（自動化腳本 + crontab）← 依賴 A/B 的完整流程
    ↓
Person D（簡報）← 依賴全員成果截圖
```

---

## 💡 關鍵同步點

| 時間 | 里程碑 |
|------|--------|
| 第 30 分鐘 | Person A 完成憑證產生，傳遞 `/opt/certs/` 給 B |
| 第 60 分鐘 | Person B 完成 server.xml 更新，Liberty 已可 HTTPS 存取 |
| 第 80 分鐘 | 開發組提供截圖給 Person D |
| 第 100 分鐘 | 全員 Review 簡報內容 |

---

## 🏦 AGENTS.md 建議內容

完成 Workshop 後，請 Person C 協助建立 `.bob/AGENTS.md`，記錄本環境的特殊設定：

```markdown
# MEGA Liberty 環境特性

## 路徑資訊
- Liberty 安裝路徑：/opt/ibm/wlp
- Server 名稱：defaultServer
- Server 設定路徑：/opt/ibm/wlp/usr/servers/defaultServer
- Keystore 路徑：/opt/certs/keystore.p12
- 憑證輪換腳本：/opt/scripts/cert-rotate.sh
- 執行日誌：/var/log/cert-rotate.log

## 重要限制
- Liberty 使用 PKCS12 格式（非 JKS）
- 只允許 TLSv1.2、TLSv1.3
- Keystore 密碼：存放於 /etc/liberty/keystore.pwd（非寫死在 server.xml）

## 憑證置換 SOP
1. 執行 /opt/scripts/cert-rotate.sh
2. 等待 Liberty 自動 reload（約 30 秒）
3. 使用 /check-cert 確認新憑證生效
```

---

## 🆘 常見問題

### Q: Liberty 啟動後 HTTPS 連不上？
A: 把 `messages.log` 中的 `CWWKS` 或 `SSL` 錯誤訊息貼給 Bob，它會幫你解讀。

### Q: keytool 轉換出現 "Invalid keystore format"？
A: 通常是 JDK 版本問題。把錯誤訊息給 Bob，請它提供對應 JDK 版本的指令。

### Q: crontab 排程沒有執行？
A: 確認腳本路徑是絕對路徑，並且 cron 用戶有執行權限。請 Bob 幫你 debug crontab。

### Q: openssl 與 keytool 指令產生的密碼格式不一致？
A: 把兩個工具的輸出貼給 Bob，請它分析不一致的原因。

---

## 📚 參考資源

- [IBM WebSphere Liberty — SSL 配置](https://www.ibm.com/docs/en/was-liberty)
- [OpenSSL 指令參考](https://www.openssl.org/docs/manpages.html)
- [IBM Bob 官方文件](https://bob.ibm.com/docs)

---

**準備好開始挑戰了嗎？打開 Bob，讓我們把憑證置換從「夜間維護視窗」變成「排程自動處理」！** 🔐🚀
