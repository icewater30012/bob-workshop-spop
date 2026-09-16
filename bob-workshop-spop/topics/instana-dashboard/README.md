<!-- Created: 2026-09-15 21:21:58 +0800 -->
# Instana Dashboard 客製化監控

> **用途**：IBM Bob Workshop — 兆豐銀行 MEGA 專場（OP 人員專屬題目）  
> **難度**：⭐⭐⭐ 中等  
> **時長**：2 小時  
> **角色**：OP（Operations）維運操作人員

---

## 📋 專案簡介

對銀行 OP 人員來說，監控平台的 Dashboard 往往是預設的、對自己業務不夠貼近的。每次要查看特定服務的健康狀態，都要在預設畫面裡翻來翻去，遇到異常還不一定能第一時間發現。

在本 Workshop 中，你將以 **IBM Bob** 作為 AI 輔助工具，學習如何呼叫 Instana REST API，為兆豐的監控環境建立一套客製化的 Dashboard：從選擇關鍵指標、設計 Widget，到建立 Alert Channel，讓監控真正為你所用。

---

## 🎯 Workshop 目標

完成本 Workshop 後，你將能夠：

- ✅ 使用 Bob 理解 Instana REST API 的結構與認證方式
- ✅ 使用 Bob 撰寫 Shell Script / Python，自動查詢 Instana 指標
- ✅ 使用 Bob 產生 Dashboard 設定的 JSON Payload，建立客製化 Widget
- ✅ 使用 Bob 設定 Custom Event Rule 與 Alert Channel（Email / Webhook）
- ✅ 使用 Bob 建立 Slash Command，一鍵查詢服務健康狀態
- ✅ 使用 Bob 建立 AGENTS.md，記錄 Instana 環境資訊供日後維護

---

## 🏗️ 環境說明

講師已預先準備好以下環境：

| 元件 | 說明 |
|------|------|
| **Instana 版本** | Instana SaaS Trial 或 Self-managed |
| **存取方式** | Web UI + REST API |
| **API Base URL** | 由講師提供（例：`https://mega-instana.instana.io`）|
| **API Token** | 由講師提供（具 Read + Write 權限）|
| **被監控服務** | 預先部署的 Spring Boot 示範應用（模擬兆豐業務服務）|

> **注意**：所有 API 操作都可以先在 Bob 中設計，再執行 curl 指令。

---

## 🔧 背景知識（Bob 幫你學）

不需要事先了解以下內容，Workshop 過程中你將請 Bob 解釋：

- Instana REST API 的認證方式（API Token）
- Dashboard 的 Widget 類型（Time Series、Top List、Big Number、等）
- Custom Metrics vs. Built-in Metrics 的差異
- Alert Channel 種類（Email、Webhook、Slack、PagerDuty 等）
- Instana 的 Application Perspective 概念

---

## 📋 Workshop 任務

### 👥 團隊分工建議（3+1 模式）

本 Workshop 採用 **3 人實作 + 1 人簡報** 的協作模式。

---

### **👤 Person A：探索 Instana API + 查詢現有指標（難度 ⭐⭐）**

**任務**：理解 Instana API 結構，查詢服務清單與關鍵指標

**時間**：35 分鐘

#### Step 1｜請 Bob 解釋 Instana REST API 架構

在 Bob 中輸入：
```
我是一位銀行 OP，需要學習使用 Instana REST API。
請解釋：
1. Instana API 的認證方式（API Token 如何放在 Header）
2. 主要的 API 端點類別（Infrastructure、Application、Events 等）
3. 查詢指標時 Rollup 和 TimeFrame 的意義
4. 提供一個查詢所有受監控 Services 的 curl 範例
```

#### Step 2｜實際查詢 Instana 環境

把講師提供的 API Token 和 Base URL 設定為變數，然後用 Bob 產生的指令查詢：

```bash
# 設定環境變數（將 XXX 換成講師提供的值）
export INSTANA_URL="https://mega-instana.instana.io"
export INSTANA_TOKEN="YOUR_API_TOKEN"

# 查詢所有受監控的 Application Services
curl -s -H "authorization: apiToken ${INSTANA_TOKEN}" \
  "${INSTANA_URL}/api/application-monitoring/services" | python3 -m json.tool
```

