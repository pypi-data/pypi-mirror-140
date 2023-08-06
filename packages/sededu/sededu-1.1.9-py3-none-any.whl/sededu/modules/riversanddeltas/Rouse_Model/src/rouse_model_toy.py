# interactive Rouse Profile toy run_model

# import liblaries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widget
from mpl_toolkits.axes_grid1 import make_axes_locatable
import utils

# set parameters
H = Z = 5
nz = 100-1
dz = Z / nz
z = np.array(np.linspace(Z*0.05, Z, nz+1))
kappa = 0.41

# some constants
rop = 2650.0 # density of particle in kg/m3
rof = 1000.0 # density of water in kg/m3
nu = 1.002*1E-6 # dynamic viscosity in Pa*s at 20 C
C1 = 18 # constant in Ferguson-Church equation
C2 = 1 # constant in Ferguson-Church equation
R = (rop-rof)/rof
g = 9.81

gsInit = 300
gs = gsInit * 1e-6
gsMax = 2000
gsMin = 5

ustarInit = 30
ustar = ustarInit * 1e-2
ustarMax = 75
ustarMin = 25

TaubInit = .7
Taub = TaubInit
TaubMax = 2.25
TaubMin = 0.25

Taucrit_cohInit = .3
Taucrit_coh = Taucrit_cohInit
TaucritMax = 0.5
TaucritMin = 0.03
por = 0.35
cf = .004

# define functions
def calculate_refheight(H):
    return H * 0.05


#def calculate_refconc(_gs, _ws, _ustar):
    #'''
    #'''
    #_Rep = (np.sqrt(R*g*_gs)*_gs)/nu
    #_X = (_ustar/_ws)*(_Rep**0.6)
    #_A = 1.3e-7
    #_Es = (_A*(_X**5)) / ( 1 + ((_A/0.3)*(_X**5)) )
    #return _Es

def get_criticalstress(_gs):
    _Rep = (np.sqrt(R*g*_gs)*_gs)/nu
    if _Rep <= 6.61:
        _thetcrit = 0.1414 * _Rep**(-0.2306)
        _Taucrit = _thetcrit * ((rop - rof) * g) * gs;
    elif _Rep > 6.61 and _Rep < 282.84:
        _tc1 = (1 + ((0.0223 * _Rep)**(2.8358)))**(0.3542)
        _tc2 = (3.0946 * _Rep**(0.6769))
        _thetcrit = _tc1/_tc2
        _Taucrit = _thetcrit * ((rop - rof) * g) * gs;
    #elif _Rep>= 282.84
    else:
        _thetcrit = 0.045
        _Taucrit = _thetcrit * ((rop - rof) * g) * gs;
    #print("Taucrit =",_Taucrit)
    return _Taucrit

def calculate_refconc(Taucrit,por,Taub):
    '''
    '''
    # _Taub = cf*rof*(_ustar**2)
    #print("Taub=",_Taub)
    _Tstar = Taub/Taucrit;
    _E = _Tstar-1
    if _Tstar <= 1:
        _Es = 0
    else:
        _Es = (0.004*(1-por)*_E)/(1+(0.004*_E))
    return _Es

def calculate_refconc_coh(Taucrit_coh,por,Taub):
    '''
    '''
    # _Taub = cf*rof*(_ustar**2)
    _Tstar = Taub/Taucrit_coh;
    _E = _Tstar-1
    if _Tstar <= 1:
        _Es_coh = 0
    else:
        _Es_coh = (0.004*(1-por)*_E)/(1+(0.004*_E))
    if _Es_coh > 0.3:
        _Es_coh = 0.3
    else:
        _Es_coh = _Es_coh
    return _Es_coh

def calculate_setting(_gs):
    '''
    take from Zoltan Sylvester's blog at Hindered Settling:
    https://hinderedsettling.com/2013/08/09/grain-settling-python/
    '''
    d = _gs
    w = ((R*9.81*d**2)/(C1*nu/rof + (0.75*C2*R*9.81*d**3)**0.5))

    return w


def calculate_rousenum(Taub, _ws):
    _ustar = (Taub/(cf*rof))**(1/2)
    return _ws / (kappa * _ustar), _ustar


# def nondim_profile(z, c):
#     '''
#     nondimensionalize the profile by the flow depth and the near bed conc
#     '''
#     zstar = z / np.max(Z)
#     cstar = c / np.max(c)
#
#     return zstar, cstar


