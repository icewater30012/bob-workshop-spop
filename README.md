<!-- Created: 2026-09-15 21:21:58 +0800 -->
<!-- Updated: 2026-09-29 16:05:15 +0800 -->
# Bob Workshop — 兆豐銀行 (MEGA) 專場

> **活動類型**：企業定制 Workshop
> **目標對象**：AP（應用程式開發）、SP（系統平台）/ OP（維運操作）人員
> **總時長**：依題目難度各 2 小時

---

## 🎯 Workshop 目標

本專場 Workshop 針對兆豐銀行不同職能角色設計，讓各角色透過符合日常工作場景的實作題目，體驗 **IBM Bob** 在真實企業環境中的 AI 輔助能力。

| 角色 | 英文縮寫 | 主要工作 | 本次題目方向 |
|------|---------|---------|------------|
| 應用程式開發人員 | AP | 業務功能開發、API 設計 | 信用卡/交通卡交易系統（沿用 bob-workshop 原題） |
| 系統平台 / 維運人員 | SP / OP | 中介軟體維護、平台建置、維運自動化 | Vault + Liberty 憑證生命週期管理（CLM）|

---

## 📁 專案結構

```
bob-workshop-spop/
├── README.md                        # 本文件（Workshop 總覽）
├── skills/
│   └── frontend-slides/             # 🎨 Frontend Slides Skill（需手動安裝）
│       ├── SKILL.md
│       ├── STYLE_PRESETS.md
│       ├── viewport-base.css
│       ├── html-template.md
│       ├── animation-patterns.md
│       └── scripts/
└── topics/
    └── vault-liberty-clm/           # 🔐 SP/OP 題目：Vault + Liberty CLM
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

## 🔐 SP / OP 人員題目（統一）

**題目：Vault + Liberty 憑證生命週期管理（CLM）**
**難度**：⭐⭐⭐ 中等 ～ ⭐⭐⭐⭐ 進階（依模組組合而定）
**時長**：2 小時

透過 Bob 學習如何建立完整的 TLS 憑證生命週期管理機制。題目採**模組化設計**，學員自由選擇「憑證來源」與「部署方式」進行組合，打造最符合自身環境的 CLM 解決方案。

| 憑證來源模組 | 部署模組 |
|------------|---------|
| 模組 A：Vault PKI Secrets Engine | 模組 1：Vault Agent（自動 sidecar）|
| 模組 B：OpenSSL 自簽憑證 | 模組 2：Shell Script + crontab |
| | 模組 3：Ansible Playbook |

→ [詳細說明](topics/vault-liberty-clm/README.md)

---

## 🚀 環境準備

### AP 人員
- Java 17+、Maven 3.6+、IBM Bob IDE

### SP / OP 人員
- IBM Bob IDE
- WAS Liberty + Vault 試用環境（由講師提供 VM 連線資訊）
- Bob Trial License
- Frontend Slides Skill（見下方安裝說明）

---

## 🎨 Frontend Slides Skill 安裝

本 repo 已內含 Frontend Slides Skill 的完整檔案（位於 `skills/frontend-slides/`）。
請於 Workshop 開始前完成以下安裝步驟：

```bash
# 1. 建立 Bob skills 目錄（如尚未建立）
mkdir -p ~/.bob/skills

# 2. 將 skill 複製到 Bob 的 skills 目錄
cp -r skills/frontend-slides ~/.bob/skills/frontend-slides
```

安裝完成後，在 Bob 中輸入以下指令即可啟用：
```
使用 frontend-slides skill 製作技術簡報
```

> **注意**：`scripts/deploy.sh`（部署到 Vercel）和 `scripts/export-pdf.sh`（匯出 PDF）為選用功能，Workshop 中不強制使用。

---

## 👤 聯絡資訊

**技術支援窗口**：

- 姓名: Raphael Li
  Email: Raphael.Li@ibm.com

---

**文件版本**: 1.0
**最後更新**: 2026-09-15 21:28:32 +0800
