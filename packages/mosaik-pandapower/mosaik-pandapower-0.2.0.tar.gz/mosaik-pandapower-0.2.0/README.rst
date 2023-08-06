mosaik-pandapower
=================

This package contains an adapter to connect *pandapower* to *mosaik*.


Input
-----
Grid import can be done from Json or Excel files, and the file
should exist in the working directory of mosaik scenario::

    sim_config = {
       'Grid': {
            'python': 'mosaik_pandapower.simulator:Pandapower'
            }
    }
     
    GRID_FILE = 'path to the file.json' or  'path to the file.xlsx'
    gridsim = world.start('Grid', step_size=15*60)
    grid = gridsim.Grid(gridfile=GRID_FILE).children
    
* In pandapower library there exist a list of standard grids that 
  can be directly imported and simulated. An overview is given
  in the `documentation`__

__ https://pandapower.readthedocs.io/en/develop/networks.html
 
  
The following list of grid clusters that could be simulated by 
this model are:

* Simbench::

          GRID_FILE = 'name of the simbench grid'

To use Simbench grid, simbench has to be installed with 'pip install simbench'
          
* Cigre networks::

          GRID_FILE = 'cigre_(voltage level: hv,mv,lv)'
          
* Cigre network with DER::

          GRID_FILE = 'cigre_mv_all' or 'cigre_mv_pv_wind'
          
* Power system Cases :
  these networks exist as Json files in
  ~/pandapower/networks/power_system_test_case_jsons

  these files should be copied in the working directory and 
  imported as json file
          
          
Examples
--------

Examples of the mosaik-pandapower adapter can be found in a seperated `repository`__.

__ https://gitlab.com/mosaik/examples/mosaik-pandapower-examples
