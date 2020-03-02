

############### Problem definition #############

from sl1m.problem_definition import *
           
        
#### problem related global variables #### 

NUM_SLACK_PER_SURFACE = 1
NUM_INEQ_SLACK_PER_SURFACE = 1 # 
M = 1000.
M2= M*10
        
        
#### global variables, depending on number of effectors ####  
# You need to call initGlobals with the number of effectors before using sl1m generic
N_EFFECTORS                             = None
DEFAULT_NUM_VARS                        = None
COM_WEIGHTS_PER_EFFECTOR                = None
DEFAULT_NUM_EQUALITY_CONSTRAINTS        = None
DEFAULT_NUM_EQUALITY_CONSTRAINTS_START  = None
DEFAULT_NUM_INEQUALITY_CONSTRAINTS      = None

#### Selection matrices ####  
COM_XY_ExpressionMatrix  = None
COM_Z1_ExpressionMatrix  = None
COM_Z2_ExpressionMatrix  = None
COM1_ExpressionMatrix    = None
COM2_ExpressionMatrix    = None
footExpressionMatrix    = None
footExpressionMatrixXY  = None
wExpressionMatrix       = None
gExpressionMatrix       = None
bExpressionMatrix       = None

#Slack variables startIndex
BETA_START  = None
GAMMA_START = None
W_START     = None
ALPHA_START = None



# breakdown of variables for each phase

# [ c_x't, c_y't, c_z_1't, c_z_2't, p_i't, b_i't, g_i't, w_i_t ,  a_i_l't]   
# [ 1    , 1    ,   1    ,    1   , 3*n_e, 2*n_e, 3*n_e,    n_e, [0, n_s]]   

# COM position
def _COM_XY_ExpressionMatrix():
    ret = zeros((2, DEFAULT_NUM_VARS))
    ret[:2,:2] = identity(2)
    return ret
    
def _COM_Z1_ExpressionMatrix():
    ret = zeros((1, DEFAULT_NUM_VARS))
    ret[0,2] = 1
    return ret
    
def _COM_Z2_ExpressionMatrix():
    ret = zeros((1, DEFAULT_NUM_VARS))
    ret[0,3] = 1
    return ret
          
def _COM1ExpressionMatrix():
    ret = zeros((3, DEFAULT_NUM_VARS))
    ret[:,:3] = identity(3)
    return ret
    
def _COM2ExpressionMatrix():
    ret = zeros((3, DEFAULT_NUM_VARS))
    ret[:2,:2] = identity(2)
    ret[2,  3] = 1
    return ret
        
def _footExpressionMatrix(footId, dim):
    ret = zeros((dim, DEFAULT_NUM_VARS))
    ret[:, 4 + footId * 3:4 + footId * 3 +dim] = identity(dim)
    return ret
        
def _contactDecisionExpressionMatrix():
    ret = zeros(DEFAULT_NUM_VARS)
    ret[W_START:] = ones(N_EFFECTORS)
    return ret
    
def _gExpressionMatrix():
    ret = zeros(DEFAULT_NUM_VARS)
    ret[GAMMA_START:W_START] = ones(3 * N_EFFECTORS)
    return ret
    
def _bExpressionMatrix():
    ret = zeros(DEFAULT_NUM_VARS)
    ret[BETA_START:GAMMA_START] = ones(2 * N_EFFECTORS)
    return ret
    
