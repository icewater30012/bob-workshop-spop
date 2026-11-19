#!/usr/bin/env python3
"""Build browser-readable workshop handouts and synchronize the tabbed viewer.
Uses only Python's standard library; Markdown is the editable source.
"""
from pathlib import Path
import re
from html import escape as e
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'topics/vault-liberty-clm'
index=BASE/'index.html'
s=index.read_text()
css='''pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f0f4fa;border:1px solid #dce4ee;border-radius:8px;padding:16px;font:14px/1.7 ui-monospace,monospace}code{font-family:ui-monospace,monospace}table{border-collapse:collapse;width:100%;margin:18px 0}th,td{border:1px solid #dce4ee;padding:10px;text-align:left}th{background:#edf3fa}.handout{max-width:1100px;margin:auto}.handout h2{margin-top:32px}.handout h3{margin-top:26px}.full-material{background:white;border:1px solid #dde5ed;padding:24px;border-radius:12px;margin-top:24px}.overview-info{margin-top:26px}.command-card{margin-top:14px}.command-card pre{font-size:13px}.table-wrap{overflow-x:auto}.handout svg{max-height:none}'''
if '.overview-info{' not in s:s=s.replace('</style>',css+'</style>')
css2='''.optional-note{background:#fff4d6;border:1px solid #f0b429;border-left:8px solid #f59e0b;border-radius:8px;padding:14px 18px;margin:16px 0;color:#5b3a00}.optional-note strong{color:#8a4b00}details.optional-steps{border:2px dashed #f0b429;border-radius:10px;padding:4px 16px;margin:16px 0;background:#fffdf5}details.optional-steps>summary{cursor:pointer;font-weight:700;color:#8a4b00;padding:10px 0}'''
if '.optional-note{' not in s:s=s.replace('</style>',css2+'</style>')
style=re.search(r'<style>(.*?)</style>',s,re.S)[1]
def inline(t):
 t=e(t)
 t=re.sub(r'`([^`]+)`',r'<code>\1</code>',t)
 t=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',t)
 def link(m):
  href=m[2]
  if not href.startswith(('https:','http:','#')):href=re.sub(r'\.md(?=#|$)', '.html',href)
  return '<a href="'+href+'">'+m[1]+'</a>'
 return re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,t)
def render(md,svg=''):
 lines=md.splitlines();out=[];i=0
 while i<len(lines):
  line=lines[i]
  if not line.strip():i+=1;continue
  if line in ('<details>','</details>') or line.startswith('<details class=') or (line.startswith('<summary>') and line.endswith('</summary>')):
   out.append(line);i+=1;continue
  if line.startswith('```'):
   lang=line[3:].strip();i+=1;block=[]
   while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
   if lang=='mermaid':out.append('<div class="architecture">'+svg+'</div>')
   else:out.append('<pre><code class="language-'+e(lang)+'">'+e('\n'.join(block))+'</code></pre>')
   i+=1;continue
  if line.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].startswith('|'):
    cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch(r':?-+:?',c) for c in cells):rows.append(cells)
    i+=1
   out.append('<div class="table-wrap"><table>'+''.join('<tr>'+''.join('<'+('th' if n==0 else 'td')+'>'+inline(c)+'</'+('th' if n==0 else 'td')+'>' for c in row)+'</tr>' for n,row in enumerate(rows))+'</table></div>');continue
  h=re.match(r'^(#{1,6}) (.*)',line)
  if h:out.append(f'<h{len(h[1])}>{inline(h[2])}</h{len(h[1])}>');i+=1;continue
  if re.match(r'^(- |\d+\. )',line):
   ordered=bool(re.match(r'^\d+\.',line));tag='ol' if ordered else 'ul';items=[]
   while i<len(lines) and re.match(r'^(- |\d+\. )',lines[i]):items.append('<li>'+inline(re.sub(r'^(- |\d+\. )','',lines[i]))+'</li>');i+=1
   out.append('<'+tag+'>'+''.join(items)+'</'+tag+'>');continue
  if line.startswith('> ! '):out.append('<blockquote class="optional-note">'+inline(line[4:])+'</blockquote>');i+=1;continue
  if line.startswith('> '):out.append('<blockquote>'+inline(line[2:])+'</blockquote>');i+=1;continue
  out.append('<p>'+inline(line)+'</p>');i+=1
 return '\n'.join(out)