把輸出結果貼給 Bob：
```
這是我的 Instana 環境中的 Services 清單，請幫我：
1. 列出所有 Service 的名稱和 ID
2. 識別哪些是關鍵業務服務（依 errorRate 和 callCount 判斷）
3. 建議我應該監控哪些指標

[貼上 JSON 輸出]
```

#### Step 3｜請 Bob 幫你查詢特定服務的健康指標

```
我要查詢服務 "payment-service" 最近 1 小時的以下指標：
- 請求數（calls）
- 錯誤率（erroneousCalls）
- 平均回應時間（latency.mean）

請提供對應的 Instana API 查詢指令。
```

**Bob 使用重點**：
```
• 使用 Bob Ask Mode 理解 API 結構
• 把 JSON 輸出貼給 Bob 解讀
• 請 Bob 幫你格式化 curl 指令
```

---

### **👤 Person B：建立客製化 Dashboard Widget（難度 ⭐⭐⭐）**

**任務**：透過 Instana API 建立一個兆豐業務監控 Dashboard

**時間**：40 分鐘（可與 Person A 同步進行）

#### Step 1｜請 Bob 說明 Dashboard API 結構

在 Bob 中輸入：
```
我想用 Instana REST API 建立一個客製化 Dashboard。
請說明：
1. 建立 Dashboard 的 API 端點和所需的 JSON 結構
2. 有哪些 Widget 類型可以使用（Time Series、Big Number、Top List 等）
3. 如何在 Widget 中指定要顯示的 Metric
請提供一個包含 3 個 Widget 的 Dashboard JSON 範例。
```

#### Step 2｜設計兆豐監控 Dashboard

在 Bob 中輸入：
```
請幫我設計一個「兆豐核心業務監控」Dashboard 的 JSON Payload，包含以下 4 個 Widget：

Widget 1：Big Number — 目前每分鐘總請求數（calls/min）
Widget 2：Time Series — 過去 1 小時的錯誤率趨勢（erroneousCalls %）
Widget 3：Top List — 回應時間最慢的前 5 個 Endpoint
Widget 4：Time Series — Infrastructure CPU 使用率（payment-service 相關主機）

API Base URL: ${INSTANA_URL}
這個 Dashboard 要在 Instana SaaS 版本上建立。
```

#### Step 3｜執行 API 建立 Dashboard

```bash
# 將 Bob 產生的 JSON 存成檔案
cat > /tmp/mega-dashboard.json << 'EOF'
# [貼上 Bob 產生的 JSON]
EOF

# 呼叫 API 建立 Dashboard
curl -s -X POST \
  -H "authorization: apiToken ${INSTANA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @/tmp/mega-dashboard.json \
  "${INSTANA_URL}/api/custom-dashboards"
```

#### Step 4｜登入 Instana Web UI 確認 Dashboard

1. 開啟瀏覽器，登入 Instana Web UI
2. 前往 **Dashboards** → 確認「兆豐核心業務監控」已出現
3. 截圖保存（供 Person D 做簡報使用）

如果 Widget 顯示不正確，把錯誤截圖描述給 Bob：
```
我的 Dashboard 建立成功，但 Widget 顯示"No Data"，
請幫我 debug JSON Payload 中的 Metric 設定。
這是我的 JSON：[貼上 JSON]
```

**Bob 使用重點**：
```
• 使用 Bob 設計複雜的 JSON Payload
• 把 API 回傳錯誤給 Bob Debug
• 請 Bob 解讀 Instana API 文件中的 Widget 參數
```

---

### **👤 Person C：設定 Alert + Webhook 通知（難度 ⭐⭐⭐⭐）**

**任務**：建立自定義告警規則，並透過 Webhook 連接通知系統

**時間**：40 分鐘

#### Step 1｜請 Bob 說明 Instana Alert Channel API