def initGlobals(nEffectors, comWeightsPerEffector=None):
    global DEFAULT_NUM_VARS
    global N_EFFECTORS
    global DEFAULT_NUM_EQUALITY_CONSTRAINTS
    global DEFAULT_NUM_EQUALITY_CONSTRAINTS_START
    global DEFAULT_NUM_INEQUALITY_CONSTRAINTS
    global COM_WEIGHTS_PER_EFFECTOR    
    global BETA_START 
    global GAMMA_START
    global W_START    
    global ALPHA_START
    
    N_EFFECTORS = nEffectors
    if comWeightsPerEffector is None:
        COM_WEIGHTS_PER_EFFECTOR = [1./(N_EFFECTORS -1) for _ in range(N_EFFECTORS) ]
    else:
        COM_WEIGHTS_PER_EFFECTOR = comWeightsPerEffector
    # for one phase, for all i:
    # [ c_x't, c_y't, c_z_1't, c_z_2't, p_i't, b_i't, g_i't, w_i_t ,  a_i_l't]   
    # [ 1    , 1    ,   1    ,    1   , 3*n_e, 2*n_e, 3*n_e,    n_e, [0, n_s]]   
    DEFAULT_NUM_VARS = N_EFFECTORS * 9 + 4     
    BETA_START = 4 + 3* N_EFFECTORS
    GAMMA_START = BETA_START +  2 * N_EFFECTORS
    W_START = GAMMA_START +  3 * N_EFFECTORS
    ALPHA_START = W_START +  N_EFFECTORS
    assert ALPHA_START == DEFAULT_NUM_VARS
    
    # c_x't, c_y't are given by a convex combination of fixed weight of the non moving effectors. There are N_EFFECTORS possible combinations
    # by default each position is equal to the previous one, so that 3 * N_EFFECTORS equalities 
    DEFAULT_NUM_EQUALITY_CONSTRAINTS = (2 + 3) * N_EFFECTORS
    DEFAULT_NUM_EQUALITY_CONSTRAINTS_START = (2) * N_EFFECTORS
    # wi <= 1 ;  - M_wi <= b_ix _ y <= M w_i; - M_wi <= g_ix _ y _ z <= M w_i      wi> 0 implicit
    DEFAULT_NUM_INEQUALITY_CONSTRAINTS = (1 + 2 * 2 + 2 * 3) * N_EFFECTORS
    
    
    global COM_XY_ExpressionMatrix 
    global COM_Z1_ExpressionMatrix 
    global COM_Z2_ExpressionMatrix  
    global COM_XY_ExpressionMatrix 
    global footExpressionMatrix   
    global footExpressionMatrixXY   
    global COM1_ExpressionMatrix  
    global COM2_ExpressionMatrix  
    global wExpressionMatrix   
    global gExpressionMatrix   
    global bExpressionMatrix   
    
    COM_XY_ExpressionMatrix  = _COM_XY_ExpressionMatrix()
    COM_Z1_ExpressionMatrix  = _COM_Z1_ExpressionMatrix()
    COM_Z2_ExpressionMatrix  = _COM_Z2_ExpressionMatrix()
    COM1_ExpressionMatrix    = _COM1ExpressionMatrix()
    COM2_ExpressionMatrix    = _COM2ExpressionMatrix()
    wExpressionMatrix        = _contactDecisionExpressionMatrix()
    gExpressionMatrix        = _gExpressionMatrix()
    bExpressionMatrix        = _bExpressionMatrix()
    footExpressionMatrix     = [_footExpressionMatrix(footId, 3) for footId in range(N_EFFECTORS)]
    footExpressionMatrixXY   = [_footExpressionMatrix(footId, 2) for footId in range(N_EFFECTORS)]
    

### helper functions to count number of variables, equalities and inequalities constraints in the problem ###

def numVariablesForPhase(phase):
    ret = DEFAULT_NUM_VARS
    numSurfaces =len(phase["S"])
    if numSurfaces > 1:
        ret += numSurfaces
    return ret
    
# ~ def numIneqForPhase(phase, phase = -1 ):
def numIneqForPhase(phase, phaseId):
    #COM Kinematic constraints: summation over all effectors, times 2 because there are 2 height possible for the transition
    #except for first time
    ret = sum([k.shape[0]  for (_, k) in phase["K"][0] ])
    if phaseId != 0:
        ret *= 2
    # relative kinematic constraints between each effectors
    for footIdFrame, constraintsInFootIdFrame in enumerate(phase["allRelativeK"][0]):
        for (footId, Kk ) in  constraintsInFootIdFrame:
            ret += Kk[0].shape[0]    
    # all inequalities relative to each contact surface 
    # the inequalities must always be written for each effector
    ret += sum([(S[1].shape[0]) * N_EFFECTORS for S in  phase["S"]])
    numSurfaces =len(phase["S"])
    if numSurfaces >1:
        # alpha > 0 
        # ~ ret += numSurfaces * NUM_INEQ_SLACK_PER_SURFACE 
        ret += numSurfaces * 2 * N_EFFECTORS 
    ret += DEFAULT_NUM_INEQUALITY_CONSTRAINTS
    return ret
    