def document(title,body):return '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+e(title)+'</title><style>'+style+'</style></head><body><main class="handout">'+body+'</main></body></html>'
for n,p in enumerate(sorted((BASE/'parts').glob('part-*.md')),1):
 pat=rf'<section id="part-{n}".*?</section>'
 section=re.search(pat,s,re.S)[0]
 svg=(ROOT/f'tools/diagrams/part-{n}.svg').read_text().strip()
 svg=svg.replace('學員電腦與 Liberty VM；不需要 Vault Server VM','學員電腦與 Liberty VM')
 svg=re.sub(r'<text\b[^>]*>不需要 Vault Server VM</text>', '', svg)
 md=p.read_text();body=render(md,svg)
 p.with_suffix('.html').write_text(document(f'IBM Bob workshop｜Scenario {n}',body))
 embedded=body.replace('href="../README.html"','href="#home"').replace(f'href="../index.html#part-{n}"',f'href="#part-{n}"')
 # Keep the title, architecture and full instructions in the same Scenario block.
 section=f'<section id="part-{n}" hidden><div class="full-material" id="material-{n}">'+embedded+'</div><!-- full-material-end --></section>'
 s=re.sub(pat,lambda m:section,s,count=1,flags=re.S)
# Overview order follows Markdown; the choice cards are always last.
overview=(BASE/'README.md').read_text();info=overview[overview.index('## Workshop 目標'):overview.index('## 選擇情境')]
home=re.search(r'<section id="home">.*?</section>',s,re.S)[0]
cards=re.search(r'<div class="combos">.*?</div>(?=<div class="overview-info">|</section>|\s*<)',home,re.S)
# Card grid contains only article elements, so its first closing div ends the grid.
cards=re.search(r'<div class="combos">.*?</div>',home,re.S)[0]
for label,stars in [('進階','⭐⭐⭐⭐'),('中高階','⭐⭐⭐'),('中階','⭐⭐'),('入門','⭐')]:
 cards=re.sub(r'(?:⭐+\s*)?'+label+' · 60 分鐘',stars+' '+label+' · 60 分鐘',cards)
home='<section id="home"><div class="overview-info">'+render(info)+'</div><!-- overview-info-end --><h2>選擇一個情境，完成一次換證</h2><p class="muted">四個 Scenario 各自獨立、互不相依，每組只選一個，60 分鐘。星等為四個情境的相對難度（⭐～⭐⭐⭐⭐）。</p>'+cards+'</section>'
s=re.sub(r'<section id="home">.*?</section>',lambda m:home,s,count=1,flags=re.S)
# Also make footer links browser-readable.
s=re.sub(r'<a href="INSTRUCTOR\.(md|html)">[^<]*</a>(?: · )?','',s)
s=s.replace('href="INSTRUCTOR.md"','href="INSTRUCTOR.html"').replace('href="README.md"','href="README.html"').replace('Markdown 總覽','完整總覽')
s=re.sub(r'<title>.*?</title>','<title>IBM Bob workshop｜SP／OP 憑證自動化</title>',s,count=1)
# Resolve fragments inside the active Scenario as well as top-level tabs.
s=s.replace("const valid=target&&target.tagName==='SECTION'?id:'home';", "const owner=target&&(target.tagName==='SECTION'?target:target.closest('main>section'));const valid=owner?owner.id:'home';")
s=s.replace("else a.removeAttribute('aria-current')});}","else a.removeAttribute('aria-current')});if(target&&owner&&target!==owner)requestAnimationFrame(()=>target.scrollIntoView({block:'start'}));}")
index.write_text(s)
for name in ['README','INSTRUCTOR']:
 p=BASE/(name+'.md');p.with_suffix('.html').write_text(document('IBM Bob workshop｜'+name,render(p.read_text())))
(ROOT/'README.html').write_text(document('IBM Bob workshop',render((ROOT/'README.md').read_text())))
print('Built four unified Scenario handouts with final cheatsheets, overview and instructor page.')
