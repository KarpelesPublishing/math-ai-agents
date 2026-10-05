#!/usr/bin/env python3
"""Build local reading PDFs from workbook sources, with offline equation rendering.

Requires reportlab and markdown. TeX rendering also requires a local Node tree
containing mathjax-full and @resvg/resvg-js. No network calls are made.
"""
from __future__ import annotations
import argparse
from collections import Counter
from functools import partial
from reportlab.pdfgen.canvas import Canvas
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap

import markdown
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted

ROOT=Path(__file__).resolve().parents[1]
BOOK_TITLE='The Mathematics of Artificial Intelligence Agents'
BOOK_SUBTITLE='A Readable Guide to Decisions, Planning, Memory, Tools, Learning, and Cooperation'
INK=colors.HexColor('#263238')
BLUE=colors.HexColor('#31586b')
MUTED=colors.HexColor('#59666b')
LIGHT=colors.HexColor('#eff3f4')
WIDTH=letter[0]-104

NODE_RENDER=r'''
const fs=require('fs'),path=require('path');
const modules=process.argv[2], jobs=JSON.parse(fs.readFileSync(process.argv[3]));
const {mathjax}=require(path.join(modules,'mathjax-full/js/mathjax.js'));
const {TeX}=require(path.join(modules,'mathjax-full/js/input/tex.js'));
const {SVG}=require(path.join(modules,'mathjax-full/js/output/svg.js'));
const {liteAdaptor}=require(path.join(modules,'mathjax-full/js/adaptors/liteAdaptor.js'));
const {RegisterHTMLHandler}=require(path.join(modules,'mathjax-full/js/handlers/html.js'));
const {AllPackages}=require(path.join(modules,'mathjax-full/js/input/tex/AllPackages.js'));
const {Resvg}=require(path.join(modules,'@resvg/resvg-js'));
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const document=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'none'})});
const results={};
for(const job of jobs){
 const node=document.convert(job.tex,{display:false,em:16,ex:8,containerWidth:640});
 const svg=adaptor.firstChild(node);let markup=adaptor.outerHTML(svg);
 if(markup.includes('data-mml-node="merror"'))throw new Error('MathJax error: '+job.tex);
 const vb=adaptor.getAttribute(svg,'viewBox').split(/\s+/).map(Number);
 markup=markup.replace(/currentColor/g,'#263238');
 const width=Math.max(1,Math.ceil(vb[2]/1000*10.5*5));
 const image=new Resvg(markup,{fitTo:{mode:'width',value:width},background:'white'});
 fs.writeFileSync(job.png,image.render().asPng());
 results[job.id]={width_em:vb[2]/1000,height_em:vb[3]/1000,depth_em:Math.max(0,vb[1]+vb[3])/1000};
}
fs.writeFileSync(process.argv[4],JSON.stringify(results));
'''

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class Node:
    def __init__(self,tag='',attrs=None):self.tag=tag;self.attrs=dict(attrs or []);self.children=[]
    def text(self):return ''.join(c if isinstance(c,str) else c.text() for c in self.children)

class Tree(HTMLParser):
    def __init__(self):super().__init__();self.root=Node('root');self.stack=[self.root]
    def handle_starttag(self,tag,attrs):
        n=Node(tag,attrs);self.stack[-1].children.append(n)
        if tag not in ('img','br','hr'):self.stack.append(n)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:self.stack=self.stack[:i];break
    def handle_data(self,data):self.stack[-1].children.append(data)