def getTotalNumVariablesAndIneqConstraints(pb):
    nphases = pb["nphases"]
    cols = sum([numVariablesForPhase(phase) for phase in  pb["phaseData"]])
    rows = sum([numIneqForPhase(phase, i) for  i, phase in enumerate(pb["phaseData"]) ])
    return rows, cols
    
def numEqForPhase(phase, phaseId):
    #no equality constraints at first phase
    if phaseId == 0:
        return DEFAULT_NUM_EQUALITY_CONSTRAINTS_START
    return DEFAULT_NUM_EQUALITY_CONSTRAINTS
    
def getTotalNumEqualityConstraints(pb):
    return int(sum( [numEqForPhase(phase, phaseId) for  phaseId, phase in enumerate(pb["phaseData"]) ]))
    

### Constraint functions ###
        
# for all effectors i , Ki (c2 - pi) <= ki
def FootCOM2KinConstraint(pb, phaseDataT, A, b, startCol, endCol, startRow):
    idRow = startRow
    for footId, (K, k) in enumerate(phaseDataT["K"][0]):
        consLen = K.shape[0]
        A[idRow:idRow+consLen, startCol:startCol+DEFAULT_NUM_VARS] =  K.dot(COM2_ExpressionMatrix - footExpressionMatrix[footId])
        b[idRow:idRow+consLen] = k 
        idRow += consLen    
    return idRow
    
# for all effectors i , Ki (c1't - pi'(t-1)) <= ki
# this should not be called for first phase
def FootCOM1KinConstraint(pb, phaseDataT, A, b, previousStartCol, startCol, endCol, startRow):
    idRow = startRow
    for footId, (K, k) in enumerate(phaseDataT["K"][0]):
        consLen = K.shape[0]
        A[idRow:idRow+consLen, startCol:startCol+DEFAULT_NUM_VARS]                  =  K.dot(COM1_ExpressionMatrix)
        A[idRow:idRow+consLen, previousStartCol:previousStartCol+DEFAULT_NUM_VARS]  = -K.dot(footExpressionMatrix[footId])
        b[idRow:idRow+consLen] = k 
        idRow +=   consLen    
    return idRow
    
def FootCOMKinConstraint(pb, phaseDataT, A, b, previousStartCol, startCol, endCol, startRow, phaseId):
    idRow = startRow
    if phaseId != 0:
        idRow = FootCOM1KinConstraint(pb, phaseDataT, A, b, previousStartCol, startCol, endCol, startRow)
    return FootCOM2KinConstraint(pb, phaseDataT, A, b, startCol, endCol, idRow)
        
# for all effectors i , for all j !=i Ki (pj - pi) <= ki   
# TODO REMOVE FOR FIRST PHASE
def RelativeDistanceConstraint(pb, phaseDataT, A, b, startCol, endCol, startRow):    
    idRow = startRow
    for footIdFrame, constraintsInFootIdFrame in enumerate(phaseDataT["allRelativeK"][0]):
        for (footId, Kk ) in  constraintsInFootIdFrame:
            K = Kk[0]; k = Kk[1]
            consLen = K.shape[0]
            A[idRow:idRow+consLen, startCol:startCol+DEFAULT_NUM_VARS] = K.dot(footExpressionMatrix[footId] - footExpressionMatrix[footIdFrame])
            b[idRow:idRow+consLen] = k 
            idRow += consLen    
    return idRow       
    
def SurfaceConstraint(phaseDataT, A, b, startCol, endCol, startRow):    
    idRow = startRow
    sRow = startRow
    nSurfaces = len(phaseDataT["S"])
    idS = ALPHA_START
    for (S,s) in phaseDataT["S"]:   
        for footId in range(N_EFFECTORS):
            idRow = sRow + S.shape[0]
            # Sl pi - M alphal <= sl + M2 (1 - w_t)
            # Sl pi - M alphal + M2 w_t <= sl + M2
            onesM2 = ones(idRow-sRow) * M2
            A[sRow:idRow, startCol:startCol+DEFAULT_NUM_VARS] = S.dot(footExpressionMatrix[footId])
            A[sRow:idRow, startCol+W_START + footId] = onesM2
            b[sRow:idRow                 ] = s + onesM2
            if nSurfaces >1:
                A[sRow:idRow, startCol+idS] = -ones(idRow-sRow) * M
            sRow = idRow
        idS += 1
    return idRow
    
