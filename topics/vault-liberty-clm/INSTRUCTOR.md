# 講師課前準備與控時

[← 組合總覽](README.md)

## 課程邊界

只涵蓋 SP／OP。每組約五人、四選一；共同操作與驗收都包含在 60 分鐘內。這是課程設計時間，尚需在實際 VM 與學員背景下試跑確認。

每組可分為操作／Bob 提示 2 人、憑證與設定 1 人、驗證與故障排查 1 人、紀錄與計時 1 人。避免多人同時修改 live keystore。

## 環境與權限

- 沿用一台共用 Vault 與八台各組 Liberty VM 的規劃。OpenSSL 路線不依賴 Vault。
- 主機規格：Vault：RHEL 9.6／4 vCPU／16 GB RAM／100 GB 磁碟；每台 Liberty：RHEL 9.6／2 vCPU／8 GB RAM／100 GB 磁碟。SSH 別名為 `vault` 與 `liberty1`～`liberty8`；IP、user、key 已匯入學員 Bob 的 SSH config。
- 記錄實際 RHEL、JDK、Liberty、Vault、Agent、Ansible 與 OpenSSL 版本，課前確認相容性；不沿用舊教材未驗證的固定版本。
- Liberty HTTPS 預先啟動，提供可回應成功狀態的測試頁、基準憑證、備份與環境重置程序。
- 預裝所需 CLI；權限與服務控制以各組執行帳號試跑。不要讓學員花時間處理安裝、sudo、systemd 與目錄權限。
- `~/clm-workshop/` 由學員在 Liberty VM 自行建立；教材不預先提供 env.sh 或程式骨架。課前備妥並確認實際 CA_FILE、TLS_HOST（IP）、TLS_PORT、SERVER_NAME、Liberty 路徑、live keystore、服務控制命令、密碼檔位置，學員依步驟向 Bob 確認後使用。
- Vault 事先建立 Root／Intermediate CA、每組 PKI role 與最小權限認證。每組路徑隔離，不發 Root Token，不讓學員改共用 CA、mount、policy 或 auth method。
- Vault 使用實際內網位址與受信任 TLS 連線；將 CA 信任設定提供給 CLI 與 Agent。localhost 只用於該組 Liberty。
- Part 1 預建 AppRole、ID 檔案與可持續執行的 Agent 設定骨架，確認 Secret ID 的消耗／移除行為與重新啟動方式。
- Part 1 另建專用短 TTL role（建議 3 分鐘），實測兩個自動輪換週期；確認 CA 效期、允許 TTL、Agent 版本與 pkiCert 行為。結束後恢復一般設定。
- Part 2 提供每組獨立且涵蓋課程時長的受限 Token；交接時要求指出到期後處理方式。
- OpenSSL 路線由學員自行建立測試 CA，效期與輪換門檻自行決定；後續輪換沿用 CA，私鑰僅留在該組 VM。
- OpenSSL 路線不固定 leaf 效期；輪換門檻須小於憑證效期。確認自訂 CA、CN 及 SAN 適用 curl 與 s_client 驗證。
- 課前以同映像、同權限從頭執行各路線。此 repo 目前提供的是教材與提示，並未附上經 VM 實測的程式骨架或參考完成檔；若需於超時時救援，授課前須自行備妥。

## 控時與救援

| Part | 現況 | 設定／簽發 | 自動化 | 驗證 | 故障 | 交接 | 合計 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1：Vault Agent | 5 | 12 | 15 | 13 | 10 | 5 | 60 |
| 2：Vault Shell | 5 | 10 | 17 | 13 | 10 | 5 | 60 |
| 3：OpenSSL Ansible | 5 | 10 | 17 | 13 | 10 | 5 | 60 |
| 4：OpenSSL Shell | 5 | 10 | 17 | 13 | 10 | 5 | 60 |

- 入門線也要實際簽發、部署、確認 skip、加入排程及處理一次故障，避免只複製一條指令就結束。
- 任一階段超時五分鐘，交付該階段參考完成檔，保留驗證與故障練習；不得略過線上憑證驗收。
- 故障使用測試設定或複本，不破壞共用 CA、正式設定或刻意撤銷共用 Token。
- 簡報、Skill、Slash Command、完整 CA 階層、多台主機及 systemd 建置均為課後延伸。

## 預演驗收

- 每條路線以新學員操作速度實跑一次，記錄總時間與卡點；目標核心操作約 40 分鐘，其餘用於故障及交接。
- 成功路徑：線上序號改變、憑證鏈／SAN 驗證通過，HTTP 測試頁成功。
- 重跑路徑：Shell／Ansible 不到期時 skip；Agent 自行觸發下一次簽發及部署。
- 失敗路徑：申請／轉檔失敗不更動 live keystore；部署後驗證失敗可恢復舊檔及 HTTPS。
- 確認日誌與交付檔不包含秘密，結束時清理短 TTL Agent 與課堂測試排程。

## 官方參考

- [Vault Agent template／pkiCert](https://developer.hashicorp.com/vault/docs/agent-and-proxy/agent/template)
- [Vault PKI](https://developer.hashicorp.com/vault/docs/secrets/pki)
- [Liberty 文件](https://www.ibm.com/docs/en/was-liberty)
- [Ansible block／rescue](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_blocks.html)
