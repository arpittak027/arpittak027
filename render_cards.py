#!/usr/bin/env python3
"""Render animated GitHub profile SVG cards. STATIC=1 renders final frames."""
import os, json, base64, subprocess
from pathlib import Path
from datetime import date, timedelta
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'cards'; DATA=ROOT/'data/contributions.json'
STATIC=os.getenv('STATIC')=='1'
BG='#0B1020'; PANEL='#111A2E'; BORDER='#263451'; BRAND='#8B7CFF'; AQUA='#63D6C8'; WHITE='#F3F5FF'; MUTED='#A6B1CC'
FONT='Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif'
def esc(x): return escape(str(x))
def font_css():
    src=ROOT/'assets/fonts/Inter[opsz,wght].ttf'; dst=OUT/'Inter-subset.woff'
    if not src.exists(): return ''
    try:
        subprocess.run(['pyftsubset',str(src),f'--output-file={dst}','--flavor=woff','--unicodes=U+0020-007E,U+00A0-00FF','--layout-features=*'],check=True,capture_output=True)
        return '@font-face{font-family:Inter;src:url(data:font/woff;base64,'+base64.b64encode(dst.read_bytes()).decode()+') format(\'woff\')}'
    except Exception: return ''
def render(name,w,h,body,delay=0):
    anim='' if STATIC else f'.enter{{opacity:0;transform:translateY(16px);animation:rise .8s ease {delay}s forwards}} @keyframes rise{{to{{opacity:1;transform:translateY(0)}}}}'
    if STATIC: anim='.enter{opacity:1;transform:none}'
    doc=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><title>Arpit Tak GitHub profile</title><style>{font_css()} text{{font-family:{FONT};fill:{WHITE}}}.muted{{fill:{MUTED}}}.brand{{fill:{BRAND}}}.aqua{{fill:{AQUA}}}{anim}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}.enter{{opacity:1;transform:none}}}}</style><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="{BG}" stroke="{BORDER}"/><rect x="1" y="1" width="{w-2}" height="4" rx="2" fill="{BRAND}"/>{body}</svg>'''
    OUT.mkdir(parents=True,exist_ok=True); (OUT/name).write_text(doc,encoding='utf-8')
def load_days():
    if not DATA.exists(): return []
    x=json.loads(DATA.read_text()); x=x.get('data',x); x=x.get('user',{}).get('contributionsCollection',{}).get('contributionCalendar',x)
    return [d for week in x.get('weeks',[]) for d in week.get('contributionDays',[])] if 'weeks' in x else x.get('days',[])
def n(d): return int(d.get('contributionCount',d.get('count',0)))
def main():
    OUT.mkdir(parents=True,exist_ok=True); portrait=ROOT/'assets/portrait.png'; avatar=''
    if portrait.exists():
        b=base64.b64encode(portrait.read_bytes()).decode(); avatar=f'<defs><clipPath id="p"><circle cx="785" cy="115" r="53"/></clipPath></defs><image href="data:image/png;base64,{b}" x="732" y="62" width="106" height="106" clip-path="url(#p)"/><circle cx="785" cy="115" r="56" fill="none" stroke="{AQUA}" stroke-width="2"/>'
    hero=f'<g class="enter"><circle cx="790" cy="80" r="180" fill="{BRAND}" opacity=".08"/><text x="48" y="55" class="aqua" font-size="13" letter-spacing="3">HELLO, WORLD / DEVELOPER PROFILE</text><text x="48" y="132" font-size="58" font-weight="800">Arpit Tak</text><text x="51" y="174" font-size="18" class="muted">Building web products and exploring how AI agents can make software better.</text><rect x="50" y="207" width="176" height="34" rx="17" fill="{BRAND}" opacity=".2"/><text x="81" y="229" font-size="12" font-weight="700">FULL-STACK · AI</text><text x="50" y="277" font-size="12" class="muted">LESS CONSUMING. MORE BUILDING.</text>{avatar}</g>'
    render('01-hero.svg',900,310,hero,0)
    for i,(label,sub,url) in enumerate([('PORTFOLIO','Visit my website','https://arpittak.netlify.app/'),('LINKEDIN','Connect professionally','https://www.linkedin.com/in/arpit-tak-a865492a4'),('GITHUB','Explore my code','https://github.com/arpittak027')],1):
        body=f'<a href="{url}" xlink:href="{url}"><g class="enter"><rect x="15" y="14" width="270" height="112" rx="17" fill="{PANEL}" stroke="{BORDER}"/><text x="36" y="49" class="aqua" font-size="12">{label}</text><text x="36" y="82" font-size="17">{sub}</text><text x="250" y="108" class="brand" font-size="21">↗</text></g></a>'
        render(f'02-link-{i}.svg',300,140,body,1)
    days=load_days(); counts={str(d.get('date',''))[:10]:n(d) for d in days}; today=date.today(); span=[today-timedelta(days=i) for i in range(364,-1,-1)]
    active=sum(counts.get(d.isoformat(),0)>0 for d in span); total=sum(counts.get(d.isoformat(),0) for d in span); cur=today if counts.get(today.isoformat(),0)>0 else today-timedelta(days=1); streak=0
    while counts.get(cur.isoformat(),0)>0: streak+=1; cur-=timedelta(days=1)
    busy=max(counts,key=counts.get) if counts else '—'; busylabel=date.fromisoformat(busy).strftime('%b %d, %Y') if busy!='—' else '—'
    months=[]
    for k in range(11,-1,-1):
        y,m=today.year,today.month-k
        while m<=0: y-=1; m+=12
        months.append(date(y,m,1))
    vals=[sum(v for key,v in counts.items() if key.startswith(m.strftime('%Y-%m'))) for m in months]; peak=max(vals or [1]) or 1; bars=[]
    for i,(m,v) in enumerate(zip(months,vals)):
        x=62+i*66; h=100*v/peak; bars.append(f'<rect x="{x}" y="{177-h:.1f}" width="34" height="{h:.1f}" rx="6" fill="{BRAND}"><title>{m:%B}: {v}</title></rect><text x="{x+17}" y="199" text-anchor="middle" font-size="10" class="muted">{m:%b}</text>')
    activity=f'<g class="enter"><text x="40" y="43" font-size="22">Your coding activity</text><text x="40" y="65" font-size="12" class="muted">Monthly contributions · trailing 12 months</text><rect x="38" y="82" width="824" height="132" rx="14" fill="{PANEL}"/>{"".join(bars)}<g transform="translate(42 260)"><text font-size="29" class="aqua">{streak}</text><text y="22" font-size="11" class="muted">DAY STREAK</text><text x="205" font-size="29">{active}</text><text x="205" y="22" font-size="11" class="muted">ACTIVE DAYS</text><text x="410" font-size="29">{total}</text><text x="410" y="22" font-size="11" class="muted">CONTRIBUTIONS</text><text x="645" font-size="16">{busylabel}</text><text x="645" y="22" font-size="11" class="muted">BUSIEST DAY</text></g></g>'
    render('03-activity.svg',900,305,activity,2)
    repos=[('OUTPOST','AGENTIC COLLABORATIVE WORKSPACE','Humans and AI agents design systems, diagrams and technical documentation together in real time.','Next.js · TypeScript · Gemini · tldraw · Yjs · Prisma · PostgreSQL','https://github.com/arpittak027/OUTPOST'),('SUR','INTERACTIVE WEB EXPERIENCE','An interactive experience showcasing wind chimes from different countries through motion and responsive design.','HTML · CSS · JavaScript · GSAP · SVG','https://github.com/arpittak027/Sur')]
    for i,(name,kind,desc,stack,url) in enumerate(repos,1):
        body=f'<g class="enter"><text x="42" y="48" class="aqua" font-size="12">FEATURED PROJECT / 0{i}</text><text x="42" y="105" font-size="37" font-weight="800">{name}</text><text x="42" y="137" font-size="11" class="brand">{kind}</text><text x="42" y="177" font-size="15" class="muted">{esc(desc)}</text><text x="42" y="214" font-size="12" class="aqua">{esc(stack)}</text><a href="{url}" xlink:href="{url}"><rect x="42" y="235" width="188" height="38" rx="19" fill="{BRAND}"/><text x="136" y="259" text-anchor="middle" font-size="12">EXPLORE PROJECT ↗</text></a><text x="820" y="252" text-anchor="end" font-size="86" fill="{BRAND}" opacity=".22">0{i}</text></g>'
        render(f'04-project-{i}.svg',900,295,body,3+(i-1)*1.2)
    palette=['#202B43','#423C83','#6255B8',BRAND,AQUA]; start=today-timedelta(days=363); start-=timedelta(days=(start.weekday()+1)%7); cells=[]
    for i in range(371):
        d=start+timedelta(days=i)
        if d>today: break
        c=counts.get(d.isoformat(),0); level=0 if c==0 else 1 if c<3 else 2 if c<6 else 3 if c<10 else 4
        cells.append(f'<rect x="{58+(i//7)*14}" y="{76+(i%7)*14}" width="10" height="10" rx="2" fill="{palette[level]}"><title>{d.isoformat()}: {c}</title></rect>')
    graph=f'<g class="enter"><text x="40" y="40" font-size="22">Contribution graph</text><text x="40" y="61" font-size="12" class="muted">A year of building, one day at a time</text>{"".join(cells)}<text x="60" y="205" font-size="11" class="muted">LESS</text>'+''.join(f'<rect x="{105+i*16}" y="195" width="10" height="10" fill="{c}"/>' for i,c in enumerate(palette))+'<text x="190" y="205" font-size="11" class="muted">MORE</text></g>'
    render('99-contributions.svg',900,225,graph,6); print(f'Rendered {len(list(OUT.glob("*.svg")))} cards; STATIC={int(STATIC)}')
if __name__=='__main__': main()