def SlackPositivityConstraint(phaseDataT, A, b, startCol, endCol, startRow):     
    idRow = startRow
    nSurfaces = len(phaseDataT["S"])
    for footId in range(N_EFFECTORS):
        # -Mwi <= b_i x y <= M wi  
        # -Mwi  - b_i xy} <= 0 ; b_ixy- M wi <= 0
        A[idRow:idRow+2, startCol + W_START + footId                                               ] = ones(2)*-M; 
        A[idRow:idRow+2, (startCol + BETA_START + footId*2):(startCol + BETA_START + footId*2) + 2 ] = -identity(2);
        idRow += 2 
        A[idRow:idRow+2, startCol + W_START + footId                                               ] = ones(2)*-M; 
        A[idRow:idRow+2, (startCol + BETA_START + footId*2):(startCol + BETA_START + footId*2) + 2 ] = identity(2);
        idRow += 2
        # -Mwi <= g_i x + g_i y + g_i_z <= M wi  
        # -Mwi  - g_i x - g_i y - g_i_z  <= 0 ; g_ix + g_iy + g_iz - M wi <= 0
        A[idRow:idRow+3, startCol + W_START + footId                                                 ] = ones(3)*-M; 
        A[idRow:idRow+3, (startCol + GAMMA_START + footId*3):(startCol + GAMMA_START + footId*3) + 3 ] = -identity(3);       
        idRow += 3 
        A[idRow:idRow+3, startCol + W_START + footId                                                 ] = ones(3)*-M; 
        A[idRow:idRow+3, (startCol + GAMMA_START + footId*3):(startCol + GAMMA_START + footId*3) + 3 ] = identity(3);        
        idRow += 3 
        # wi <= 1
        A[idRow, startCol + W_START + footId ] = 1; 
        b[idRow] = 1.00;     
        idRow += 1 
        # ~ if nSurfaces > 1:            
            # -Mwi <= a_l <= M wi  
            # -Mwi  - a_l  <= 0 ; a_l - M wi <= 0
            # ~ for i in range(nSurfaces):
                 # ~ A[idRow  , startCol + ALPHA_START + i ]  = -1;
                 # ~ A[idRow  , startCol + W_START + footId ] = -M;
                 # ~ A[idRow+1, startCol + ALPHA_START + i ]  =  1;
                 # ~ A[idRow+1, startCol + W_START + footId ] = -M;
                 # ~ idRow += 2
    # -al < 0
    # -al < 0
    # ~ nSurfaces = len(phaseDataT["S"])
    if nSurfaces > 1:
        for i in range(nSurfaces):
             A[idRow+i, startCol + ALPHA_START + i ] = -1;
        # ~ idRow += nSurfaces   
    return idRow    
    
def CoMWeightedEqualityConstraint(phaseDataT, E, e, startCol, endCol, startRow):
    idRow = startRow
    for flyingFootId in range(N_EFFECTORS):
        # 0 =  sum(j != i) o_j'i p_j't + [b_ix't, b_iy't]^T - c_x_y
        EqMat = -COM_XY_ExpressionMatrix[:]
        for otherFootId in range(N_EFFECTORS):
            if flyingFootId != otherFootId:
                EqMat += COM_WEIGHTS_PER_EFFECTOR[otherFootId] * footExpressionMatrixXY[otherFootId]
        EqMat[:2, BETA_START + flyingFootId*2:(BETA_START + flyingFootId*2)+2] = identity(2)
        E[idRow:idRow+2, startCol:startCol+DEFAULT_NUM_VARS] = EqMat; #e = 0 
        idRow+=2
    return idRow    
    
#only applies after first step
def FootContinuityEqualityConstraint(pb, phaseDataT, E, e, previousStartCol, startCol, endCol, startRow, phaseId):
    idRow = startRow
    if phaseId !=0:
        for footId in range(N_EFFECTORS):
            # 0 =  p_(i-1)'t - p_(i-1)'t + [g_ix't, b_iy't, g_iz't]^T
            E[idRow:idRow+3, startCol:startCol + DEFAULT_NUM_VARS ]         =  footExpressionMatrix[footId]
            E[idRow:idRow+3, previousStartCol:previousStartCol + DEFAULT_NUM_VARS] = -footExpressionMatrix[footId]
            E[idRow:idRow+3, startCol + GAMMA_START + footId*3:(startCol + GAMMA_START + footId*3)+3] = identity(3); #e = 0 
            idRow+=3
    return idRow    
        
    