class ReadingPDF:
    def __init__(self,font_dir,work,node_modules):
        self.work=work;self.node_modules=node_modules;self.equations={};self.rendered={};self.counts=Counter()
        fonts=[('Reader','STIXTwoText-Regular.ttf'),('Reader-Bold','STIXTwoText-Bold.ttf'),('Reader-Italic','STIXTwoText-Italic.ttf'),('Reader-BoldItalic','STIXTwoText-BoldItalic.ttf')]
        if not all((font_dir/f).exists() for _,f in fonts):
            raise FileNotFoundError('Provide --font-dir containing the four STIXTwoText TTF faces. No remote fonts are downloaded.')
        for name,filename in fonts:pdfmetrics.registerFont(TTFont(name,str(font_dir/filename)))
        import matplotlib
        mono = Path(matplotlib.get_data_path()) / 'fonts/ttf/DejaVuSansMono.ttf'
        pdfmetrics.registerFont(TTFont('Reader-Mono', str(mono)))
        pdfmetrics.registerFontFamily('Reader',normal='Reader',bold='Reader-Bold',italic='Reader-Italic',boldItalic='Reader-BoldItalic')
        self.styles={
          'p':ParagraphStyle('Body',fontName='Reader',fontSize=10.5,leading=15,textColor=INK,spaceAfter=8,splitLongWords=True),
          'h1':ParagraphStyle('Title',fontName='Reader-Bold',fontSize=26,leading=30,textColor=BLUE,spaceAfter=17,keepWithNext=True),
          'h2':ParagraphStyle('Section',fontName='Reader-Bold',fontSize=16,leading=20,textColor=BLUE,spaceBefore=16,spaceAfter=9,keepWithNext=True),
          'h3':ParagraphStyle('Subsection',fontName='Reader-Bold',fontSize=12.5,leading=16,textColor=BLUE,spaceBefore=11,spaceAfter=7,keepWithNext=True),
          'cell':ParagraphStyle('TableCell',fontName='Reader',fontSize=9.2,leading=13,textColor=INK,spaceAfter=2,splitLongWords=True),
          'code':ParagraphStyle('Code',fontName='Reader-Mono',fontSize=8,leading=11,textColor=INK,spaceBefore=5,spaceAfter=10),
        }
    def preprocess(self,text):
        # Render only the book's explicit inline TeX tokens; preserve command blocks.
        parts=re.split(r'(```.*?```)',text,flags=re.S)
        for i in range(0,len(parts),2):
            def replace(match):
                tex=match.group(1)
                if '\\' not in tex:return match.group(0)
                key='MATH'+hashlib.sha256(tex.encode()).hexdigest()[:20]
                # Component-set braces in the original Markdown are literal sets,
                # not TeX grouping braces. Keep their visible mathematical meaning.
                render_tex=re.sub(r'(?<!\\)\{(\\theta(?:,[^{}]*)?)\}',r'\\{\1\\}',tex)
                self.equations[key]=render_tex;return f'<span data-equation="{key}"></span>'
            parts[i]=re.sub(r'(?<!`)`([^`\n]+)`(?!`)',replace,parts[i])
            # Generated exercise arithmetic uses literal multiplication stars.
            parts[i]=re.sub(r'(?<=[\w.)\]])\*(?=[\w.(\[-])',r'\\*',parts[i])
        return markdown.markdown(''.join(parts),extensions=['fenced_code','tables','sane_lists'])
    def render_equations(self):
        jobs=[{'id':k,'tex':v,'png':str(self.work/(k+'.png'))} for k,v in self.equations.items()]
        script=self.work/'render.cjs';script.write_text(NODE_RENDER)
        inputs=self.work/'equations.json';inputs.write_text(json.dumps(jobs));outputs=self.work/'dimensions.json'
        subprocess.run(['node',str(script),str(self.node_modules),str(inputs),str(outputs)],check=True,capture_output=True,text=True)
        self.rendered=json.loads(outputs.read_text())
    def inline(self,node,width=WIDTH,fontsize=10.5):
        if isinstance(node,str):return html.escape(node)
        if node.tag=='span' and 'data-equation' in node.attrs:
            k=node.attrs['data-equation'];v=self.rendered[k];w=v['width_em']*fontsize;h=v['height_em']*fontsize;scale=min(1,(width-10)/max(w,1));w*=scale;h*=scale;depth=v['depth_em']*fontsize*scale
            return f'<img src="{self.work/(k+".png")}" width="{w:.3f}" height="{h:.3f}" valign="{-depth:.3f}"/>'
        inner=''.join(self.inline(c,width,fontsize) for c in node.children)
        if node.tag in ('strong','b'):return '<b>'+inner+'</b>'
        if node.tag in ('em','i'):return '<i>'+inner+'</i>'
        if node.tag=='code':return '<font name="Reader-Mono" size="8.8">'+inner+'</font>'
        if node.tag=='br':return '<br/>'
        if node.tag=='a':
            href=node.attrs.get('href','')
            # Manuscript-relative links are reference labels, not bundle links.
            if href.startswith(('https://','http://')):return '<a href="'+html.escape(href,quote=True)+'" color="#31586b">'+inner+'</a>'
            return inner
        return inner
    def paragraph(self,node,style='p',width=WIDTH):return Paragraph(self.inline(node,width,self.styles[style].fontSize),self.styles[style])
    def flows(self,nodes):
        story=[]
        for n in nodes:
            if isinstance(n,str):continue
            if n.tag in ('h1','h2','h3','h4'):
                self.counts[n.tag]+=1;story.append(self.paragraph(n,n.tag if n.tag in self.styles else 'h3'))
            elif n.tag=='p':story.append(self.paragraph(n))
            elif n.tag in ('ul','ol'):
                i=0
                for item in n.children:
                    if isinstance(item,Node) and item.tag=='li':
                        i+=1;prefix=str(i)+'. ' if n.tag=='ol' else '• '
                        story.append(Paragraph(prefix+self.inline(item),self.styles['p']))
            elif n.tag=='pre':
                raw=n.text();wrapped_lines=[]
                for line in raw.splitlines():
                    pieces=textwrap.wrap(line,width=100,replace_whitespace=False,drop_whitespace=False) or ['']
                    # Explicit shell continuation preserves commands when line breaks are copied.
                    shell=line.lstrip().startswith(('python3 ','python ','py '))
                    separator="\\\n" if shell else "\n"
                    wrapped_lines.append(separator.join(pieces))
                story.append(Preformatted("\n".join(wrapped_lines),self.styles['code']))
            elif n.tag=='table':
                rows=[]
                def visit(x):
                    if isinstance(x,str):return
                    if x.tag=='tr':rows.append([c for c in x.children if isinstance(c,Node) and c.tag in ('td','th')])
                    else:
                        for c in x.children:visit(c)
                visit(n)
                cols=max(map(len,rows));weights=[.29,.58,.13] if cols==3 and rows[0][0].text()=='Symbol' else [1/cols]*cols
                widths=[WIDTH*w for w in weights];cells=[[self.paragraph(c,'cell',widths[j]-14) for j,c in enumerate(row)] for row in rows]
                table=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
                table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),LIGHT),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#bac7cc')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d3dde1')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
                story.extend([table,Spacer(1,10)])
            else:story.extend(self.flows(n.children))
        return story
    def build(self,rendered,destination,title,subtitle):
        tree=Tree();tree.feed(rendered);story=self.flows(tree.root.children)
        # Retain source title, then print a restrained author/edition line.
        if story:story.insert(1,Paragraph(html.escape(subtitle),self.styles['p']))
        destination.parent.mkdir(parents=True,exist_ok=True)
        def footer(canvas,doc):
            canvas.saveState();canvas.setStrokeColor(colors.HexColor('#ced8dc'));canvas.line(52,43,letter[0]-52,43);canvas.setFont('Reader',8);canvas.setFillColor(MUTED);canvas.drawString(52,30,BOOK_TITLE.upper()+'  |  '+title.upper());canvas.drawRightString(letter[0]-52,30,str(doc.page));canvas.restoreState()
        temporary_destination=destination.with_suffix('.pdf.tmp')
        doc=SimpleDocTemplate(str(temporary_destination),pagesize=letter,rightMargin=52,leftMargin=52,topMargin=46,bottomMargin=58,title=BOOK_TITLE+': '+title,author='Jason Karpeles',subject=BOOK_SUBTITLE,allowSplitting=True)
        doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=partial(Canvas, initialFontName='Reader'))
        temporary_destination.replace(destination)


