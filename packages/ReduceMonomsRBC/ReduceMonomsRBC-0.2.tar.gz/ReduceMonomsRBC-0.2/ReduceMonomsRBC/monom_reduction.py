"""
Created on Mon Feb 14 21:28:43 2022

@author: mlols
"""

from timeit import default_timer as timer
import csv
import os
from .construct_roms import construct_roms_quadratic, hk_modes
from .reduce_monoms import reduceMonoms

def monom_reduction(ode_name, monom_deg=2, hk_hier=True, hier_num=1,
                    p_modes=[(1,1)], t_modes=[(0,2),(1,1)],
                    monom_stats=True, monom_dir='Monoms/', 
                    fQ_dir='Monoms/fQ/'):
    """
    Generates list of monomials for auxiliary func ansatz in SDP computation. 
    Monomials are reduced using symmetry conditions and highest degree 
    cancellation.

    Parameters
    ----------
    ode_name : string
        Name of ODE. If name is 'auto', name will be 'HKN' with N = num vars
    monom_deg : int, optional
        Maximum degree of auxilary functions. Typically an even number.
        The default is 2.
    hk_hier : bool, optional
        If True, uses HK hierarchy for Rayleigh-Benard. The default is True.
    hier_num : int, optional
        Model number in the HK hierarchy. Only matters if hk_hier=True.
        The default is 1.
    p_modes : list
        List of psi modes, represented as tuples.
        Each tuple contains the horizontal and vertical wavenumbers.
    t_modes : list
        List of theta modes, represented as tuples.
    monom_stats : bool, optional
        If True, outputs stats on number of monomials after each step.
        The default is True.
    monom_dir : string, optional
        Specify output directory. The default is 'Monoms/'
    fQ_dir : string, optional
        Specify output directory for ROM structrue data. 
        The default is 'Monoms/fQ/'

    Returns
    -------
    None.
    
    Examples
    --------
    monom_reduction('HK4', 4, 6, hk_hier=True, hier_num=1)
        Generates and reduces list of monomials of degree 6 for the HK4 model

    """   
    if type(ode_name) is not str:
        print('Error: ode_name must be a string')
        return
    if type(monom_deg) is not int:
        print('Error: monom_deg must be an integer')
        return
    if type(hk_hier) is not bool:
        print('Error: hk_hier must be bool')
        return
    if type(hier_num) is not int:
        print('Error: hier_num must be an integer')
        return
    if type(monom_stats) is not bool:
        print('Error: monom_stats must be bool')
        return
    if type(monom_dir) is not str:
        print('Error: monom_dir must be a string')
        return
    if type(fQ_dir) is not str:
        print('Error: fQ_dir must be a string')
        return
    if not hk_hier:
        if p_modes is not list:
            print('p_modes must be a list of tuples')
            return
        if t_modes is not list:
            print('t_modes must be a list of tuples')
            return
    
    #Create directories if necessary
    if not os.path.exists(monom_dir):
        os.mkdir(monom_dir)
    if monom_dir[-1] != '/':
        monom_dir += '/'
        
    if not os.path.exists(fQ_dir):
        os.mkdir(fQ_dir)
    if fQ_dir[-1] != '/':
        fQ_dir += '/'
        
    if hk_hier:
        p_modes, t_modes = hk_modes(hier_num)
    num_vars = len(p_modes) + len(t_modes)
    if ode_name == 'auto':
        ode_name = 'hk' + str(num_vars)
        
    #Write data file with indices and coefficients of quadratic terms
    print('System: ' + ode_name)
    print('-'*15)
    print('Constructing ROMs')
    construct_roms_quadratic(mode_sel='hk', hier_num=hier_num, 
                                         fQ_dir=fQ_dir,
                                         p_modes=p_modes, t_modes=t_modes)
    
    start = timer()
    #Generate and reduce monomial list
    V, V0, Monoms = reduceMonoms(num_vars, monom_deg, fQ_dir)
    
    if V is None:
        print("No monomials remain. Check for errors.")
        return
        
    monom_stats_file = 'MonomStats.csv'
    end = timer()
    print('Time = ' + str(end-start))
    
    if not os.path.exists(monom_dir + monom_stats_file):
        head1 = ['','','Initial','','','Symm','','','End','','','Time']
        head2 = ['n','d'] + ['Deg d','Deg < d','Total']*3 + ['']
        with open(monom_dir+monom_stats_file, 'w', newline='') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow(head1)
            csvwriter.writerow(head2)
    
    with open(monom_dir + monom_stats_file,'a+',newline='') as csv_file:
        csvwriter = csv.writer(csv_file)
        t = '{:.3f}'.format(end-start)
        row = [str(num_vars), str(monom_deg)]+[str(m) for m in Monoms]+[t]
        csvwriter.writerow(row)
        
    monom_file = 'Monoms_' + ode_name + '_deg_' + str(monom_deg) + '.csv'
    
    with open(monom_dir + monom_file,'w', newline='') as csv_file:
        csvwriter = csv.writer(csv_file)
        for v in V:
            csvwriter.writerow(v)
        for v in V0:
            csvwriter.writerow(v)
    
    return