def convertProblemToLp(pb, convertSurfaces = True):        
    assert DEFAULT_NUM_VARS is not None, "call initGlobals first"
    if convertSurfaces:
        replace_surfaces_with_ineq_in_problem(pb, eqAsIneq = True)
    #define first problem
    #A u <= b
    nIneq, nvars  = getTotalNumVariablesAndIneqConstraints(pb)
    A = zeros((nIneq, nvars)); b = zeros(nIneq)
    #E u = b
    nEq = getTotalNumEqualityConstraints(pb)
    E = zeros((nEq, nvars)); e = zeros(nEq)
    
    startRow = 0;
    startRowEq = 0;
    startCol = 0;
    previousStartCol = 0;
    endCol   = 0;
    #~ fixedFootMatrix = None;
    
    for phaseId, phaseDataT in enumerate(pb["phaseData"]):   
        #inequality
        endCol = startCol + numVariablesForPhase(phaseDataT)
        startRow = FootCOMKinConstraint(pb, phaseDataT, A, b, previousStartCol, startCol, endCol, startRow, phaseId)
        # ~ startRow = RelativeDistanceConstraint(pb, phaseDataT, A, b, startCol, endCol, startRow)
        startRow = SurfaceConstraint(phaseDataT, A, b, startCol, endCol, startRow)
        startRow = SlackPositivityConstraint(phaseDataT, A, b, startCol, endCol, startRow)
        
        #equalities        
        startRowEq = CoMWeightedEqualityConstraint(phaseDataT, E, e, startCol, endCol, startRowEq)
        startRowEq = FootContinuityEqualityConstraint(pb, phaseDataT, E, e, previousStartCol, startCol, endCol, startRowEq, phaseId)
        previousStartCol = startCol
        startCol   = endCol 
        
    print ('startRow ', startRow)
    print ('A.shape[0] ', A.shape[0])
        
    # ~ assert endCol   == A.shape[1]
    # ~ assert startRowEq == E.shape[0]
    # ~ assert startRow == A.shape[0]
    
    A,b = normalize([A,b])
    E,e = normalize([E,e])
    return (A,b,E,e)
        
def pbSelectionMatrix(pb, selectionMatrix = wExpressionMatrix):
    nvars = getTotalNumVariablesAndIneqConstraints(pb)[1]
    c = zeros(nvars)
    cIdx = 0
    for i, phase in enumerate(pb["phaseData"]):
        c[cIdx:cIdx+DEFAULT_NUM_VARS] = selectionMatrix[:]
        cIdx += numVariablesForPhase(phase)
    assert cIdx == nvars
    return c

#contact activations
def wSelectionMatrix(pb):
    return pbSelectionMatrix(pb, selectionMatrix = wExpressionMatrix)
    
#position continuity violation
def gSelectionMatrix(pb):
    return pbSelectionMatrix(pb, selectionMatrix = gExpressionMatrix)
    
#com centering
def bSelectionMatrix(pb):
    return pbSelectionMatrix(pb, selectionMatrix = bExpressionMatrix)

def alphaSelectionMatrix(pb):
    nvars = getTotalNumVariablesAndIneqConstraints(pb)[1]
    c = zeros(nvars)
    cIdx = 0    
    for i, phase in enumerate(pb["phaseData"]):
        phaseVars = numVariablesForPhase(phase)
        print ("phase vars", phaseVars)
        print ("phase DEFAULT_NUM_VARS", DEFAULT_NUM_VARS)
        nslacks = phaseVars - DEFAULT_NUM_VARS
        startIdx = cIdx + DEFAULT_NUM_VARS
        for i in range (0,nslacks,NUM_SLACK_PER_SURFACE):
            c[startIdx + i] = 1
        cIdx += phaseVars
    assert cIdx == nvars
    return c
    