def fieldguide():
    entries=json.loads((ROOT/'chapter-map.json').read_text());out=['# Laboratory field guide',BOOK_TITLE,BOOK_SUBTITLE,'## Choose a working route','Start with the mathematical question. The notebooks teach a hand calculation, a changed assumption, and a transfer task. Chapter skills apply the same local Python method to supplied JSON. The master skill chooses compatible chapter methods; a phrase suggestion still needs an assumption check.','## Read first, then execute','The local HTML guide at guide/index.html is immediately readable without Python. PDF pages are reading editions and do not execute their printed results. For a first calculation, run notebooks/00-start-here.ipynb. For the integrated workflow, run notebooks/28-document-release-capstone.ipynb.','## Setup and recovery']
    setup=(ROOT/'START-HERE.md').read_text();out.append(setup[setup.find('\n')+1:])
    out.extend(['## Chapter methods and useful outputs','Each method below uses declared constructed inputs or compatible local reader data. Its result remains conditional on its probability model, data boundary, units, and permission contract.'])
    for e in entries:
        out.extend([f"### {e['chapter']:02d}. {e['title']}",e['outcome'],f"Notebook: `{e['notebook']}`. Skill: `{e['skill']}`.",f"Ask about: {'; '.join(e['routes'])}."])
    out.extend(['## Reliability needs the right evidence','Use Chapter 5 for a declared step or composite-kernel construction, Chapter 17 for uncertain tool consequences, Chapter 16 for candidate and selector allocation, and Chapter 24 for observed run-level outcomes. A marginal step average does not identify a trajectory law. A selected candidate does not prove its effect was authorized or confirmed.','## Read the result boundary','Every report should name the executed method, input contract, evidence kind, assumptions, limitations, and unavailable quantities. A constructed example teaches what a model implies; it does not measure deployed-agent performance. Human usability testing, operating-system launch acceptance, and assistant discovery are different checks from mathematical execution.'])
    return '\n\n'.join(out)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--font-dir',type=Path,default=ROOT.parent/'tmp/proofs/fonts');parser.add_argument('--node-modules',type=Path,default=ROOT.parent/'tmp/proofs/tooling/node_modules');parser.add_argument('--receipt-dir',type=Path,default=ROOT.parent/'QA/companion-completion');args=parser.parse_args()
    sources=[ROOT/'workbook/workbook.md',ROOT/'workbook/solutions.md',ROOT/'workbook/notation-guide.md']
    with tempfile.TemporaryDirectory(prefix='maa-reading-pdfs-') as tmp:
        pdf=ReadingPDF(args.font_dir,Path(tmp),args.node_modules.resolve());texts=[p.read_text() for p in sources]+[fieldguide()];rendered=[pdf.preprocess(t) for t in texts];pdf.render_equations();outputs=[p.with_suffix('.pdf') for p in sources]+[ROOT/'guide/field-guide.pdf'];titles=['Laboratory workbook','Separate solutions','Notation guide','Laboratory field guide']
        for text,dest,title in zip(rendered,outputs,titles):pdf.build(text,dest,title,'Jason Karpeles | Constructed exercises and conditional calculations')
        question_count = sum(len(json.loads(path.read_text())['exercises'])
                             for path in (ROOT/'content').glob('ch??.json'))
        demonstration_count = sum(len(entry.get('demonstrations', [])) for entry in json.loads((ROOT/'chapter-map.json').read_text()))
        receipt={'status':'built','offline':True,'equation_renderer':'Local MathJax SVG glyph paths, rasterized at five pixels per point for PDF inline placement','unique_equations_rendered':len(pdf.equations),'code_sha256':digest(Path(__file__)), 'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sources+[ROOT/'START-HERE.md',ROOT/'chapter-map.json']},'output_sha256':{str(p.relative_to(ROOT)):digest(p) for p in outputs},'exercise_inventory':{'original_questions':23,'new_questions':question_count,'demonstration_questions_with_answers':demonstration_count,'answers':'Separate solutions PDF'},'limitations':['Inline equation images retain visual notation but are not searchable mathematical text.','PDF pages do not execute notebooks.','Fresh builds need declared local rendering dependencies and fonts; they make no network calls.']}
        args.receipt_dir.mkdir(parents=True,exist_ok=True);(args.receipt_dir/'pdf-build.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'pdfs':[str(p.relative_to(ROOT)) for p in outputs],'unique_equations':len(pdf.equations)}))

if __name__=='__main__':main()
