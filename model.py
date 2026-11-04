"""SKEPTIC-1 v0.1: ideal three-mass structural-identification study.

No hardware data. No universal fault-detection or novelty claim.
Run: python model.py. Requires numpy, scipy, matplotlib.
"""
from pathlib import Path
import csv, json
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'; FIG=ROOT/'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
MASS=.1
K0=1000.

def matrices(dl=0.,dr=0.,alpha=1.,brace=0.,beta=1.,mass_scales=None):
    springs=K0*alpha*np.array([1-dl,1.,1.,1-dr])
    K=np.diag([springs[0]+springs[1],springs[1]+springs[2],springs[2]+springs[3]])
    K+=np.diag([-springs[1],-springs[2]],1)+np.diag([-springs[1],-springs[2]],-1)
    K[0,0]+=brace*beta
    M=np.eye(3)*MASS if mass_scales is None else np.diag(np.asarray(mass_scales)*MASS)
    return K,M

def spectrum(dl=0.,dr=0.,alpha=1.,brace=0.,beta=1.,mass_scales=None):
    vals=eigh(*matrices(dl,dr,alpha,brace,beta,mass_scales),eigvals_only=True)
    if np.any(vals<=0): raise ValueError('Non-positive ideal stiffness spectrum')
    return np.sqrt(vals)/(2*np.pi)

def analytic_sensitivity(brace):
    K,M=matrices(brace=brace)
    vals,V=eigh(K,M)
    f=np.sqrt(vals)/(2*np.pi)
    dK_l=np.diag([-K0,0.,0.]); dK_r=np.diag([0.,0.,-K0])
    dK_a=matrices()[0]
    return np.column_stack([np.einsum('ij,ij->j',V,A@V)/(8*np.pi**2*f) for A in [dK_l,dK_r,dK_a]])

def numeric_sensitivity(brace,eps=1e-5):
    x=np.array([0.,0.,1.]); D=np.eye(3)*eps
    return np.column_stack([(spectrum(*(x+D[j]),brace=brace)-spectrum(*(x-D[j]),brace=brace))/(2*eps) for j in range(3)])

def combined(dl,dr,alpha,brace,beta=1.,mass_scales=None):
    return np.r_[spectrum(dl,dr,alpha,mass_scales=mass_scales),spectrum(dl,dr,alpha,brace,beta,mass_scales)]

def wrong_fit(observed,brace):
    """Multistart LOCAL profile fit: not a certified global lower bound.

    Alternate hypothesis is right-end stiffness loss, with nuisance scale and
    +/-3% brace calibration factor. Bounds are illustrative, not empirical.
    """
    best=None
    for d in [0.,.1,.25,.4]:
        for a in [.9,1.,1.1]:
            res=least_squares(lambda x:combined(0.,x[0],x[1],brace,x[2])-observed,
                [d,a,1.],bounds=([0.,.9,.97],[.4,1.1,1.03]),
                xtol=1e-11,ftol=1e-11,gtol=1e-11)
            if best is None or res.cost<best.cost: best=res
    return {'d_right':float(best.x[0]),'alpha':float(best.x[1]),'brace_factor':float(best.x[2]),
            'rms_residual_Hz':float(np.sqrt(np.mean(best.fun**2))),
            'max_absolute_residual_Hz':float(np.max(abs(best.fun)))}

def save(fig,name):
    fig.savefig(FIG/(name+'.png'),dpi=180,bbox_inches='tight')
    fig.savefig(FIG/(name+'.svg'),bbox_inches='tight')
    plt.close(fig)