def gammaSelectionMatrix(pb):
    nvars = getTotalNumVariablesAndIneqConstraints(pb)[1]
    c = zeros(nvars)
    cIdx = 0
    for i, phase in enumerate(pb["phaseData"]):
        c[cIdx:cIdx+DEFAULT_NUM_VARS] = g[:]
        print ("wExpressionMatrix", wExpressionMatrix)
        cIdx += numVariablesForPhase(phase)
    assert cIdx == nvars
    return c
    return c

###########################" PLOTTING ################"
    
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def retrieve_points_from_res(pb, res):
    coms = []
    # ~ if pb["c0"] is not None:
        # ~ coms = [pb["c0"]]
        
    # ~ if pb["p0"] is not None:
        # ~ footPos = [[pb["p0"][LF]],[pb["p0"][RF]]]
        # ~ allFeetPos = [footPos[0][0], footPos[1][0]]
    # ~ else:
    footPos = [[],[]]
    allFeetPos = []
        
    col = 0
    for i, phaseDataT in enumerate(pb["phaseData"]):          
        coms += [COM1_ExpressionMatrix.dot(res[col:col + COM1_ExpressionMatrix.shape[1]]), COM2_ExpressionMatrix.dot(res[col:col + COM2_ExpressionMatrix.shape[1]])]
        for footId in range(N_EFFECTORS):
            pos = footExpressionMatrix[footId].dot(res[col:col + footExpressionMatrix[footId].shape[1]])
            allFeetPos += [pos]
            footPos[footId] += [pos]
        col += numVariablesForPhase(phaseDataT)
    return coms, footPos, allFeetPos
    
    
def plotPoints(ax, wps, color = "b", D3 = True, linewidth=2):
    x = array(wps)[:,0]
    y = array(wps)[:,1]
    if(D3):                
            z = array(wps)[:,2]
            ax.scatter(x, y, z, color=color, marker='o', linewidth = 5) 
    else:
            ax.scatter(x,y,color=color, linewidth = linewidth)  
   
   
def plotConstraints(ax, pb, allfeetpos, coms):
    from tools.plot_plytopes import plot_polytope_H_rep
    for i, phase in enumerate(pb["phaseData"][:]):
        if i <1 :
            continue
        fixed =   phase["fixed"]  
        moving = phase["moving"]   
        oldK, oldk = pb["phaseData"][i-1]["K"][0][fixed]
        oldK = oldK.copy()
        oldk = oldk.copy()
        oldk += oldK.dot(allfeetpos[i-1])
        K, k = phase["K"][0][moving]  
        K = K.copy()
        k = k.copy()
        pos =  allfeetpos[i]
        com = coms[i]
        relK, relk = pb["phaseData"][i-1]["relativeK"][0]
        relK = relK.copy()
        relk = relk.copy()
        relk += relK.dot(allfeetpos[i-1])
        
        k = k + K.dot(pos)
        resK = vstack([oldK,K])
        resk = concatenate([oldk, k]).reshape((-1,)) 
        if True:
        #~ if i %2 ==0:
        #~ if i %2 ==1:
            try :                
                #~ plot_polytope_H_rep(resK,resk.reshape((-1,1)), ax = ax)
                plot_polytope_H_rep(relK,relk.reshape((-1,1)), ax = ax)
                #~ plot_polytope_H_rep(K,k.reshape((-1,1)), ax = ax)
            except: 
                print("qhullfailed")
    
        
def plotQPRes(pb, res, linewidth=2, ax = None, plot_constraints = False, show = True):
    coms, footpos, allfeetpos = retrieve_points_from_res(pb, res)
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
    ax.grid(False)
        
    ax.set_autoscale_on(False)
    ax.view_init(elev=8.776933438381377, azim=-99.32358055821186)
    
    # ~ plotPoints(ax, coms, color = "b")
    plotPoints(ax, footpos[RF], color = "r")
    plotPoints(ax, footpos[LF], color = "g")
    
    cx = [c[0] for c in coms]
    cy = [c[1] for c in coms]
    cz = [c[2] for c in coms]
    # ~ ax.plot(cx, cy, cz)
    px = [c[0] for c in allfeetpos]
    py = [c[1] for c in allfeetpos]
    pz = [c[2] for c in allfeetpos]
    # ~ ax.plot(px, py, pz)
        
    if show:
        plt.ion()
        plt.show()
       
    
    
