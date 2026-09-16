<!-- Created: 2026-09-15 21:21:58 +0800 -->
# Bob Workshop — 兆豐銀行 (MEGA) 專場

> **活動類型**：企業定制 Workshop  
> **目標對象**：AP（應用程式開發）、SP（系統平台）、OP（維運操作）人員  
> **總時長**：依題目難度各 2 小時

---

## 🎯 Workshop 目標

本專場 Workshop 針對兆豐銀行不同職能角色設計，讓各角色透過符合日常工作場景的實作題目，體驗 **IBM Bob** 在真實企業環境中的 AI 輔助能力。

| 角色 | 英文縮寫 | 主要工作 | 本次題目方向 |
|------|---------|---------|------------|
| 應用程式開發人員 | AP | 業務功能開發、API 設計 | 信用卡/交通卡交易系統（沿用 bob-workshop 原題） |
| 系統平台人員 | SP | 中介軟體維護、平台建置 | WAS Liberty 自動憑證置換 |
| 維運操作人員 | OP | 監控、告警、維運自動化 | Instana Dashboard 客製化 |

---

## 📁 專案結構

```
bob-workshop-mega/
├── README.md                        # 本文件（Workshop 總覽）
└── topics/
    ├── liberty-cert-rotation/       # 🔐 SP 題目：WAS Liberty 自動憑證置換
    │   └── README.md
    └── instana-dashboard/           # 📊 OP 題目：Instana Dashboard 客製化
        └── README.md
```

---

## 🏦 AP 人員題目（沿用）

AP 人員使用原 bob-workshop 中的題目，請參考：

- **💳 荷包守護神：信用卡爭Bob戰**（中等，2 小時）  
  → [bob-workshop/topics/transaction-monitor](../bob-workshop/topics/transaction-monitor/README.md)

- **🗺️ 終結交通Bob爆王：交通卡使用分析**（進階，2 小時）  
  → [bob-workshop/topics/journey-analysis](../bob-workshop/topics/journey-analysis/)

---

## 🔐 SP 人員題目

**題目：WAS Liberty 自動憑證置換**  
**難度**：⭐⭐⭐ 中等  
**時長**：2 小時

透過 Bob 學習如何在 WAS Liberty 環境中進行 TLS 憑證的完整生命週期管理，從手動流程走向全自動化排程。

→ [詳細說明](topics/liberty-cert-rotation/README.md)

---

## 📊 OP 人員題目

**題目：Instana Dashboard 客製化監控**  
**難度**：⭐⭐⭐ 中等  
**時長**：2 小時

透過 Bob 學習如何利用 Instana API 客製化監控 Dashboard，結合 Custom Metrics 與 Alert Channel 建立符合銀行業務需求的觀測平台。

→ [詳細說明](topics/instana-dashboard/README.md)

---

## 🚀 環境準備

### AP 人員
- Java 17+、Maven 3.6+、IBM Bob IDE

### SP 人員
- IBM Bob IDE
- WAS Liberty 試用環境（由講師提供 VM 連線資訊）
- Bob Trial License

### OP 人員
- IBM Bob IDE
- Instana Trial 帳號 或講師提供的共用 Instana 環境
- API Token（由講師提供）

---

## 👤 聯絡資訊

**技術支援窗口**：

- 姓名: Raphael Li
  Email: Raphael.Li@ibm.com

---

**文件版本**: 1.0
**最後更新**: 2026-09-15 21:28:32 +0800
