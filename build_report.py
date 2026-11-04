"""Rebuild the SKEPTIC-1 concept report after running model.py."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter

ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'results/results.json').read_text())
for name,file in [('Body','DejaVuSerif.ttf'),('Sans','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
NAVY=colors.HexColor('#153B50');TEAL=colors.HexColor('#16778B');MUTED=colors.HexColor('#50616B')
S={
 'title':ParagraphStyle('Title',fontName='Bold',fontSize=34,leading=40,textColor=NAVY,spaceAfter=12),
 'lead':ParagraphStyle('Lead',fontName='Sans',fontSize=16,leading=22,textColor=TEAL,spaceAfter=14),
 'h':ParagraphStyle('H',fontName='Bold',fontSize=14,leading=18,textColor=NAVY,spaceAfter=10,keepWithNext=True),
 'sub':ParagraphStyle('Sub',fontName='Bold',fontSize=10.7,leading=14,textColor=NAVY,spaceBefore=8,spaceAfter=5,keepWithNext=True),
 'body':ParagraphStyle('Body',fontName='Body',fontSize=10.2,leading=14.2,spaceAfter=8,textColor=colors.HexColor('#1D2B35'),allowWidows=0,allowOrphans=0),
 'small':ParagraphStyle('Small',fontName='Sans',fontSize=8.5,leading=11.5,textColor=MUTED,spaceAfter=7),
 'cell':ParagraphStyle('Cell',fontName='Sans',fontSize=9.0,leading=12,textColor=NAVY),
 'eq':ParagraphStyle('Equation',fontName='Mono',fontSize=9.1,leading=13.5,textColor=NAVY,backColor=colors.HexColor('#EDF4F6'),borderPadding=8,spaceBefore=6,spaceAfter=12),
}
story=[]
def p(t,style='body'):story.append(Paragraph(t,S[style]))
def h(t):p(t,'h')
def sub(t):p(t,'sub')
def page():story.append(PageBreak())
def eq(t):story.append(Preformatted(t,S['eq']))
def fig(name,w=500,h=190):story.append(Image(str(ROOT/'figures'/name),width=w,height=h));story.append(Spacer(1,7))
def table(rows,widths):
    cells=[[Paragraph(escape(str(x)),S['cell']) for x in row]for row in rows]
    t=Table(cells,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DCECF1')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F7F8')]),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.6,TEAL)]))
    story.append(t);story.append(Spacer(1,10))

p('SKEPTIC-1','title')
p('Matter that asks a second question.','lead')
p('CONCEPT STUDY v0.1  |  NOVEMBER 4, 2026  |  UNBUILT','small')
p('A proposed reconfigurable diagnostic instrument that changes a small, measured part of its stiffness when an initial vibration measurement cannot distinguish competing explanations. It then measures again and checks whether the original state returns.')
p('The intended output is a traceable finding: <b>separated within the tested model</b>, <b>still ambiguous</b>, or <b>the calibrated model does not explain the data</b>. These output rules are design requirements; a validated decision system has not been implemented.')
fig('architecture.png',505,145)
sub('The concrete idea')
p('Different defects can produce the same resonant frequencies. Repeating that same incomplete measurement can produce more precise ambiguity. SKEPTIC-1 instead selects a reversible physical probe, records the intervention it actually achieved, and asks whether the competing explanations still predict the same result.')
sub('What was established in this work')
p('In the supplied ideal model, left- and right-end spring losses give exactly equal spectra. Adding a known 500 N/m brace to the left mass separates their first frequencies by <b>0.402029 Hz</b>. A symmetric center brace remains ambiguous. No hardware performance has been measured.')
p('AI-led design and numerical study by Asteris Solenne / ChatGPT, requested by Anubis without further design input. AI-assisted outside review. This is a new design presentation built on established methods, not a claim of unprecedented physics or established patent novelty.','small')

page();h('1 / The physical instrument')
table([
 ['Module','Proposed function'],
 ['Test body','Three nominal 100 g proof masses; four nominal 1000 N/m spring cartridges between fixed supports. One axial degree of freedom per mass in the reduced model.'],
 ['Probe cartridge','A grounded auxiliary spring acting on mass 1, with proposed 0 / 250 / 500 N/m settings. Achieved stiffness must be measured independently, not inferred from the command.'],
 ['Readout and excitation','Non-contact optical motion tracking and a low-amplitude exciter. Frequency uncertainty, clock error and mode assignment require bench calibration.'],
 ['Intervention monitor','Records actual stiffness, motion, time ordering, excitation amplitude and return to the original condition.'],
 ['Inference and report','Keeps competing explanations and nuisance ranges; selects admissible tests; reports alternatives, residuals, calibration and unresolved cases. This controller is proposed, not demonstrated.'],
 ],[108,397])
sub('One diagnostic round: A0 / B / A0')
p('<b>A0:</b> Measure the original body, estimate uncertainty, and retain all explanations that fit the calibrated observations. A declaration of ignorance is a valid result.')
p('<b>B:</b> Choose a reversible probe intended to distinguish those explanations. Independently verify the achieved brace stiffness; measure again with matched sensing and excitation resources.')
p('<b>A0 return:</b> Remove the probe and repeat the original measurement. A failure to return within an empirically calibrated band invalidates the comparison and requires investigation of drift, slip, or probe-induced change.')
sub('Actuation envelope is a bench requirement, not a proven limit')
p('At an assumed 0.2 mm displacement, a 500 N/m auxiliary spring carries 0.10 N and stores 10 microjoules. Those numbers describe only that ideal spring at that displacement. They exclude drive, actuator switching, optical sensing, electronics and computation. Mechanical travel limits and a hardware stop are required before trials. The apparatus is a small unloaded research specimen, not a diagnostic attachment for an occupied structure.')

page();h('2 / The reproducible numerical example')
eq('(K(dL, dR, alpha) + Kq(a)) v = omega^2 M v\nf = omega / (2 pi)\nKq(a) = a e1 e1^T ;  M = 0.1 I kg')
p('The unbraced matrix has diagonal entries [k1+k2, k2+k3, k3+k4] and adjacent off-diagonal entries [-k2, -k3]. Here ki = 1000 alpha N/m, except k1 is multiplied by (1-dL) and k4 by (1-dR). The auxiliary brace a is separate from alpha.')
table([
 ['Ideal case','f1 (Hz)','f2 (Hz)','f3 (Hz)'],
 ['Left-end 25% loss, unbraced','11.431407','21.798818','29.165501'],
 ['Right-end 25% loss, unbraced','11.431407','21.798818','29.165501'],
 ['Left-end loss + 500 N/m probe','12.750897','23.195330','29.707487'],
 ['Right-end loss + 500 N/m probe','12.348868','23.155770','29.907512'],
 ],[215,97,97,96])
fig('spectral_ambiguity.png',505,182)
p('Reflection maps one unbraced fault to the other: K_R = P K_L P^T and M = P M P^T, so their eigenvalues agree. The off-center brace breaks that reflection relationship. This is a conditional mathematical example, not a measured damage-detection result.','small')

page();h('3 / What becomes observable')
fig('local_rank.png',505,190)
p('At the healthy nominal point, the frequency sensitivity S = df/d[dL,dR,alpha] has rank 2. Stacking baseline and 500 N/m probe data gives rank 3, with singular values 27.7824, 4.18801 and 0.923383 Hz per unit dimensionless parameter. Analytic derivatives agreed with central finite differences. This is <b>local observability of this three-parameter model</b>; it is not global identifiability of arbitrary defects.')
sub('An exploratory nuisance search')
p('Allowing the wrong-side explanation to vary its loss from 0 to 40%, the uniform stiffness scale alpha from 0.90 to 1.10, and probe calibration by +/-3%, a multistart local fit at the 500 N/m probe leaves an RMS frequency residual of 0.123362 Hz. Without a probe, the wrong-side hypothesis fits exactly. The local search is not a certified global lower bound or a statistical exclusion.')
sub('Limits that matter')
p('Uniform alpha is an abstract stiffness nuisance, not a validated temperature model. Damping, friction, fixture mass, mode swaps, spring nonlinearity and optical readout physics are omitted. The illustrative 0.02 Hz frequency noise is not demonstrated instrument precision. No accuracy, confidence level, false-alarm rate or safety assurance follows from these calculations.')
sub('Controls already checked in the numerical study')
p('The unbraced reflection identity, healthy closed-form eigenfrequencies, analytic/finite-difference sensitivities and rank change were checked. A 500 N/m brace applied symmetrically at the center leaves the mirror ambiguity intact. A commanded but absent probe and a 1% return-state stiffness drift were also simulated as calibration challenges; no validated rejection rule is claimed.')

page();h('4 / What would make this worth building')
sub('Prior work changes the claim')
p('Artificial boundary-condition methods already improve structural identification, including symmetry-related rank deficiencies [1]. Known added stiffness and semi-active dampers also have a long history in health monitoring [2]. Environmental changes can imitate or obscure mechanical changes [3]. The underlying principles are established. A search does not establish novelty of the complete instrument.')
sub('The candidate research question')
p('<b>Does calibration-gated probe selection with a verified A0/B/A0 return and explicit ambiguity reporting reduce false separations at matched time and resources?</b> That is the proposed engineering question. The current model does not answer it.')
table([
 ['Required comparison','What it challenges'],
 ['Repeat the original measurement','Whether more time alone provides the same benefit.'],
 ['Random probe / fixed best probe','Whether adaptive selection adds value over a simple predetermined action.'],
 ['Richer passive sensing','Whether mode shapes or full frequency responses resolve the ambiguity without intervention.'],
 ['Known defects + injected mismatch','Whether slip, mass offsets, friction or loose supports create confident wrong answers.'],
 ],[167,338])
sub('Go / stop gates before expansion')
p('First measure repeatability and the complete error budget. Then verify probe stiffness and reversible return across repeated cycles. Lock a scoring rule, nuisance ranges and acceptance criteria before collecting evaluation data. Test held-out defects and deliberate model mismatch. Stop expansion if simpler methods match performance or if confidently wrong reports exceed the agreed limit.')
p('If no admissible probe separates the remaining explanations, retain the ambiguity. If all tested explanations fail the calibrated observations, report that failure without claiming every possible model has been ruled out.')
sub('AI-assisted outside review')
p('Outside reviews supported the ideal frequency example but challenged novelty, unmeasured precision, local-rank interpretation and the unvalidated third verdict. Those limits are retained. Assertions that real hardware would necessarily destroy the signal were treated as risks to test, not established facts. AI agreement is not human peer review or validation.')

page();h('5 / Reproduce and extend')
p('The research pack contains model.py, this report builder, numerical JSON/CSV results and scientific figures. Run the model before rebuilding the report:','small')
eq('python model.py\npython build_report.py')
p('Python dependencies: NumPy, SciPy, Matplotlib and ReportLab. The report builder uses DejaVu fonts at a standard Linux font path; adjust that path if needed. The simulation has no random draws. Its profile fits are numerical local optimizations and should not be mistaken for rigorous interval bounds.')
sub('What is designed, simulated, and still missing')
table([
 ['Stage','Status'],
 ['Instrument architecture and test protocol','Proposed; no physical apparatus constructed.'],
 ['Reduced-model example and local sensitivity','Calculated and supplied for reproduction.'],
 ['Adaptive policy and three-way decision rule','Not implemented or validated; thresholds and scoring require a locked protocol.'],
 ['Hardware uncertainty and performance','Unmeasured; no component sourcing, construction quotes or feasibility guarantee.'],
 ['Scientific or patent novelty','Not established; close predecessors explicitly identified.'],
 ],[204,301])
sub('References')
p('[1] J. H. Gordis, J.-C. Shin and M. D. Bouwense (2018). Minimum condition number by orthogonal projection row selection of artificial boundary conditions for finite element model update and damage detection. Journal of Sound and Vibration 433, 179-197. DOI: 10.1016/j.jsv.2018.07.006.','small')
p('<link href="https://calhoun.nps.edu/bitstreams/72103372-5087-4d2a-88d1-9f10b84e0da4/download" color="#16778B">Author/institutional manuscript</link>','small')
p('[2] Integrated vibration control and health monitoring of building structures using semi-active friction dampers: Part I - methodology. Engineering Structures (publisher abstract inspected; full text not reviewed).','small')
p('<link href="https://www.sciencedirect.com/science/article/pii/S014102960700452X" color="#16778B">Publisher record</link>','small')
p('[3] Meteorological Controls on Reversible Resonance Changes in Natural Rock Arches (2022). Journal of Geophysical Research: Earth Surface. DOI: 10.1029/2022JF006734.','small')
p('<link href="https://doi.org/10.1029/2022JF006734" color="#16778B">Research article</link>','small')
p('Prepared November 4, 2026. No results from a physical experiment, commitments from collaborators, external endorsements or world-first claims are represented.','small')

def footer(c,doc):
    c.saveState();c.setStrokeColor(colors.HexColor('#D7E2E6'));c.line(48,41,564,41)
    c.setFont('Helvetica',8);c.setFillColor(MUTED);c.drawRightString(564,27,f'Page {doc.page}');c.restoreState()

dest=ROOT/'SKEPTIC-1-Concept-and-Model-v0.1.pdf'
doc=SimpleDocTemplate(str(dest),pagesize=letter,leftMargin=48,rightMargin=48,topMargin=48,bottomMargin=56,
 title='SKEPTIC-1 - Matter that asks a second question',author='Asteris Solenne / ChatGPT; requested by Anubis',
 subject='Proposed diagnostic instrument with ideal-model calculations; unbuilt; novelty not established',pageCompression=1)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(dest)
