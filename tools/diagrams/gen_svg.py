import re
from pathlib import Path
BLUE='#4482ca'; GREEN_BG='#eef8f4'
def box(x,y,w,h,t1,t2=None,fill='white',stroke='#c1d4e9',sw=1,f1=16,f2=13):
    cx=x+w/2
    o=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    if t2:
        o+=f'<text x="{cx}" y="{y+h/2-4}" text-anchor="middle" font-size="{f1}">{t1}</text><text x="{cx}" y="{y+h/2+19}" text-anchor="middle" font-size="{f2}">{t2}</text>'
    else:
        o+=f'<text x="{cx}" y="{y+h/2+6}" text-anchor="middle" font-size="{f1}">{t1}</text>'
    return o
def arrow(d,mid,dash=False):
    da=' stroke-dasharray="6 4"' if dash else ''
    return f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="2"{da} marker-end="url(#{mid})"/>'
def lab(x,y,t,fs=16,fill='#476382'):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{fs}" fill="{fill}">{t}</text>'
def gen(n,left,right,lr_arrow,lr_label,vault_label,arrow_dir):
    """n=part number; vault_label None => no Vault"""
    mid=f'arch{n}'; vault=vault_label is not None
    W=1320 if vault else 980; H=560 if vault else 500
    o=f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Scenario {n} 主機部署架構"><defs><marker id="{mid}" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L6,3" fill="{BLUE}"/></marker></defs>\n'
    # student
    o+='<rect x="20" y="100" width="220" height="%d" rx="14" fill="#f0f5fc" stroke="#99b6d6" stroke-width="2"/>'%(380 if vault else 300)
    o+='<text x="130" y="140" text-anchor="middle" font-size="22" fill="#173e68">學員電腦</text>'
    o+=box(35,170,190,65,'IBM Bob IDE','SSH Terminal／HTTPS 測試',f2=14)
    o+=box(35,295,190,65,'瀏覽器','開啟 Liberty AdminCenter',f2=13)
    if vault: o+=box(35,385,190,65,'瀏覽器','開啟 Vault Web UI',f2=14)
    # Liberty VM
    o+=f'<rect x="480" y="30" width="460" height="440" rx="14" fill="{GREEN_BG}" stroke="#81bca4" stroke-width="2"/><text x="710" y="65" text-anchor="middle" font-size="22" fill="#173e68">Liberty VM：各組獨立</text>\n'
    o+=box(500,95,200,60,left[0],left[1])
    o+=box(730,95,190,60,right[0],right[1],f2=14)
    o+='<rect x="610" y="215" width="310" height="225" rx="12" fill="#fff" stroke="#81bca4" stroke-width="2"/><text x="765" y="252" text-anchor="middle" font-size="21" fill="#173e68">Liberty server</text><text x="765" y="284" text-anchor="middle" font-size="15">TLS 設定讀取下方憑證檔</text>'
    o+='<rect x="635" y="325" width="260" height="75" rx="8" fill="#eaf3ff" stroke="#a3c7f3"/><text x="765" y="353" text-anchor="middle" font-size="17">PKCS12 keystore 檔案</text><text x="765" y="379" text-anchor="middle" font-size="14">server.crt ＋ server.key</text>\n'
    # https badge
    o+='<rect x="430" y="295" width="100" height="65" rx="10" fill="#eaf3ff" stroke="#4482ca" stroke-width="2"/><text x="480" y="321" text-anchor="middle" font-size="16" fill="#173e68">HTTPS</text><text x="480" y="346" text-anchor="middle" font-size="19" fill="#173e68">:9443</text>\n'
    o+=arrow('M240 125 H500',mid)+lab(370,111,'SSH：操作與傳送檔案')
    o+=arrow('M240 327 H430',mid)+lab(335,312,'HTTPS 連線與驗證')+lab(335,350,'/adminCenter/',13)
    o+=arrow('M530 327 H610',mid)
    # left<->right row arrow
    if arrow_dir=='right': o+=arrow('M700 125 H730',mid)
    else: o+=arrow('M730 125 H700',mid)
    if lr_label: o+=lab(715,86,lr_label,13)
    o+=arrow('M560 155 V363 H635',mid,True)+lab(522,203,'部署檔案',14)
    if vault:
        o+='<rect x="1060" y="30" width="240" height="440" rx="14" fill="#f4f0fc" stroke="#b7a0d2" stroke-width="2"/><text x="1180" y="65" text-anchor="middle" font-size="22" fill="#173e68">Vault Server VM</text>\n'
        o+=box(1080,95,200,60,'Vault Server','API Port :8200',f2=14)
        o+=box(1080,195,200,60,'PKI Secrets Engine','每組獨立 role',f2=14)
        o+=f'<path d="M1180 155 V195" stroke="{BLUE}" stroke-width="2" fill="none"/>'
        o+=box(1080,390,200,55,'Vault Web UI','講師提供網址',f2=14)
        o+=f'<path d="M1180 255 V300" stroke="#c1d4e9" stroke-width="2" fill="none" stroke-dasharray="3 3"/>'
        o+=lab(1180,350,'講師管理／各組共用',14,'#173e68')
        o+=arrow('M920 125 H1080',mid)+lab(1000,111,vault_label[0],14)+lab(1000,150,vault_label[1],14,'#173e68')
        # browser -> Vault UI over bottom
        o+=f'<path d="M130 450 V505 H1180 V445" fill="none" stroke="#9862cd" stroke-width="2" marker-end="url(#{mid})"/>'
        o+=lab(655,535,'瀏覽器 → Vault UI：HTTPS 查看權限內的憑證狀態',15,'#7840ad')
    o+='</svg>'
    return o
S={
1:gen(1,('部署 Shell script','轉 PKCS12 並重載 Liberty'),('Vault Agent','監控並自動重新簽發'),'left','憑證更新後觸發',('Vault API','認證／簽發'),'left'),
2:gen(2,('crontab ＋ Shell 腳本','排程與部署'),('Vault CLI','以 Token 申請憑證'),'right','呼叫',('Vault API','Token 簽發'),'right'),
3:gen(3,('Ansible Playbook','localhost connection 部署'),('OpenSSL','建立自簽 CA 並簽發憑證'),'right','呼叫',None,'right'),
4:gen(4,('crontab ＋ Shell 腳本','排程與部署'),('OpenSSL','產生伺服器自簽憑證'),'right','呼叫',None,'right'),
}
if __name__=='__main__':
    html='<!doctype html><meta charset=utf-8><body style="font-family:system-ui;max-width:1100px;margin:auto">'+''.join(f'<h2>Scenario {n}</h2>{s}' for n,s in S.items())
    Path('preview.html').write_text(html)
