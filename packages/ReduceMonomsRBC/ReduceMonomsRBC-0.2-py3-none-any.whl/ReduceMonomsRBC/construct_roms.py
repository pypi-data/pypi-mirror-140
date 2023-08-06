
from .constructODEs_quad import construct_psi_quad, construct_theta_quad
from timeit import default_timer as timer

def hk_modes(hier_num):
    """
    Generate modes in the HK hierarchy

    Parameters
    ----------
    hier_num : int
        Model number in the HK hierarchy.

    Returns
    -------
    p_modes : list, optional
        List of psi modes, represented as tuples.
        Each tuple contains the horizontal and vertical wavenumbers.
        Only necessary if mode_type = 'input'. 
        Default (Lorenz): [(1,1)].
    t_modes : list, optional 
        List of theta modes, represented as tuples.
        Only necessary if mode_type = 'input'.
        Default (Lorenz): [(0,2), (1,1)]
    """
    p_modes = [(0,1), (1,1)]
    t_modes = [(0,2), (1,1)]
    
    pair = (1,1) 
    
    
    for i in range(1, hier_num):

        if pair[1] == 1:
            level = pair[0]+1
            pair = (1, level)
            p_modes.append((0, level*2-1))
            t_modes.append((0, level*2))
        else:
            pair = (pair[0]+1, pair[1]-1)
            
        p_modes.append(pair)
        t_modes.append(pair)
        
            
    p_modes.sort()
    t_modes.sort()
                
    return p_modes, t_modes

def construct_roms_quadratic(mode_sel = 'hk', p_modes = [(1,1)],
                   t_modes = [(1,1), (0,2)], 
                   hier_num=1, fQ_dir='Monoms/fQ/'):
    """
    Construct quadratic terms of ROM for the Rayleigh--Benard system and 
    output data for monomoial reduction. Model only computes quadratic terms
    on RHS.

    Parameters
    ----------
    mode_sel : string, optional
        Method of mode selection. Options:
            'hk' : select model from hk hierarchy (model number = hier_num)
            'input' : input mode list manually (p_modes, t_modes)
    p_modes : list, optional
        List of psi modes, represented as tuples.
        Each tuple contains the horizontal and vertical wavenumbers.
        Only necessary if mode_type = 'input'. 
        Default (Lorenz): [(1,1)].
    t_modes : list, optional 
        List of theta modes, represented as tuples.
        Only necessary if mode_type = 'input'.
        Default (Lorenz): [(0,2), (1,1)]
    hier_num : int, optional
        Number in the HK hierarchy (hier_num = n means the nth model).
    fQ_dir : string, optional
        Name of directory to output matlab files. Must be of form dir1/dir2.
        If print_matlab is False, this argument does nothing.    
        The default is 'Monoms/fQ/'

    Returns
    -------
    None.
    """   
    start = timer()

    if mode_sel == 'hk':
        p_modes, t_modes = hk_modes(hier_num)
    elif mode_sel == 'input':
        #Make sure modes are in correct order
        p_modes.sort()
        t_modes.sort()
    
    num_modes = len(p_modes) + len(t_modes)
    
    #Compute lists of variable indices, coeffs of quadratic terms on RHS
    fQ, a = construct_psi_quad(p_modes, t_modes)
    theta_fQ, theta_a = construct_theta_quad(p_modes, t_modes)
    
    fQ += theta_fQ
    a += theta_a
    
    fname = fQ_dir + 'hk' + str(num_modes) + '.txt'
    
    file = open(fname,'w')
    file.write(str(fQ) + '\n')
    file.write(str(a))
    file.close()
    
    end = timer()
    print('Time = ' + str(end-start))
    
    return