def calculate_profile_simp(z, H, _epsza, _P):
    '''
    Rousean profile for a given Rouse number:
        z        = elevations above bed to evaluate eps
        H        = flow depth
        _eps     = volumetric concentration
        _Z       = max elevation
        _epsza   = reference concentration
        _P       = Rouse number
    '''
    _Z = np.max(z)
    _eps = np.zeros(z.size)
    _za = np.min(z)
    for i, _z in enumerate(z):
        # VERSION GIVEN IN NOTES
        _eps[i] = _epsza * ( (_za) / _z ) ** _P

        # VERSION GIVEN IN HOMEWORK
        # _eps[i] = _epsza * ( ((H-_z)/_z) * (_za/(H-_za)) ) ** _P

    return _eps


def calculate_profile_full(z, H, _epsza, _P):
    '''
    Rousean profile for a given Rouse number:
        z        = elevations above bed to evaluate eps
        H        = flow depth
        _eps     = volumetric concentration
        _Z       = max elevation
        _epsza   = reference concentration
        _P       = Rouse number
    '''
    _Z = np.max(z)
    _eps = np.zeros(z.size)
    b = np.min(z)
    for i, _z in enumerate(z):
        _eps[i] = _epsza * ( ((H-_z)/_z) / ((H-b)/b) ) ** _P

    return _eps

def calculate_profile_full_coh(z, H, _epsza_coh, _P):
    '''
    Rousean profile for a given Rouse number:
        z        = elevations above bed to evaluate eps
        H        = flow depth
        _eps     = volumetric concentration
        _Z       = max elevation
        _epsza   = reference concentration
        _P       = Rouse number
    '''
    _Z = np.max(z)
    _eps = np.zeros(z.size)
    b = np.min(z)
    for i, _z in enumerate(z):
            _eps[i] = _epsza_coh * ( ((H-_z)/_z) / ((H-b)/b) ) ** _P

    return _eps


def run_model(event):
    '''
    the core model run method
    '''

    # read values from the sliders
    _gs = slide_gs.val * 1e-6
    # _ustar = slide_ustar.val * 1e-2
    Taub = slide_taub.val
    Taucrit_coh = slide_taucrit.val


    # compute
    _ws = calculate_setting(_gs)
    _P,_ustar = calculate_rousenum(Taub, _ws)
    #print("IN:", _gs, _ws, _ustar)
    _Taucrit = get_criticalstress(_gs);
    _epsza = calculate_refconc(_Taucrit,por,Taub)
    _eps_dim_mood = calculate_profile_full(z, H, _epsza, _P)
    _epsza_coh = calculate_refconc_coh(Taucrit_coh,por,Taub)
    _eps_dim_carl = calculate_profile_full_coh(z, H, _epsza_coh, _P)
    #print("MOOD: ", _epsza, _eps_dim_mood[0])
    #print("CARL: ", _epsza_coh, _eps_dim_carl[0])
    # _z_nondim_carl, _eps_nondim_carl = nondim_profile(z, _eps_dim_carl)
    # _z_nondim_mood, _eps_nondim_mood = nondim_profile(z, _eps_dim_mood)
    _eps_max = np.max(_eps_dim_carl)

    # update the plots
    Zd_line.set_xdata([0, 10**-1])
    carl_dim_line.set_data(_eps_dim_carl, z)
    mood_dim_line.set_data(_eps_dim_mood, z)
    # carl_nondim_line.set_data(_eps_nondim_carl, _z_nondim_carl)
    # mood_nondim_line.set_data(_eps_nondim_mood, _z_nondim_mood)
    info_text.set_text(numformat(_ws/_ustar, _P))

    ax_dim.relim()
    ax_dim.autoscale_view()
    fig.canvas.draw_idle()


def reset(event):
    '''
    reset buttons
    '''
    slide_gs.reset()
    #slide_ustar.reset()
    slide_taub.reset()
    slide_taucrit.reset()
    run_model(event)
    fig.canvas.draw_idle()


def numformat(wsus, rouse):
    '''
    format numbers for the text label
    '''
    return '$w_s/u_* = ${:.3f}\n $P$ = {:.3f}'.format(wsus, rouse)


