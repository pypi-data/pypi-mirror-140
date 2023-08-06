# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 22:18:26 2021

@author: mlols
"""

import numpy as np
from scipy.linalg import null_space
import sympy as sym
from random import uniform
from os import path

def partition_rec(n, d, depth=0):
    """
    Recursion for generating partitions of integer d of length n

    Parameters
    ----------
    n : int
        Length of partition vector.
    d : int
        Maximum sum of the vector.
    depth : int, optional
        Depth of recursion. The default is 0.

    Returns
    -------
    List
        Partitions in recursive algorithm, used for building partitions list.

    """
    if n == depth:
        return [[]]
    
    P = []
    
    for i in range(d+1):
        for item in partition_rec(n, d-i, depth=depth+1):
            P.append(item + [i])  
              
    return P

def partition(n, d):
    """
    Generate list of partitions of sum d or less of length n

    Parameters
    ----------
    n : Integer
        Length of the partition vector
    d : Integer
        Maximum sum of the vector

    Returns
    -------
    List
        All partitions of maximum sum d of length n.
        Each element of the list is a list of length n.

    """
    return [[d-sum(p)] + p for p in partition_rec(n-1, d)]

def UV(n,i):
    """
    Unit vector of length n with a 1 in the ith position.
    """
    UV = [0] * (i-1) + [1] + [0] * (n-i)
    return np.array(UV)

def ind2vec(n,ind):
    """
    Return vector of length n with ones in the indices in ind.
    """
    vec = [0]*n
    for i in ind:
        vec[i-1] += 1
        
    return tuple(vec)

def num_zero(n):
    """ 
    Number of modes with nonzero horizontal wavenumber in the 
    system with n total modes of the HK hierarchy.
    """
    shells = [4,10,18,28,40,54,70,88,108,130,154,180,208,238]
    return min([i+1 for i in range(len(shells)) if shells[i] >= n])

#Find nullspace of a matrix mod 2
def nullspace(M):
    """
    Find the nullspace of the matrix M over the integers modulo 2. 
    This means that all operations are performed in mod 2.
    """
    m = np.array([np.array(mi) for mi in M])
    m = np.transpose(np.ubyte(m))
    rows, cols = m.shape
    Id = np.ubyte(np.eye(rows))
    
    l = 0
    for k in range(min(rows, cols)):
        if l >= cols: break
        # Swap with pivot if m[k,l] is 0
        if m[k,l] == 0:
            found_pivot = False
            while not found_pivot:
                if l >= cols: break
                for i in range(k+1, rows):
                    if m[i,l]:
                        m[[i,k]] = m[[k,i]]  # Swap rows
                        Id[[i,k]] = Id[[k,i]]
                        found_pivot = True
                        break

                if not found_pivot: l += 1

        if l >= cols: break  # No more rows

        # For rows below pivot, subtract row
        for i in range(k+1, rows):
            if m[i,l]: 
                m[i] ^= m[k]
                Id[i] ^= Id[k]

        l += 1
        zero_rows = np.where(~m.any(axis=1))[0]
        N = Id[zero_rows]

    return N

def unique(lst):
    """
    Identify the unique elements of a list (the elements that do not appear 
    anywhere else in the list)
    """
    un_lst = []
    for i,v in enumerate(lst):
        if i == len(lst) - 1:
            continue
        if v != lst[i-1] and v != lst[i+1]:
            un_lst.append(i)
          
    return un_lst

def delMult(lst,elts):
    """
    Remove elements from the list 'lst' with elements in position 'elts'
    """
    elts.sort(reverse=True)
    for elt in elts:
        del lst[elt]

    return lst

def symmRed(V, V0, fQ, n, nzero):
    """
    Reduce list of monomials using symmetries of ODE system. Monomials used
    in SOS opt should obey sign-symms of ODE variables; others can be ignored.

    Parameters
    ----------
    V : List
        List of monomials of highest degree. See Readme for monomial format.
    V0 : List
        Monomials of lower degree. Same format as V.
    fQ : List
        Terms in right-hand side of ODE of highest deg. 
        Sub-lists correspond to equation # in ODE system.
        Sub-sub-lists give indices of quadratic terms.
        Ex: [[[2,3]],[],[]] indicates that 1st ODE has term prop to x2x3.
    n : List
        Coefficients of the terms in fQ.
        Sub-lists correspond to eqn # in ODE system
    nzero : Integer
        # of terms w/nonzero horizontal wavenum

    Returns
    -------
    V : List
        List of monomials of highest deg, reduced.
    V0 : List
        List of monomials of lower deg, reduced.
    """
    M = set()
    #Construct M, matrix of monoms in x.fQ (state vec times quad rhs terms)
    for i,q in enumerate(fQ):
        if q == [[]]:
            continue
        for j in range(len(q)):
            M.add(ind2vec(n,q[j]+[i+1]))
    #Add lower order terms of x.f (only off-diag matter)
    for i in range(nzero+1,n//2+1):
        M.add(ind2vec(n,(i,n//2+i)))
        
    #Sign-symms of ODE given by nullspace of M (mod 2)
    S = nullspace(M).tolist()
    #Eliminate terms not satisfying the symmetries
    V = [p.tolist() for p in V if all(np.sum(p*S, axis=1) % 2 == 0)]
    V0 = [p.tolist() for p in V0 if all(np.sum(p*S, axis=1) % 2 == 0)]
    
    return V, V0

def constructDV(V, fQ, a, n):
    """
    Construct gradient of V in monom structure of V.

    Parameters
    ----------
    V : List
        Monomials of highest degree.
    fQ : List
        Terms in rhs of ODE of highest degree.
    a : List
        Coefficients of fQ.
    n : Integer
        Length of state vector (x)

    Returns
    -------
    DV : List
        Monomials of the terms in grad(V). 
    V_locs : Array
        Each entry in V_locs indicates the term in V that generated the 
        corresponding term in DV.
    coeffDV : Array
        Coefficients of the terms in DV.

    """
    #Expected # of terms for pre-allocation
    exp_terms = len(V)*n**2//5 
    DV = np.zeros([exp_terms,n],int) #Monomial terms in gradient of V
    #Keep track of indices of V that produced term in DV
    V_locs = np.zeros([exp_terms],int)
    coeffDV = np.zeros(exp_terms)
    
    #Take the gradient of V, creating DV and coeffDV
    ii = 0
    for i,m in enumerate(V):
        for j in range(n):
            if m[j] == 0:
                continue
            gradm = m - UV(n,j+1) #Subtract 1 from power to take deriv
            for K,q in enumerate(fQ[j]):
                gradV = gradm + ind2vec(n,q)
                DV[ii] = gradV
                V_locs[ii] = i
                coeffDV[ii] = a[j][K]*m[j]
                ii += 1

    #Eliminate excess elements and convert DV to list
    DV = DV[:ii].tolist()
    V_locs = V_locs[:ii]
    coeffDV = coeffDV[:ii]
    
    return DV, V_locs, coeffDV

def highestDegRed(DV, UDV, V_locs, V, coeffDV, tol=1e-6):
    """
    Reduce monomial list using requirement that highest degree terms 
    must cancel (must have odd highest degree terms)

    Parameters
    ----------
    DV : List
        Monomials of the terms in grad(V). 
    V_locs : Array
        Each entry in V_locs indicates the term in V that generated the 
        corresponding term in DV.
    coeffDV : Array
        Coefficients of the terms in DV.
    V : List
        List of monomials of highest degree.
    coeffDV : Array
        Coefficients of highest degree terms.
    tol : float, optional
        Tolerance for nullspace calculation.
        Default is 1e-6.

    Returns
    -------
    V : List
        List of monomials of highest degree.
    NA : List
        Null space of A.

    """
    V_ind_to_del = []
    while len(UDV) > 0:
        DV_ind_to_del = np.array([],int)
        for i in UDV:
            if i in DV_ind_to_del:
                continue
            V_ind = V_locs[i]
            V_locs_ind = np.where(V_locs == V_ind)[0]
            DV_ind_to_del = np.append(DV_ind_to_del, V_locs_ind)
            V_ind_to_del.append(V_ind)
            
        V_locs = np.delete(V_locs, DV_ind_to_del)
        coeffDV = np.delete(coeffDV, DV_ind_to_del)
        delMult(DV, DV_ind_to_del.tolist())
        
        UDV = unique(DV)
                
    new_V_ind = delMult(list(range(len(V))), V_ind_to_del)
    V = delMult(V, V_ind_to_del)
    
   
    
    A = np.zeros([len(DV)//2+1, len(V)])
    ii = 0
    j = 0
    while ii < len(DV):
        ii_aux = next((i for i in range(ii,len(DV)) 
                       if DV[i] != DV[ii]), len(DV))
        for ind in range(ii,ii_aux):
            A[j,new_V_ind.index(V_locs[ind])] = coeffDV[ind]
        j += 1
        ii = ii_aux
    A = A[:j] #Remove extra rows in A  
            
    NA = null_space(A)
    V_ind_to_del = []
        
    for i in range(len(V)):
        if all(abs(NA[i,:]) < tol):
            V_ind_to_del.append(i)
    if len(V_ind_to_del) == 0:
        return V, NA
        
    V = delMult(V, V_ind_to_del)
        
    return V, NA
        
def reduceMonoms(n, d, fQ_dir):
    """
    Generate all monomials of length n, degree d, and reduce monomials
    using model symmetries and highest degree cancellation. Prints monomial
    list and summary stats to csv files.

    Parameters
    ----------
    n : int
        Number of state variables.
    d : int
        Maximum degree of auxiliary functions.
    fQ_dir : string
        Output directory for fQ files

    Returns
    -------
    V : List
        List of monomials of highest degree.
    V0 : List
        List of monomials of lower degree.
    Monoms : list
        Number of monomials of highest deg, lower deg, and total
    """
    nzero= num_zero(n)
    
    #Generate all possible monomials of length n that sum to d
    print('Generating monomial list...')
    V = np.array(partition(n,d),int)
    V0 = []
    for i in range(d-1, 0, -1):
        V0 += partition(n,i)
        
    V0 = np.array(V0,int)
    
    fQ = []
    
    #Imports variables a and fQ from text files
    file_name = 'hk' + str(n) + '.txt'
    
    #See readme for format of nested lists.
    k = sym.Symbol('k')
    
    if path.exists(fQ_dir + file_name):
        data_file = open(fQ_dir + file_name, 'r')
        
        line = data_file.readline()
        fQ = eval(line[5:-1])
        line2 = data_file.readline()
        a = eval(line2[4:])

        data_file.close()
    else:
        print('ODE data file not found.')
        return None, None, None

    #Select random value for k since symbolic very slow
    kVal = uniform(.25, .75)
    a = [[float(term2.subs(k,kVal)) for term2 in term] for term in a]
    
    Monoms = [len(V), len(V0), len(V)+len(V0)]
    
    print('Applying symmetry reduction...')
    
    V, V0 = symmRed(V, V0, fQ, n, nzero)
    
    Monoms += [len(V), len(V0), len(V)+len(V0)]
    
    print('Applying highest degree cancellation...')
    DV, V_locs, coeffDV = constructDV(V, fQ, a, n)
    
    #Sort together to preserve indices
    sorted_tuples = zip(*sorted(zip(DV, V_locs, coeffDV)))
    DV, V_locs, coeffDV = [list(tup) for tup in sorted_tuples]
    
    UDV = unique(DV)
    
    V, NA = highestDegRed(DV, UDV, V_locs, V, coeffDV, tol=1e-6)
    
    Monoms += [len(V), len(V0), len(V)+len(V0)]
        
    return V, V0, Monoms
        