def main():
    baseline=spectrum(.25,0.)
    mirror=spectrum(0.,.25)
    P=np.eye(3)[::-1]
    KL,ML=matrices(.25,0.);KR,MR=matrices(0.,.25)
    mirror_matrix_error=float(np.max(abs(KR-P@KL@P.T)))
    assert mirror_matrix_error<1e-12
    assert np.allclose(baseline,mirror,rtol=1e-12,atol=1e-12)
    # Independent closed-form healthy equal-chain eigenvalues.
    exact=np.sqrt((K0/MASS)*(2-2*np.cos(np.arange(1,4)*np.pi/4)))/(2*np.pi)
    assert np.allclose(exact,spectrum(),atol=1e-12)
    for b in [0.,250.,500.,1000.]:
        assert np.allclose(analytic_sensitivity(b),numeric_sensitivity(b),rtol=2e-7,atol=1e-7)
    S0=analytic_sensitivity(0.)
    S1=np.vstack([S0,analytic_sensitivity(500.)])
    singular0=np.linalg.svd(S0,compute_uv=False)
    singular1=np.linalg.svd(S1,compute_uv=False)
    assert np.linalg.matrix_rank(S0,tol=1e-8)==2
    assert np.linalg.matrix_rank(S1,tol=1e-8)==3
    # Negative control: a symmetric center brace cannot distinguish reflections.
    def center_brace(dl,dr):
        K,M=matrices(dl,dr);K[1,1]+=500.
        return np.sqrt(eigh(K,M,eigvals_only=True))/(2*np.pi)
    assert np.allclose(center_brace(.25,0.),center_brace(0.,.25),atol=1e-12)
    a=np.linspace(0,1000,81)
    gaps=np.array([np.linalg.norm(spectrum(.25,0.,brace=b)-spectrum(0.,.25,brace=b)) for b in a])
    rows=[]
    for b in [0.,100.,250.,500.,1000.]:
        left=spectrum(.25,0.,brace=b);right=spectrum(0.,.25,brace=b)
        rows.append({'brace_N_per_m':b,'left_Hz':left.tolist(),'right_Hz':right.tolist(),
                     'raw_three_mode_distance_Hz':float(np.linalg.norm(left-right)),
                     'wrong_hypothesis_local_profile':wrong_fit(combined(.25,0.,1.,b),b)})
    # Calibration failures are observable only if achieved intervention is checked.
    nominal=combined(.25,0.,1.,500.)
    failed_brace=combined(.25,0.,1.,0.)
    return_drift=np.max(abs(spectrum(.25,0.)-spectrum(.25,0.,alpha=.99)))
    result={'status':'Ideal-model calculations only; no hardware results',
        'model':{'masses_kg':[MASS]*3,'nominal_springs_N_per_m':[K0]*4,
          'demonstration_end_spring_loss_fraction':.25,'brace_N_per_m':500.,
          'illustrative_frequency_noise_sigma_Hz':.02,
          'profile_fit_nuisance_bounds':{'d_right':[0.,.4],'alpha':[.9,1.1],'brace_factor':[.97,1.03]}},
        'baseline_left_Hz':baseline.tolist(),'baseline_right_Hz':mirror.tolist(),
        'symmetric_center_probe_left_Hz':center_brace(.25,0.).tolist(),
        'symmetric_center_probe_right_Hz':center_brace(0.,.25).tolist(),
        'local_sensitivity_units':'Hz per unit dimensionless dl, dr, alpha, evaluated at healthy nominal point',
        'local_singular_values_baseline':singular0.tolist(),'local_singular_values_combined':singular1.tolist(),
        'rank_baseline':2,'rank_combined':3,'brace_sweep':rows,
        'checks':{'reflection_matrix_error':mirror_matrix_error,'healthy_closed_form':'passed',
          'analytic_vs_finite_difference_sensitivity':'passed','center_probe_remains_ambiguous':'passed',
          'failed_brace_change_vector_max_Hz':float(np.max(abs(nominal-failed_brace))),
          'return_drift_uniform_stiffness_minus1pct_max_Hz':float(return_drift)},
        'added_brace_only_at_0p2mm':{'force_N':500*.0002,'stored_energy_J':.5*500*.0002**2},
        'limits':['Ranks are local to a chosen three-parameter ideal model.',
          'Wrong-hypothesis fits are local multistart numerical searches, not global exclusion certificates.',
          'Uniform stiffness scale is not a validated model of temperature or humidity.',
          'No damping, friction, fixture mass, mode-matching failure, actuator hysteresis or sensor error physics.',
          'Frequency noise is illustrative; no demonstrated hardware precision or sampling model.',
          'No statistical detection rate, false-alarm guarantee or structural safety certification.']}
    (OUT/'results.json').write_text(json.dumps(result,indent=2))
    with (OUT/'spectra.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['brace_N_per_m','location','f1_Hz','f2_Hz','f3_Hz'])
        for r in rows:
            for name,key in [('left','left_Hz'),('right','right_Hz')]: w.writerow([r['brace_N_per_m'],name,*r[key]])
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans'})
    from matplotlib.patches import Rectangle, FancyArrowPatch
    fig,ax=plt.subplots(figsize=(9.5,2.6))
    def spring(x0,x1,y):
        xx=np.linspace(x0,x1,19); yy=np.full(19,y); yy[1:-1]+=np.array([.09,-.09]*8+[.09])
        ax.plot(xx,yy,color='#294B5C',lw=1.8)
    ax.add_patch(Rectangle((0,.65),.15,.7,color='#294B5C'))
    ax.add_patch(Rectangle((5.85,.65),.15,.7,color='#294B5C'))
    for x in [1.2,3.,4.8]:
        ax.add_patch(Rectangle((x-.3,.78),.6,.44,facecolor='#DAEAF0',edgecolor='#126C86',lw=1.5))
        ax.text(x,1.,'0.1 kg',ha='center',va='center',fontsize=9)
    for i,(l,r) in enumerate([(.15,.9),(1.5,2.7),(3.3,4.5),(5.1,5.85)]):
        spring(l,r,1.);ax.text((l+r)/2,1.4,f'k{i+1}',ha='center',fontsize=10)
    ax.plot([1.2,1.2],[.78,.4],color='#D28725',lw=3)
    ax.plot([.75,1.65],[.4,.4],color='#D28725',lw=3)
    ax.text(1.2,.15,'Known probe to ground',ha='center',fontsize=9,color='#A26013')
    ax.text(3.,.15,'A0  /  B  /  A0 return check',ha='center',fontsize=10)
    ax.text(3.,1.75,'Reduced model: three masses, four springs, one reversible probe',ha='center',fontweight='bold')
    ax.set(xlim=(-.15,6.15),ylim=(0,2.));ax.axis('off');fig.tight_layout();save(fig,'architecture')
    fig,ax=plt.subplots(1,2,figsize=(9.7,3.5),sharey=True)
    for axis,b,title in zip(ax,[0.,500.],['Unbraced: reflection ambiguity','Left probe: symmetry broken']):
        for dl,dr,label,color,marker,offset in [(.25,0.,'Left-end loss','#126C86','o',-.05),(0.,.25,'Right-end loss','#D28725','x',.05)]:
            axis.plot(np.arange(1,4)+offset,spectrum(dl,dr,brace=b),marker=marker,color=color,linestyle='none',markersize=8,label=label)
        axis.set(title=title,xlabel='Ordered mode',xticks=[1,2,3]);axis.grid(alpha=.2)
    ax[0].set_ylabel('Ideal eigenfrequency (Hz)');ax[1].legend(loc='lower right',fontsize=9)
    fig.suptitle('Same first spectrum; a different physical question',fontweight='bold')
    fig.tight_layout();save(fig,'spectral_ambiguity')
    fig,ax=plt.subplots(figsize=(8.7,3.4));ax.plot(a,gaps,color='#126C86',lw=2)
    ax.scatter([250,500],[gaps[20],gaps[40]],color='#D28725',zorder=5)
    ax.set(xlabel='Known auxiliary left brace stiffness (N/m)',ylabel='Three-mode distance (Hz)',title='Illustrative pair separation, fixed 25% loss and scale')
    ax.grid(alpha=.2);fig.tight_layout();save(fig,'probe_sweep')
    fig,ax=plt.subplots(figsize=(8.7,3.4));xx=np.arange(3)
    ax.bar(xx-.17,singular0,width=.34,label='Baseline',color='#126C86');ax.bar(xx+.17,singular1,width=.34,label='Baseline + 500 N/m probe',color='#D28725')
    ax.set(xticks=xx,xticklabels=['Direction 1','Direction 2','Direction 3'],ylabel='Singular value (Hz/unit)',title='Local sensitivity: one invisible direction becomes observable')
    ax.legend(fontsize=9);ax.grid(axis='y',alpha=.2);fig.tight_layout();save(fig,'local_rank')
    print(json.dumps({'baseline_Hz':baseline.tolist(),'probed_left_Hz':rows[3]['left_Hz'],
       'probed_right_Hz':rows[3]['right_Hz'],'ranks':[2,3],'local_singular_values_combined':singular1.tolist(),
       'wrong_fit_500':rows[3]['wrong_hypothesis_local_profile'],'checks':result['checks']},indent=2))

if __name__=='__main__':main()