# run the program once with the initial values
ws = calculate_setting(gs)
P,_ustar = calculate_rousenum(Taub, ws)
#print("ws=",ws,"_ustar=",_ustar)
Taucrit = get_criticalstress(gs);
#print("_Taucrit=",_Taucrit)
epsza = calculate_refconc(Taucrit,por,Taub)
#print("epsza=",epsza)
epsza_coh = calculate_refconc_coh(Taucrit_coh,por,Taub)
#print("epsza_coh",epsza_coh)
#print("Taub=",Taub)
eps_dim_carl = calculate_profile_full_coh(z, H, epsza_coh, P)
eps_dim_mood = calculate_profile_full(z, H, epsza, P)
# z_nondim_carl, eps_nondim_carl = nondim_profile(z, eps_dim_carl)
# z_nondim_mood, eps_nondim_mood = nondim_profile(z, eps_dim_mood)
eps_max = np.max(eps_dim_carl)

# setup the figure
plt.rcParams['toolbar'] = 'None'
plt.rcParams['figure.figsize'] = 10, 6
fig = plt.figure()
fig.canvas.set_window_title('SedEdu -- The Rouse Profile')
plt.subplots_adjust(left=0.1, bottom=0.1, top=0.95, right=0.9)
background_color = 'white'

# setup the first dimensionalized axis
ax_dim = plt.subplot(121)
ax_dim.set_xlabel("concentration [-]")
ax_dim.set_ylabel("height above bed [m]")
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
ax_dim.set_xlim(10**-6,10**-1)

# add second axes for nondim profiles
# ax_nondim = plt.subplot(122)
# ax_nondim.yaxis.tick_right()
# ax_nondim.set_xlabel("$c/cb$ [-]")
# ax_nondim.set_ylabel("height above $z_a$ [-]")
# ax_nondim.yaxis.set_label_position("right")

# add plot elements
Zd_line, = ax_dim.plot([0,10**-1], [H, H], linestyle=":", lw=1.5, color='black')
# Znd_line, = ax_nondim.plot([0, 1], [1, 1], linestyle=":", lw=1.5, color='black')
carl_dim_line, = ax_dim.semilogx(eps_dim_carl, z, lw=2, color='blue')
mood_dim_line, = ax_dim.semilogx(eps_dim_mood, z, lw=2, color='green')

# carl_nondim_line, = ax_nondim.plot(eps_nondim_carl, z_nondim_carl, lw=2, color='blue')
# mood_nondim_line, = ax_nondim.plot(eps_nondim_mood, z_nondim_mood, lw=2, color='green')

info_text = fig.text(0.67, 0.33, numformat(ws/ustar, P),  size=14)
fig.legend((carl_dim_line, mood_dim_line), ('single critical stress', 'Shields critical stress'), loc=(0.57, 0.20))

# add sliders
widget_color = 'lightgoldenrodyellow'

ax_ds = plt.axes([0.525, 0.80, 0.4, 0.05], facecolor=widget_color)
slide_gs = utils.MinMaxSlider(ax_ds, 'grain size [$\mu$m]', gsMin, gsMax,
    valinit=gsInit, valstep=1, valfmt='%i')

ax_taub = plt.axes([0.525, 0.65, 0.4, 0.05], facecolor=widget_color)
slide_taub = utils.MinMaxSlider(ax_taub, 'near-bed shear stress [Pa]', TaubMin, TaubMax,
    valinit=TaubInit, valstep=0.05)

    # ax_ustar = plt.axes([0.525, 0.65, 0.3, 0.05], facecolor=widget_color)
    # slide_ustar = utils.MinMaxSlider(ax_ustar, 'shear velocity [cm/s]', ustarMin, ustarMax,
    #     valinit=ustarInit, valstep=1, valfmt='%i')

ax_taucrit = plt.axes([0.525, 0.50, 0.4, 0.05], facecolor=widget_color)
slide_taucrit = utils.MinMaxSlider(ax_taucrit, 'cohesive critical shear stress [Pa]', TaucritMin, TaucritMax,
    valinit=Taucrit_cohInit, valstep=.05)

btn_reset_ax = plt.axes([0.770, 0.22, 0.1, 0.04])
btn_reset = widget.Button(btn_reset_ax, 'Reset', color=widget_color, hovercolor='0.975')

# connect widgets
slide_gs.on_changed(run_model)
#slide_ustar.on_changed(run_model)
slide_taub.on_changed(run_model)
slide_taucrit.on_changed(run_model)
btn_reset.on_clicked(reset)

# show the results
plt.show()
