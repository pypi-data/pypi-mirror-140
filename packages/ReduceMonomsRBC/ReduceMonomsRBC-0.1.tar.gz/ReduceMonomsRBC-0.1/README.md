# ReduceMonomsRBC
ReduceMonomsRBC is a Python package that reduces the list of monomials for sum-of-squares (SOS) optimization of reduced-order models (ROMS). The monomials are reduced by applying highest-degree cancellation and symmetry conditions derived from the structure of the ROM. This package is built for ROMs of 2D Rayleigh&ndash;Bénard convection, but can be adapted to any ROM whose general structure is known.

## Features:
- Reduce list of monomials and save list for use in SOS optimization
- Generate ouptut file with number of monomials at each reduction step.

# Package Requirements
- numpy (Version 1.5 or later)
- sympy (Version 1.6 or later)
- csv (any version)
- scipy (Version 0.10 or later)

# Installation
To install the package, either:
- download or clone this repository and use `from ReduceMonomsRBC import monom_reduction` from the directory containing the package, OR
- install package directly using `pip install ReduceMonomsRBC` then `from ReduceMonomsRBC import monom_reduction`

# Instructions
To construct a system of ROMs, use the command `monom_reduction(*args)`. Options can be passed as function arguments as detailed below.

## Options:
  - `ode_name` : Name of ODE
  - `num_vars` : Number of variables in ODE
  - `monom_deg` : Maximum degree of auxilary functions. Typically an even number
  - `hk_hier` : If `True`, uses HK hierarchy for Rayleigh&ndash;Bénard
  - `hier_num` : Model number in the HK hierarchy. Only matters if `hk_hier=True`
  - `monom_stats` : If `True`, outputs stats on number of monomials after each step
  - `out_file` : Name of output file
  - `out_dir` : Specify output directory
        
## Examples:
`monom_reduction('HK4', 4, 6, hk_hier=True, hier_num=1)`  
Generates and reduces list of monomials of degree 6 for the HK4 model (in the HK hierarchy of ROMs)