def addInitEndConstraint(pb, E, e, posInit= array([0.0, 0.0, 0.]), posEnd = array([1.2, 0.1, 0.8])):
# ~ def addInitEndConstraint(pb, E, e, posInit= array([0.0, 0.0, 0.4]), posEnd = array([-0.0, 0.0, 0.4])):
    nE = zeros((E.shape[0] +6, E.shape[1] ))
    ne = zeros(E.shape[0] +6)
    idRow = E.shape[0]
    nE[:idRow,:E.shape[1]] = E  
    ne[:idRow] = e[:]
    nE[idRow:idRow+3,:DEFAULT_NUM_VARS] = footExpressionMatrix[1][:]  
    ne[idRow:idRow+3] = posInit
    nVarEnd = numVariablesForPhase(pb["phaseData"][-1])
    print ("nVarEnd", nVarEnd)
    # ~ nE[-3:,E.shape[1]-nVarEnd:E.shape[1]-nVarEnd+DEFAULT_NUM_VARS] = COM2_ExpressionMatrix[:]  
    # ~ ne[-3:] = posEnd
    return nE, ne
    
####################### MAIN ###################"

# try to import mixed integer solver
MIP_OK = False  
try:
    import gurobipy
    import cvxpy as cp
    MIP_OK = True

except ImportError:
    pass

def tovals(variables):
    return array([el.value for el in variables])
    
def solveMIP(pb, surfaces, MIP = True, draw_scene = None, plot = True):  
    if not MIP_OK:
        print("Mixed integer formulation requires gurobi packaged in cvxpy")
        raise ImportError
        
    gurobipy.setParam('LogFile', '')
    gurobipy.setParam('OutputFlag',0)
       
    A, b, E, e = convertProblemToLp(pb, True)   
    E,e = addInitEndConstraint(pb, E, e)
    slackMatrix = wSelectionMatrix(pb)
    surfaceSlackMatrix = alphaSelectionMatrix(pb)
    
    rdim = A.shape[1]
    varReal = cp.Variable(rdim)
    constraints = []
    constraintNormalIneq = A * varReal <= b
    constraintNormalEq   = E * varReal == e
    
    constraints = [constraintNormalIneq, constraintNormalEq]
    #creating boolean vars
    
    slackIndices = [i for i,el in enumerate (slackMatrix) if el > 0]
    slackIndicesSurf = [i for i,el in enumerate (surfaceSlackMatrix) if el > 0]
    print ("slackIndicesSurf", slackIndicesSurf)
    numSlackVariables = len([el for el in slackMatrix if el > 0])
    numSlackVariablesSurf = len([el for el in surfaceSlackMatrix if el > 0])
    boolvars = cp.Variable(numSlackVariables, boolean=True)      
    obj = cp.Minimize(slackMatrix * varReal)
    
    if MIP:    
        # ~ constraints = constraints + [varReal[el] <= boolvars[i] for i, el in enumerate(slackIndices)]   
        constraints = constraints + [varReal[el] == boolvars[i] for i, el in enumerate(slackIndices)]   
        
        currentSum = []
        previousL = 0
        for i, el in enumerate(slackIndices):
            if i!= 0 and el - previousL > 1.:
                assert len(currentSum) > 0
                constraints = constraints + [sum(currentSum) == 1 ]
                currentSum = [boolvars[i]]
            elif el !=0:
                currentSum = currentSum + [boolvars[i]]
            previousL  = el
        if len(currentSum) > 1:
            constraints = constraints + [sum(currentSum) == 1 ]
        
        
        if numSlackVariablesSurf > 0:
            boolvarsSurf = cp.Variable(numSlackVariablesSurf, boolean=True)    
            constraints = constraints + [varReal[el] <= boolvarsSurf[i] for i, el in enumerate(slackIndicesSurf)] 
            currentSum = []
            previousL = 0
            for i, el in enumerate(slackIndicesSurf):
                if i!= 0 and el - previousL > 1.:
                    assert len(currentSum) > 0
                    constraints = constraints + [sum(currentSum) <= len(currentSum) -1 ]
                    currentSum = [boolvarsSurf[i]]
                elif el !=0:
                    currentSum = currentSum + [boolvarsSurf[i]]
                previousL  = el
            if len(currentSum) > 1:
                constraints = constraints + [sum(currentSum) <= len(currentSum) -1 ]
        
        # ~ prev = 0
        # ~ currentSum = []
        # ~ for i, el in enumerate(slackIndices):
            # ~ print ("el", el)
            # ~ idx = el
            # ~ if i ==0:
                # ~ currentSum = [boolvars[i]]
                # ~ prev = idx
                # ~ print ("dat ", currentSum)
            # ~ elif prev < idx-1:
                # ~ print ("conAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAst ", len(currentSum) )
                # ~ constraints = constraints + [sum(currentSum) == len(currentSum) -1]
                # ~ currentSum = []
            # ~ else:
                # ~ currentSum += [boolvars[i]]
                # ~ print ("dat ", currentSum)
                # ~ prev = idx
        # ~ obj = cp.Minimize(surfaceSlackMatrix * varReal)
        obj = cp.Minimize(ones(numSlackVariables) * boolvars)
        # ~ obj = cp.Minimize(0.)
    prob = cp.Problem(obj, constraints)
    t1 = clock()
    res = prob.solve(solver=cp.GUROBI, verbose=True )
    t2 = clock()
    res = tovals(varReal)
    print("bools",  tovals(boolvars))
    print("time to solve MIP ", timMs(t1,t2))

    
    # return timMs(t1,t2)
    return pb, res, timMs(t1,t2)



