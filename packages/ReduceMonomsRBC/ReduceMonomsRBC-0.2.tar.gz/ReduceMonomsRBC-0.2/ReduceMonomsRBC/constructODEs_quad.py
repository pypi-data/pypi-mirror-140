import sympy as sym

def construct_psi_quad(p_modes, t_modes):
    """
    Construct quadratic terms on right-hand side of ODEs for psi modes

    Parameters
    ----------
    p_modes : list
        List of psi modes, represented as tuples.
        Each tuple contains the horizontal and vertical wavenumbers.
    t_modes : list
        List of theta modes, represented as tuples.

    Returns
    -------
    rhs_psi : list
        Expressions on the right-hand side of each psi ODE.
    """    
    k = sym.Symbol('k')

    rho_p = [(mode[0]*k)**2 + mode[1]**2 for mode in p_modes]
    fQ = 'fQ = ['
    a = 'a = ['
    
    for idx, mode in enumerate(p_modes):

        m, n = mode
        idx = p_modes.index(mode)
        fQ += '['
        a += '['
        for idx1,t1 in enumerate(p_modes): #Loop over psi modes
            r,s = t1
            compat = [(p,q) for (p,q) in p_modes[idx1:] if 
                      (m == (p+r) or m == p-r) and 
                      (n == (q+s) or n == abs(q-s))]
            for (p, q) in compat:
                idx2 = p_modes.index((p,q))
                mu_1 = -1
                if (r+s) % 2 == 1: #Some cases for sign flips
                    mu_1 *= B(p,m,r)
                    if (m+n) % 2 == 0:
                        mu_1 *= -1
                if r == 0: #Compute divisor
                    d = 2
                else:
                    d = 4
                coeff1 = (B(p,m,r)*B(s,n,q)*p*s - B(q,n,s)*q*r)
                coeff3 = k/d*mu_1*(rho_p[idx2] - rho_p[idx1])/rho_p[idx]
                newTerm = sym.simplify(coeff1*coeff3)
                if newTerm != 0:
                    fQ += '[' + str(idx1+1) + ',' + str(idx2+1) + '],'
                    a += str(newTerm) + ','
        if a[-1] == '[':
            a += '0*k,'
        if fQ[-1] == ',':
            fQ = fQ[:len(fQ)-1] + '],'
        else:
            fQ += '],'
        a = a[:len(a)-1] + '],'
        
    return fQ, a

def construct_theta_quad(p_modes, t_modes):
    """
    Construct quadratic terms on right-hand side of ODEs for psi modes

    Parameters
    ----------
    p_modes : list
        List of psi modes, represented as tuples.
        Each tuple contains the horizontal and vertical wavenumbers.
    t_modes : list
        List of theta modes, represented as tuples.

    Returns
    -------
    fQ : string
        Records indices of quadratic terms in nested list form.
    a : sttring
        Records coefficients of quadratic terms in nested list form.
    """    
    k = sym.Symbol('k')
    fQ = ''
    a = ''

    for mode in t_modes:
        
        m,n = mode 
        fQ += '['
        a += '['
        for idx1,t1 in enumerate(t_modes):
            r, s = t1
            compat = [(p,q) for (p,q) in p_modes if 
                          (m == (p+r) or m == abs(p-r)) and 
                          (n == (q+s) or n == abs(q-s))]
            for (p,q) in compat:
                idx2 = p_modes.index((p,q))
                mu_2 = 1  
                if (p+q) % 2 == 1: #Cases for sign flips
                    mu_2 *= B(r,p,m)
                    if (m+n)% 2 == 1:
                        mu_2*= -1
                if (r+s) % 2 == 0:
                    mu_2 *= B(p,m,r)
                if m == 0 and (p+q)%2 == 1:
                    mu_2 *= -1
                if r == 0 or p == 0: #Compute Divisor
                    d = 2
                else:
                    d = 4
                if m == 0:
                    mu_3 = -1
                else:
                    mu_3 = 1
                coeff1 = (B(p,m,r)*B(s,n,q)*p*s - mu_3*B(q,n,s)*B(r,p,m)*q*r)
                coeff3= mu_2*k/d
                newTerm = sym.simplify(coeff1*coeff3)
                if newTerm != 0:
                    thetaIdx = str(idx1+1+len(p_modes))
                    fQ += '[' + thetaIdx + ',' + str(idx2+1) + '],'
                    a += str(newTerm) + ','
        if a[-1] == '[':
            a += '0*k,'
        if fQ[-1] == ',':
            fQ = fQ[:len(fQ)-1] + '],'
        else:
            fQ += '],'

        a = a[:len(a)-1] + '],'
        
    fQ = fQ[:len(fQ)-1] + ']'
    a = a[:len(a)-1] + ']'
    
    return fQ, a
 
def B(i,j,k):
    """
    Tensor B used in constructing ROMs. 

    Parameters
    ----------
    i : int
    j : int
    k : int
        Indices in the tensor.

    Returns
    -------
    int
        Tensor output.
    """
    if i == j + k:
        return -1
    elif j == i + k or k == i + j:
        return 1
    else:
        msg = "Possible Error: Indices ({},{},{})".format(i,j,k)
        print(msg)
        return 0