在 Bob 中輸入：
```
我想用 Instana REST API 設定告警通知，需求如下：
1. 建立一個 Webhook Alert Channel（接收端：http://webhook.site 測試用）
2. 建立一個 Custom Event Rule：
   - 觸發條件：payment-service 錯誤率超過 5%（持續 5 分鐘）
   - 嚴重度：Critical
   - 發送到上面建立的 Webhook Channel

請提供完整的 API 呼叫流程和 JSON Payload。
```

#### Step 2｜建立 Webhook Alert Channel

```bash
# 先去 https://webhook.site 取得一個測試用 Webhook URL
# 將 Bob 產生的 JSON 存檔

cat > /tmp/alert-channel.json << 'EOF'
{
  "name": "MEGA-Webhook-Critical",
  "kind": "WEBHOOK",
  "webhookIntegration": {
    "url": "https://webhook.site/YOUR-UNIQUE-ID",
    "httpMethod": "POST",
    "headers": [
      {"name": "Content-Type", "value": "application/json"}
    ]
  }
}
EOF

curl -s -X POST \
  -H "authorization: apiToken ${INSTANA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @/tmp/alert-channel.json \
  "${INSTANA_URL}/api/events/settings/alertingChannels"
```

#### Step 3｜建立 Custom Event Rule（告警規則）

在 Bob 中輸入：
```
我已建立 Alert Channel，其 ID 為 "CHANNEL_ID"（從上一步 API 回傳取得）。
請幫我建立一個 Custom Event Rule 的 JSON Payload：

規則名稱：MEGA-Payment-High-ErrorRate
觸發條件：payment-service 的錯誤率（erroneousCallRate）> 5%
持續時間：5 分鐘以上才觸發
嚴重度：CRITICAL
通知管道：上面建立的 Webhook Channel

請同時說明 Instana Event Rule 的 threshold 和 window 參數。
```

#### Step 4｜模擬告警觸發

```bash
# 查詢目前 Alert Channels 是否成功建立
curl -s -H "authorization: apiToken ${INSTANA_TOKEN}" \
  "${INSTANA_URL}/api/events/settings/alertingChannels" | python3 -m json.tool

# 查詢 Custom Event Rules
curl -s -H "authorization: apiToken ${INSTANA_TOKEN}" \
  "${INSTANA_URL}/api/events/settings/event-specifications/custom" | python3 -m json.tool
```

開啟 webhook.site，等待 Instana 觸發告警（若環境有真實流量）。
把收到的 Webhook Payload 貼給 Bob：
```
這是 Instana 發送的 Webhook 告警內容，
請幫我解讀每個欄位的意義，
並說明如何用這個 Payload 自動觸發 On-call 通知或 Ticket 建立。

[貼上 Webhook Payload JSON]
```

#### Step 5（進階挑戰）｜用 Bob 建立 Slash Command `/health-check`

```markdown
# .bob/slash-commands/health-check.md

# /health-check

功能：快速查詢 Instana 中所有服務的健康狀態

操作步驟：
1. 呼叫 Instana API 查詢所有 Services
2. 顯示每個服務的：名稱、錯誤率、平均回應時間
3. 若錯誤率 > 1%，標注 ⚠️ 警告
4. 若錯誤率 > 5%，標注 🔴 嚴重

環境變數：
- INSTANA_URL：Instana API Base URL
- INSTANA_TOKEN：API Token
```

**Bob 使用重點**：
```
• 使用 Bob 設計複雜的告警規則 JSON
• 把 API 錯誤 debug 給 Bob 分析
• 使用 Bob 建立 Slash Command 提升日後維運效率
• 使用 Bob 解讀 Webhook Payload 結構
```

---

### **📊 Person D：技術簡報製作（1 人）**

**任務**：使用 Bob + Frontend-slides SKILL 製作成果簡報

**簡報大綱（8-10 slides）**：

1. **封面** — Instana Dashboard 客製化監控實戰
2. **問題背景** — 銀行 OP 的監控痛點：預設 Dashboard 不夠用
3. **解決方案** — Instana API + Bob = 分鐘級客製化
4. **Person A 成果** — 服務清單查詢與關鍵指標識別
5. **Person B 成果** — 兆豐核心業務監控 Dashboard（截圖展示）
6. **Person C 成果** — Alert Channel + Custom Event Rule 設定
7. **Bob 使用技巧** — Slash Command `/health-check`、AGENTS.md 展示
8. **監控效益** — 從被動反應到主動預警
9. **Demo 展示** — Dashboard 截圖 + Webhook 告警範例
10. **總結** — Bob 在 OP 工作中的應用場景