if __name__ == '__main__':
    from sl1m.stand_alone_scenarios.escaliers import gen_stair_pb,  draw_scene, surfaces
    # ~ from sl1m.stand_alone_scenarios.complex import gen_stair_pb,  draw_scene, surfaces
    pb = gen_stair_pb()    
    
    t1 = clock()
    initGlobals(nEffectors = 2)
    # ~ A, b, E, e = convertProblemToLp(pb)
    # ~ E,e = addInitEndConstraint(pb, E, e)
    
    pb, res, time = solveMIP(pb, surfaces, MIP = True, draw_scene = None, plot = True)
    ax = draw_scene(None)
    plotQPRes(pb, res, ax=ax, plot_constraints = False)
    
    # ~ C = identity(A.shape[1]) * 0.00001
    # ~ c =  wSelectionMatrix(pb) * 100.
    # ~ t2 = clock()
    # ~ res = qp.quadprog_solve_qp(C, c,A,b,E,e)
    # ~ t3 = clock()
    
    # ~ print("time to set up problem" , timMs(t1,t2))
    # ~ print("time to solve problem"  , timMs(t2,t3))
    # ~ print("total time"             , timMs(t1,t3))
    
    # ~ if res.success:
        # ~ print ("success")
    # ~ else:
        # ~ print ('problem infeasible')
        # ~ assert False
    
    w = wSelectionMatrix(pb)
    b = bSelectionMatrix(pb)
    g = gSelectionMatrix(pb)
    al = alphaSelectionMatrix(pb)
    
    wR = [ el for el in w *res if abs(el) > 0.00001]
    bR = [ el for el in b *res if abs(el) > 0.0001]
    gR = [ el for el in g *res if abs(el) > 0.0001]
    alR = [ el for el in al *res if abs(el) > 0.00000001]
    
    print ("w", wR)
    print ("b", bR)
    print ("g", gR)
    print ("al", alR)
    
    # ~ ax = draw_scene(None)
    # ~ plotQPRes(pb, res, ax=ax, plot_constraints = False)
    
    # ~ surfaces, indices = bestSelectedSurfaces(pb, res)
    # ~ for i, phase in enumerate(pb["phaseData"]):  
        # ~ phase["S"] = [surfaces[i]]
        
    # ~ t1 = clock()
    # ~ A, b, E, e = convertProblemToLp(pb, False)
    
    
    # ~ C = identity(A.shape[1])
    # ~ c = zeros(A.shape[1])
    # ~ t2 = clock()
    # ~ res = qp.quadprog_solve_qp(C, c,A,b,E,e)
    # ~ t3 = clock()
    
    # ~ print("time to set up problem" , timMs(t1,t2))
    # ~ print("time to solve problem"  , timMs(t2,t3))
    # ~ print("total time"             , timMs(t1,t3))
    
    # ~ coms, footpos, allfeetpos = retrieve_points_from_res(pb, res)
    # ~ ax = draw_scene(None)
    # ~ plotQPRes(pb, res, ax=ax, plot_constraints = False)
        
    
    
    
    
        
