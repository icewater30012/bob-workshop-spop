# Part 1｜Vault PKI ＋ Vault Agent

[← 回組合總覽](../README.md) · [開啟分頁教材](../index.html#part-1)

**難度：進階｜總時間：60 分鐘｜適合：想理解 Vault 持續換證與事件觸發的 SP／OP**

## 主機部署架構

```mermaid
flowchart LR
  subgraph STUDENT["學員電腦"]
    direction TB
    B["IBM Bob IDE"]
    T["SSH 終端／HTTPS 測試"]
    U["瀏覽器／Vault UI"]
  end
  subgraph LIBERTY["Liberty VM：各組獨立"]
    direction TB
  A["Vault Agent"]
  H["部署 hook"]
  K["PKCS12 keystore"]
  L["Liberty HTTPS :9443"]
  A -->|本機觸發| H
  H -->|本機寫入| K
  L ---|讀取| K
  end
  T -->|SSH：操作與傳送檔案| A
  T -->|HTTPS :9443：驗證| L
  subgraph VAULT["Vault Server VM：講師管理／各組共用"]
    direction TB
    V["Vault Server :8200"]
    P["PKI Secrets Engine／每組 role"]
    W["Vault Web UI"]
    V --- P
    V --- W
  end
  A <-->|Vault API：AppRole 認證與簽發| V
  U -->|HTTP 或 HTTPS：查看憑證狀態| W
```

Bob 在學員電腦使用；部署工具與 Liberty 在該組 VM 執行。學員可透過瀏覽器開啟講師提供的 Vault UI 網址，查看權限內的憑證狀態。

## 操作前準備

在 Bob IDE Terminal 登入自己的 Liberty VM，以第 1 組為例：

```bash
# 在學員電腦查詢該組 SSH config 的有效 HostName；此例為第 1 組
ssh -G liberty1 | awk '$1 == "hostname" {print $2; exit}'
# 記下輸出的 VM IP，再登入同一台 VM
ssh liberty1
# 以下在 Liberty VM 執行，自行建立本課工作目錄
mkdir -p ~/clm-workshop
cd ~/clm-workshop
hostname
whoami
/opt/ibm/wlp/bin/server status defaultServer
openssl version
```

確認該組 Vault API 位址、信任 CA、PKI mount／role，以及 AppRole Role ID／Secret ID 的本機檔案位置。Secret ID 是本路線 Agent auto-auth 使用的認證，值不要貼進對話。

**先讓 Bob 確認實際環境：**

```text
請協助檢查 Liberty server.xml，確認是否已設定 HTTPS、port 與 keystore；若已有憑證才讀取其 SAN，並確認服務控制方式，只讀公開憑證與設定，不顯示私鑰或密碼。
請列出本路線所需檔案與認證的位置，缺少時先指出缺項，不要假設存在 env.sh、程式骨架或參考完成檔。工作目錄是現在建立的 ~/clm-workshop，Agent 用 HCL 指定實際路徑，hook 使用明確參數；請依確認結果給完整執行命令。
```

缺少 CA、role 或認證資料時，先向講師確認。後續程式與設定檔須先讓 Bob 產生、檢視，再執行。

### 部署前確認、部署後驗證

**開始時沒有 HTTPS 或憑證也可以做。** 部署前只檢查 Liberty 設定；已提供憑證才記錄舊序號。部署完成後，才檢查服務是否送出本次產生的憑證。

**Liberty VM IP 從學員電腦的 SSH config 查詢**（用前面的 `ssh -G liberty1`，其他組換自己的編號）。把輸出的實際 IP 用於憑證 IP SAN 與驗證的 `TLS_HOST`，不要把 SSH 別名當 IP，也不要在 VM 內假設有相同 SSH config。以下驗證函式在 Liberty VM 執行；另加入 `127.0.0.1` IP SAN，可供本機測試使用。不需要 DNS 名稱或 DNS challenge。

**給 Bob 的部署要求：**

```text
請支援首次部署與後續輪換兩種情況：沒有 keystore 或未設定 HTTPS 時，建立 PKCS12、補齊 Liberty 必要的 HTTPS／keyStore 設定；已有憑證才做到期判斷與舊檔備份。不要對不存在的憑證做日期判斷，首次部署也不能 skip。修改 server.xml 前先備份，保留原有其他功能與連接埠設定。啟動後比對線上與本次產出的 leaf 憑證指紋，並驗證 CA 信任與 IP SAN。
IP SAN 必須包含從 SSH config 查到的 Liberty VM IP，另加入 127.0.0.1，不使用 DNS challenge，不要求真實 DNS 名稱。所需路徑明確傳入腳本或設定，不依賴未提供的設定檔。
```

以下函式在目前 Terminal 定義一次；`record_baseline` 在步驟 1 使用，`check_cert` 在部署完成後使用。將 CA 與本次 leaf 路徑換成實際輸出位置後，才執行 `check_cert`。這些變數只供驗證使用。

<details>
<summary>展開設定與驗證函式：record_baseline／check_cert</summary>

```bash
set -o pipefail
TLS_HOST='填入學員電腦SSH config查到的Liberty VM IP'
TLS_PORT=9443 # 以實際設定為準
CA_FILE='/實際路徑/ca.crt'
LEAF_FILE='/實際路徑/server.crt'

record_baseline() (
  set -o pipefail
  # 僅記錄公開資訊，不宣稱舊憑證已通過信任驗證
  if timeout 10 openssl s_client -connect "${TLS_HOST}:${TLS_PORT}" \
      </dev/null 2>baseline-tls.log \
      | openssl x509 -noout -serial -issuer -dates > before.tmp; then
    mv before.tmp before.txt
    cat before.txt
  else
    rm -f before.tmp before.txt
    echo '尚未取得線上憑證，確認設定後走首次部署流程。'
  fi
)

check_cert() (
  set -euo pipefail
  : "${TLS_HOST:?}" "${TLS_PORT:?}" "${CA_FILE:?}" "${LEAF_FILE:?}"
  peer=$(timeout 10 openssl s_client \
    -connect "${TLS_HOST}:${TLS_PORT}" -verify_ip "$TLS_HOST" \
    -CAfile "$CA_FILE" -verify_return_error \
    </dev/null 2>tls-check.log | openssl x509 -outform PEM)
  expected=$(openssl x509 -in "$LEAF_FILE" -noout -fingerprint -sha256)
  actual=$(printf '%s\n' "$peer" | openssl x509 -noout -fingerprint -sha256)
  [ "$expected" = "$actual" ] || { echo '線上憑證與本次產出不一致' >&2; exit 1; }
  printf '%s\n' "$peer" | openssl x509 -noout -serial -issuer -dates -ext subjectAltName
  echo '驗證通過：TLS、CA 信任、IP SAN 與本次憑證指紋一致'
)
```

</details>

`record_baseline` 無法取得憑證時，先看設定與 `baseline-tls.log`，不直接認定憑證過期或信任有誤。`check_cert` 失敗則查看 `tls-check.log`；不能用忽略驗證的方式當作完成。

### Vault 簽發設定

確認該組 role 允許 IP SAN（`allow_ip_sans=true`），簽發請求的 `ip_sans` 帶入 SSH config 查到的 VM IP 與 `127.0.0.1`。純 IP 測試可由講師將該組 role 設為 `require_cn=false`，並省略 CN；若保留必填 CN，使用 role 允許的標籤並避免自動加入 DNS SAN（`exclude_cn_from_sans=true`）。共用 role 由講師確認，不由學員任意修改。這是私有 PKI 的 role 權限，不是 DNS challenge。

## 實作流程

### 1. 辨識現況｜5 分鐘

檢查 HTTPS／keystore 設定；有舊憑證才記錄序號，沒有則走首次部署。確認 Agent 尚未執行。

**給 Bob 的提示：**

```text
我是 SP／OP 人員，請先簡要解釋：
1. TLS 憑證生命週期的申請、核發、部署、監控、輪換與撤銷。
2. Liberty 的 JKS 與 PKCS12 有何差異，本次為何選 PKCS12。
3. 自動輪換與手動置換的風險差異。
4. Vault PKI Secrets Engine 在 CLM 的角色，以及 role 如何限制簽發。
5. Vault Agent 如何取得認證並自動重新簽發憑證。

再根據本次環境：
向 Bob 說明講師環境設定，請它畫出 Vault PKI、Agent、部署 hook 與 Liberty 的關係，指出每個元件負責什麼。
```

**操作指令（Liberty VM）：**

```bash
vault version
record_baseline
```

**檢查點：** HTTPS 現況（有憑證才記錄）。

### 2. 完成 Agent 設定｜12 分鐘

確認該組 AppRole、PKI role 與認證檔位置，請 Bob 產生 auto-auth 與 template 設定。

**給 Bob 的提示：**

```text
請產生 Agent HCL 與 template：AppRole ID／Secret ID 只讀取本機檔案，不要將值寫進回覆。使用 pkiCert，單次簽發輸出同一份 PEM bundle，包含 leaf、私鑰與 CA 鏈。hook 只在成功渲染後執行；設定執行逾時。不要把私鑰分成獨立簽發的 template。
```

**操作指令（Liberty VM）：**

```bash
vault agent -help
# 請 Bob 產生 HCL 與 template，再檢視檔案內容
# 不要用 cat 回顯 role-id／secret-id 等秘密檔案
```

**檢查點：** 可啟動的 HCL 與 template。

### 3. 補完部署 hook｜15 分鐘

由 Bob 補齊 bundle 拆分、PKCS12 轉換及部署驗證，沿用已確認的 Liberty 控制方式。

**給 Bob 的提示：**

```text
請產生 deploy-hook.sh：使用互斥鎖，從單一 bundle 拆出配對的 key／cert／chain，驗證私鑰與憑證公鑰一致及憑證鏈；在暫存目錄轉成 PKCS12，再備份並原子替換 live keystore。明確處理每一步失敗；只有變更時受控重啟 Liberty。驗證失敗還原舊 keystore 並恢復服務，不輸出秘密。
```

**操作指令（Liberty VM）：**

```bash
bash -n ./deploy-hook.sh
chmod 700 ./deploy-hook.sh
# hook 由 Agent 成功渲染後觸發，勿在 bundle 尚未產生前執行
```

**檢查點：** hook 與首次部署紀錄。

### 4. 觀察自動輪換｜13 分鐘

啟動 Agent，使用講師確認可用的短 TTL 測試 role（建議 3 分鐘），持續觀察約兩個週期及線上憑證序號。

**給 Bob 的提示：**

```text
請檢查 Agent log、template 與 hook 執行紀錄，解釋重新簽發與 Token renewal 的不同。確認線上序號跟 bundle 的 leaf 相同；不要以 Agent 程序存活作為換證成功依據。
```

**操作指令（Liberty VM）：**

```bash
mkdir -p logs
# 前景執行；以 Ctrl+C 停止。另開 SSH Terminal 觀察線上憑證
vault agent -config=./liberty-agent.hcl 2>&1 | tee logs/agent.log
# 另一個 Terminal 先 設定本頁驗證變數並載入 check_cert 函式
# 每隔約 30 秒呼叫 check_cert，記錄序號變更
```

**檢查點：** 至少一次無人工執行 hook 的線上序號變更。

### 5. 核對自動輪換結果｜10 分鐘

比對 Agent log、bundle 與線上憑證，確認至少一次由 Agent 自動觸發的重新簽發及部署。

**給 Bob 的提示：**

```text
請協助比對 Agent／hook 日誌、bundle 憑證序號與線上序號，整理簽發、部署、驗證三個時間點。說明 AppRole Token renewal 與憑證重新簽發的差異；若未觀察到輪換，列出待確認項目，不要把程序存活視為成功。
```

**操作指令（Liberty VM）：**

```bash
# 在另一個 SSH Terminal 重新設定本頁驗證變數並載入 check_cert 函式
check_cert | tee after.txt
tail -n 50 logs/agent.log
if [ -s before.txt ]; then
  diff -u before.txt after.txt || true
else
  echo '首次部署：以線上與本次產出憑證一致作為驗收，不比較舊序號。'
fi
```

**檢查點：** 自動簽發／部署紀錄與線上序號一致。

### 6. 成果交付｜5 分鐘

停止短 TTL 測試 Agent，恢復講師指定的基準或一般 TTL 設定，提交設定、hook 與部署後憑證資訊（有舊憑證才附前後序號）。

**給 Bob 的提示：**

```text
請依實際紀錄整理五行交接：架構、觸發條件、驗證方式、失敗保護及未完成事項。
```

**操作指令（Liberty VM）：**

```bash
# 在 Agent 前景 Terminal 按 Ctrl+C，恢復講師指定的一般 TTL 設定
check_cert | tee after.txt
if [ -s before.txt ]; then
  diff -u before.txt after.txt || true
else
  echo '首次部署：以線上與本次產出憑證一致作為驗收，不比較舊序號。'
fi
```

**檢查點：** 交接紀錄與測試程序清理。

## Agent 注意事項

PKI leaf 輪換是重新簽發；AppRole Token renewal 是另一件事。短 TTL 測試須確認 role、CA 剩餘效期及 Agent template 行為；若未觀察到自動輪換，記錄未完成事項。

[官方 Agent template 說明](https://developer.hashicorp.com/vault/docs/agent-and-proxy/agent/template)

## 60 分鐘內的完成標準

1. 首次部署：HTTPS 成功提供本次憑證，CA 信任與 IP SAN 驗證通過；已有憑證則另外比較換證部署後憑證資訊（有舊憑證才附前後序號）。
2. Agent 自動觸發至少一次重新簽發與部署，日誌及線上序號吻合。
3. 留下程式／設定、部署後憑證資訊（有舊憑證才附前後序號）與簡短交接，不含秘密。

## 延伸練習（不計入 60 分鐘）

- Cheat sheet 參考：[Bob Cheat Sheet](https://owhc.github.io/bob-cheatsheet/bob-lite-ver.html)
- 使用測試複本或變數觸發錯誤，驗證失敗保護與部署失敗後還原。
- 完整 CA 建置、AGENTS.md、Slash Command、可重用 Skill、Frontend Slides 簡報與多台部署。

## Cheatsheet：實作流程與檢查點

| 時間 | 工作 | 檢查點 |
|---|---|---|
| 00–05 分 | 辨識現況 | HTTPS 現況（有憑證才記錄）。 |
| 05–17 分 | 完成 Agent 設定 | 可啟動的 HCL 與 template。 |
| 17–32 分 | 補完部署 hook | hook 與首次部署紀錄。 |
| 32–45 分 | 觀察自動輪換 | 至少一次無人工執行 hook 的線上序號變更。 |
| 45–55 分 | 核對自動輪換結果 | 自動簽發／部署紀錄與線上序號一致。 |
| 55–60 分 | 成果交付 | 交接紀錄與測試程序清理。 |
