import re, json, sys, subprocess
def parse(pdf, subject, patch=False):
    t = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True).stdout
    lines = [l.strip() for l in t.replace('\f','\n').split('\n')]
    lines = [l for l in lines if l and not re.fullmatch(r'\d+', l) and '押题卷（' not in l and l not in ('参考答案',) and not l.startswith('科目')]
    qs=[]; cur=None; sect=None; field=None; expect=1
    for l in lines:
        m = re.match(r'^[一二三]、\s*(判断|单项选择|多项选择|单选|多选)', l)
        if m: sect={'判断':'tf','单选':'single','多选':'multi','单项选择':'single','多项选择':'multi'}[m.group(1)]; continue
        m = re.match(r'^(\d+)\.\s*(.*)$', l)
        if m and int(m.group(1))==expect and (cur is None or field=='exp' or '缺失' in cur['q']):
            cur={'n':expect,'type':sect,'q':m.group(2),'opts':[],'ans':'','exp':''}; qs.append(cur); expect+=1; field='q'; continue
        if cur is None: continue
        m = re.match(r'^([A-E])[\.．]\s*(.*)$', l)
        if m and field in ('q','opt') and len(cur['opts'])==ord(m.group(1))-65:
            cur['opts'].append(m.group(2)); field='opt'; continue
        m = re.match(r'^正确答案[：:]\s*([A-E]+)', l)
        if m and field in('q','opt'): cur['ans']=m.group(1); field='ans'; continue
        m = re.match(r'^解析[：:]\s*(.*)$', l)
        if m and field=='ans': cur['exp']=m.group(1); field='exp'; continue
        if field=='q': cur['q']+=l
        elif field=='opt': cur['opts'][-1]+=l
        elif field=='exp':
            if l.startswith('·') or re.match(r'^(易混|同类|知识|拓展|考点|注意|对比|补充)',l): cur['exp']+='\n'+l
            else: cur['exp']+=l
    for q in qs:
        e=q['exp']
        e=re.sub(r'\s*(同类对比|易混对比|知识拓展|拓展)[\u2011\s]+', lambda m:'\n'+m.group(1)+'——', e)
        e=re.sub(r'\s*\u2011\s+', '\n· ', e)
        e=re.sub(r'\n+', '\n', e).strip()
        q['exp']=e
        if not patch: continue
        if q['n']==82 and '缺失' in q['q']:
            q.update(q='著名民间长篇叙事诗《孔雀东南飞》首见于（ ）。', opts=['《乐府诗集》','《古诗十九首》','《文选》','《玉台新咏》'], ans='D',
                     exp='【原答案卷此题缺失，题目取自题目卷，答案与解析为补充】答案选 D。《孔雀东南飞》原题《古诗为焦仲卿妻作》，首见于南朝陈徐陵编的《玉台新咏》，后被宋代郭茂倩收入《乐府诗集》，与北朝《木兰诗》合称“乐府双璧”。')
        if q['n']==83 and any('缺失' in o for o in q['opts']):
            q.update(q='留下“昔人已乘黄鹤去，此地空余黄鹤楼”名句的是（ ）。', opts=['崔颢','孟浩然','王湾','王维'])
    return qs
from collections import Counter
out=[]
import os
U=os.environ.get('PDF_DIR','pdfs')+'/'
for pdf,name,patch in [(U+'dfc5d655-LDD___7_______-__.pdf','押题卷（七）· 科目一 政策与法律法规 / 科目二 导游业务',False),
                       (U+'65c5c00a-LDD___7_______-__.pdf','押题卷（七）· 科目三 全国导游基础知识 / 科目四 地方导游基础知识',True),
                       (U+'4d1b5971-LDD___8_______-__.pdf','押题卷（八）· 科目一 政策与法律法规 / 科目二 导游业务',False),
                       (U+'f1e5673d-LDD___8_______-__.pdf','押题卷（八）· 科目三 全国导游基础知识 / 科目四 地方导游基础知识',False)]:
    qs=parse(pdf,name,patch)
    bad=[q['n'] for q in qs if not q['ans'] or not q['exp'] or len(q['opts'])<2 or any(ord(c)-65>=len(q['opts']) for c in q['ans']) or (q['type']!='multi' and len(q['ans'])!=1) or (q['type']=='tf' and q['opts']!=['对','错'])]
    miss=[q['n'] for q in qs if any(x in q['q']+''.join(q['opts'])+q['exp'] for x in ['缺失','从略'])]
    print(name, len(qs), Counter(q['type'] for q in qs), 'bad:', bad, 'missing:', miss, file=sys.stderr)
    out.append({'name':name,'qs':qs})
json.dump(out, open('data.json','w'), ensure_ascii=False, separators=(',',':'))