**Bob 使用方式**：
```
使用 Frontend-slides SKILL 製作技術簡報，主題：Instana Dashboard 客製化監控

要求：
- IBM 企業風格設計
- 包含 Dashboard 截圖位置（預留截圖框）
- 著重「手動查詢 → API 自動化」的對比
- 加入 Webhook 告警流程圖
- 10 slides 以內
```

---

## 🎯 依賴關係

```
Person A（探索 API + 查詢服務指標）
    ↓
Person B（建立 Dashboard Widget）← 使用 A 查到的 Service ID 和 Metric
    |
Person C（Alert Rules + Webhook） ← 獨立開始，但使用 A 的 Service 名稱
    ↓
Person D（簡報）← 依賴 B/C 的截圖和結果
```

---

## 💡 關鍵同步點

| 時間 | 里程碑 |
|------|--------|
| 第 20 分鐘 | Person A 完成 API 探索，分享 Service ID 清單給 B/C |
| 第 60 分鐘 | Person B Dashboard 截圖完成，Person C Webhook 收到告警 |
| 第 80 分鐘 | 開發組提供截圖給 Person D |
| 第 100 分鐘 | 全員 Review 簡報 |

---

## 🏦 AGENTS.md 建議內容

完成 Workshop 後，請建立 `.bob/AGENTS.md` 記錄環境資訊：

```markdown
# MEGA Instana 環境特性

## API 連線資訊
- Base URL：${INSTANA_URL}（存放於環境變數，不寫死）
- 認證方式：Header「authorization: apiToken <TOKEN>」
- Token 存放：/etc/instana/api.token（不寫入程式碼）

## 關鍵 Service 清單
- payment-service（ID：xxxxxxxx）— 核心支付服務
- account-service（ID：xxxxxxxx）— 帳戶查詢服務
- auth-service（ID：xxxxxxxx）— 認證服務

## 告警閾值規範
- 錯誤率 > 1%：Warning（5 分鐘持續）
- 錯誤率 > 5%：Critical（即時通知）
- 平均回應時間 > 2000ms：Warning

## Dashboard ID
- 兆豐核心業務監控：xxxxxxxx（URL：${INSTANA_URL}/dashboard/xxxxxxxx）

## Slash Command
- /health-check：快速查詢所有服務健康狀態
```

---

## 🆘 常見問題

### Q: API 回傳 401 Unauthorized？
A: 確認 Authorization Header 格式為 `apiToken YOUR_TOKEN`（不是 Bearer）。把 curl 指令貼給 Bob 確認格式。

### Q: Dashboard Widget 顯示 "No Data"？
A: 通常是 Metric 名稱或 TimeFrame 設定錯誤。把 Widget JSON 貼給 Bob，請它對照 Instana 文件找出問題。

### Q: Webhook 沒有收到告警？
A: 確認 Alert Rule 的 Threshold 和觸發條件。測試時可以故意降低閾值（如 errorRate > 0.1%）來觸發告警。

### Q: 不知道 Metric 的正確 Key 名稱？
A: 先用 `GET /api/application-monitoring/catalog/metrics` 查詢所有可用 Metric，貼給 Bob 請它幫你找出對應的欄位名稱。

---

## 📚 參考資源

- [Instana REST API 文件](https://www.ibm.com/docs/en/instana-observability/current?topic=apis-rest)
- [Instana Dashboard API](https://instana.github.io/openapi/#tag/Custom-Dashboards)
- [IBM Bob 官方文件](https://bob.ibm.com/docs)
- [webhook.site — 免費 Webhook 測試工具](https://webhook.site)

---

**準備好開始挑戰了嗎？打開 Bob，讓我們把 OP 的監控工作從「手動查圖」升級為「智慧告警」！** 📊🚀
