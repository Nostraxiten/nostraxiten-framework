class C:
    R  = '\033[91m'
    G  = '\033[92m'
    Y  = '\033[93m'
    B  = '\033[94m'
    M  = '\033[95m'
    CY = '\033[96m'
    W  = '\033[97m'
    DM = '\033[2m'
    BD = '\033[1m'
    RS = '\033[0m'

r  = lambda s: f"{C.R}{s}{C.RS}"
g  = lambda s: f"{C.G}{s}{C.RS}"
y  = lambda s: f"{C.Y}{s}{C.RS}"
cy = lambda s: f"{C.CY}{s}{C.RS}"
m  = lambda s: f"{C.M}{s}{C.RS}"
bd = lambda s: f"{C.BD}{s}{C.RS}"
dm = lambda s: f"{C.DM}{s}{C.RS}"
w  = lambda s: f"{C.W}{s}{C.RS}"
