# cartons_inventory

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Documentation Status](https://readthedocs.org/projects/cartons_inventory/badge/?version=latest)](https://cartons_inventory.readthedocs.io/en/latest/?badge=latest)

## Overview

Cartons\_inventory is package to track the content of SDSS cartons in targetdb database.
It can take as an input an rsconfig file, a curstom file or a targetdb selection criteria.
As an output it can create an input carton list (from a targetdb selection criteria), a list of CartonInfo objects with the information of the content of the cartons,
a Pandas dataframe with the parameters of every target in the carton, a Pandas dataframe with the informaion of inexisting carton versions searched along with existing
versions/categories for that carton name, and it can create an output .csv file with the information of the content of the cartons. 
The main method is process\_cartons which wraps practically all the other methods in cartons\_inventory

## Installation

To install `target_selection` do

```console
$ pip install sdss-cartons-inventory
```

## Development

New code must follow the [SDSS Coding Standards](https://sdss-python-template.readthedocs.io/en/latest/standards.html). Linting checks run as a GitHub workflow after each commit. The workflow also check that the package and dependencies can be installed. Pull Requests that don't pass the checks cannot be merged.

To test the code offline, you must install [flake8](https://flake8.pycqa.org/en/latest/) and [isort](https://pycqa.github.io/isort/) and run the following commands from the root of the package

```console
$ flake8 . --count --show-source --statistics
$ isort -c python/ bin/
```

If the command exit without error, everything should be fine.

## Usage

In this section we will review examples for using all the aplications of the cartons\_inventory package

### 1 Creating an input file from a targetdb selection criteria

To do this you have to use _origin_ ='targetdb', and _write\_input_ = True. Then you have to make sure the file with the output name doesnt exist or that _overwrite_=True
Then you define a selection criteria with the arguments of _versions_, _forced\_versions_, _all\_cartons_, and _carton\_name\_pattern_.

_all\_cartons_ = True means that we will search for all carton names while _all\_cartons_=False means that only cartons with a name matching _carton\_name\_pattern_ 
(which has to be defined) will be searched. The \* character can be used as a wildcard in the _carton\_name\_pattern_ string.

The _versions_ parameter can be 'all' to retrieve all the versions from each carton, 'latest' to retrieve the newest version of each carton, or 'single' to retrieve only
the versions matching the _unique\_version_ int, which has to be defined. Then you can also use the _forced\_versions_ dictionary to override the previous version criteria
for specific cartons where the keys are the name of the cartons for which you want to use a specific version, and the values are the version you want to use for each of those
cartons.

For example in the following block code we create input file ['./files/targetdb/Cartons\_sample\_Versions\_single\_and\_forced.txt'](https://github.com/sdss/cartons_inventory/blob/main/python/cartons_inventory/files/targetdb/Cartons_sample_Versions_single_and_forced.txt) with a list of cartons starting with 'bm\_rm' with _version\_pk_
49 except for carton 'bhm\_rm\_core' for which we search _version_ 83. This file can then be used as the input file for process\_cartons by copying it to the './files/custom/' folder and using
_origin_='custom' and _inputname_='Cartons\_sample\_Versions\_single\_and\_forced.txt'. The name assigned in these cases is 'Cartons\_' followed by 'all' or 'sample' depending on whether we are
searching all carton names or not, then '_Versions_' followed by the value of _versions_ or the value of _unique\_version_ if _version_='single', finally a suffix '_and\_forced' is added if the
_forced\_versions_ dictionary was used.

```
[u0955901@operations:cartons_inventory]$ ipython -i cartons.py 
Python 3.7.7 (default, Mar 26 2020, 15:48:22) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: process_cartons(origin='targetdb', write_input=True, all_cartons=False, cartons_name_pattern='bhm_rm*', versions='single', unique_version=49, forced_versions={'bhm_rm_core':83},overwrite=True)  
[INFO]: ############################################################
[INFO]: ###               STARTING CODE EXECUTION                ###
[INFO]: ############################################################
[INFO]: Ran process_cartons using the following arguments
[INFO]: origin=targetdb
[INFO]: files_folder=./files/
[INFO]: inputname=None
[INFO]: delim=|
[INFO]: check_exists=False
[INFO]: verb=True
[INFO]: return_objects=False
[INFO]: write_input=True
[INFO]: write_output=False
[INFO]: assign_sets=False
[INFO]: assign_placeholders=False
[INFO]: visualize=False
[INFO]: overwrite=True
[INFO]: all_cartons=False
[INFO]: cartons_name_pattern=bhm_rm*
[INFO]: versions=single
[INFO]: forced_versions={'bhm_rm_core': 83}
[INFO]: unique_version=49
[INFO]:  
[INFO]: Wrote file ./files/targetdb/Cartons_sample_Versions_single_and_forced.txt
```

### 2 Check the existence in targetdb of all the cartons in a custom list or an rsconfig file

To do this you have to use _check\_exists_=True _origin_= 'rsconfig' or 'custom' and you have to provide the inputname of the file to read which has to be in the folder './files/\{origin\}'.
This will return a Pandas dataframe with the information of the carton/version/category combinations not present in targetdb along with version/category combinations that do exist in targetdb
for those cartons. In this case we also use _verb_=True so that besides returning the dataframe the code will print and log the suggestion on how to edit your input file to replace the inexisting
carton/version/category combination for existing ones.
For example if we want to check the existence of the cartons/version/category combinations in rsconfig file 'cartons\-0.5.3' we use the following statement.

```
[u0955901@operations:cartons_inventory]$ ipython -i cartons.py 
Python 3.7.7 (default, Mar 26 2020, 15:48:22) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: diff = process_cartons(origin='rsconfig', check_exists=True, inputname='cartons-0.5.3.txt', verb=True)                                                                                                     
[INFO]: ############################################################
[INFO]: ###               STARTING CODE EXECUTION                ###
[INFO]: ############################################################
[INFO]: Ran process_cartons using the following arguments
[INFO]: origin=rsconfig
[INFO]: files_folder=./files/
[INFO]: inputname=cartons-0.5.3.txt
[INFO]: delim=|
[INFO]: check_exists=True
[INFO]: verb=True
[INFO]: return_objects=False
[INFO]: write_input=False
[INFO]: write_output=False
[INFO]: assign_sets=False
[INFO]: assign_placeholders=False
[INFO]: visualize=False
[INFO]: overwrite=False
[INFO]: all_cartons=True
[INFO]: cartons_name_pattern=None
[INFO]: versions=latest
[INFO]: forced_versions=None
[INFO]: unique_version=None
[INFO]:  
Carton mwm_halo_bb_boss not in targetdb, to avoid this you can replace the next
line with the information that follows replacing (stage) and (active) if it corresponds
|                         mwm_halo_bb_boss |  0.5.1 |                    0 |   srd |      n | --> Replace this line
|                         mwm_halo_bb_boss | 0.5.0-beta.1 |              science |   N/A |    N/A |
|                         mwm_halo_bb_boss |  0.5.0 |              science |   N/A |    N/A |
|                         mwm_halo_bb_boss |  0.5.1 |              science |   N/A |    N/A |

Carton mwm_halo_sm_boss not in targetdb, to avoid this you can replace the next
line with the information that follows replacing (stage) and (active) if it corresponds
|                         mwm_halo_sm_boss |  0.5.1 |                    0 |   srd |      n | --> Replace this line
|                         mwm_halo_sm_boss | 0.5.0-beta.1 |              science |   N/A |    N/A |
|                         mwm_halo_sm_boss |  0.5.0 |              science |   N/A |    N/A |
|                         mwm_halo_sm_boss |  0.5.1 |              science |   N/A |    N/A |

[INFO]: Ran check_existence to compare input file cartons-0.5.3.txt with targetdb content

In [2]: diff                                                                                                                                                                                                       
Out[2]: 
             carton          plan category_label stage active      tag  version_pk  in_targetdb
0  mwm_halo_bb_boss         0.5.1              0   srd      n    0.3.2          92        False
1  mwm_halo_bb_boss  0.5.0-beta.1        science   N/A    N/A  0.2.2b0          67         True
2  mwm_halo_bb_boss         0.5.0        science   N/A    N/A    0.3.0          83         True
3  mwm_halo_bb_boss         0.5.1        science   N/A    N/A    0.3.2          92         True
0  mwm_halo_sm_boss         0.5.1              0   srd      n    0.3.2          92        False
1  mwm_halo_sm_boss  0.5.0-beta.1        science   N/A    N/A  0.2.2b0          67         True
2  mwm_halo_sm_boss         0.5.0        science   N/A    N/A    0.3.0          83         True
3  mwm_halo_sm_boss         0.5.1        science   N/A    N/A    0.3.2          92         True
```

In this case process_cartons is telling us that there are 2 carton/version/category label combinations present in rsconfig file 'cartons-0.5.3' that are not present in targetdb
for cartons 'mwm\_halo\_bb\_boss' and 'mwm\_halo\_ms\_boss'. This is because version 92 doesn't exist for these cartons so the code indicates the corresponding lines you should probably remove
from your input 'cartons-0.5.3' and replace it by the suggestions shown below pointing to exising versions of these cartons. For the moment _stage_ and _active_ are just 'N/A' becuase that information
is not present in targetdb. And the 'diff' Pandas dataframe returned contains the basic information of the inexisting entries and the suggested carton/version/category combinations to use instead of the
inexisting ones. The last column _in\_targetdb_ indicated whether the carton/version/category combination is found or not in targetdb.

### 3 Assign target dependent information for a group of cartons and return CartonInfo objects

One of the main goals of the process_cartons method is to assign target dependent information for a group of cartons. These are parameters that may vary from target to target from the same
carton, as opposed to carton dependent information which is shared by all the targets from the same carton and which is assigned at instantiation. The target dependend information is split in
two groups and they can be calculated independently to save time for the user if it is interested in one but not the other. The first ones are python sets containing the different values found for
the carton's _cadence\_pk_, _cadence\_label_, _mapper\_pk_, and _instrument\_label_, along with the minimum and maximum values of _value_, and _priority. To assign these attributes to the CartonInfo
objects parameter one has to set _assign\_sets_=True.
The other target dependent parameter that can be calculated are maGnitude placeholders used for each photometric system (SDSS, 2MASS, GAIA). The type of outliers are:
None (For empty entries), Invalid (For Nan's and infinite values), and \{Number\} (For values brighter than -9, dimmer than 50, or equal to zero), in the latter cases the number itself is returned
as the outlier type. To calculate magnitude outliers the user has to use _assign\_placeholders_=True.
In the following block we show an example in which we assign both the target dependent sets/ranges and the magnitude placeholders for a custom list of mwm\_cb\_uvex cartons, called
['mwm\_uvex.txt'](https://github.com/sdss/cartons_inventory/blob/main/python/cartons_inventory/files/custom/mwm_uvex.txt).
In this case we also use _return\_objects_=True which in principle is optional but given that we are not saving the output .csv file (_write\_output_=False), is the only practical way to retrieve
the information from these cartons.
At the end of this example we see that 5 CartonInfo objects are returned, one for each carton, and that the first object corresponds to carton='mwm\_cb\_uvex1', which has as magnitude placeholders
(values assigned to a given magnitude when photometry couldn't be obtained) 'Invalid' (Nan's of Inf's) for all three photometric systems, along with -9999.0 and None for TMASS.
To properly visualize the content of a given CartonInfo object see the next usage example.
```
[u0955901@operations:cartons_inventory]$ ipython -i cartons.py 
Python 3.7.7 (default, Mar 26 2020, 15:48:22) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: objects=process_cartons(origin='custom', inputname='mwm_uvex.txt', assign_sets=True, assign_placeholders=True, return_objects=True)                                                                   
[INFO]: ############################################################
[INFO]: ###               STARTING CODE EXECUTION                ###
[INFO]: ############################################################
[INFO]: Ran process_cartons using the following arguments
[INFO]: origin=custom
[INFO]: files_folder=./files/
[INFO]: inputname=mwm_uvex.txt
[INFO]: delim=|
[INFO]: check_exists=False
[INFO]: verb=False
[INFO]: return_objects=True
[INFO]: write_input=False
[INFO]: write_output=False
[INFO]: assign_sets=True
[INFO]: assign_placeholders=True
[INFO]: visualize=False
[INFO]: overwrite=False
[INFO]: all_cartons=False
[INFO]: cartons_name_pattern=None
[INFO]: versions=latest
[INFO]: forced_versions=None
[INFO]: unique_version=None
[INFO]:  
[INFO]: Ran assign_target_info on carton mwm_cb_uvex1
[INFO]: Ran assign_target_info on carton mwm_cb_uvex2
[INFO]: Ran assign_target_info on carton mwm_cb_uvex3
[INFO]: Ran assign_target_info on carton mwm_cb_uvex4
[INFO]: Ran assign_target_info on carton mwm_cb_uvex5

In [2]: objects                                                                                                                                                                                               
Out[2]: 
[<__main__.CartonInfo at 0x2af5d691ad50>,
 <__main__.CartonInfo at 0x2af5d6401cd0>,
 <__main__.CartonInfo at 0x2af5d68e5c90>,
 <__main__.CartonInfo at 0x2af5d6795590>,
 <__main__.CartonInfo at 0x2af5d6718e90>]

In [3]: objects[0].carton,objects[0].magnitude_placeholders                                                                                                                                                   
Out[3]: 
('mwm_cb_uvex1',
 {'GAIA_Invalid',
  'SDSS_-9999.0',
  'SDSS_Invalid',
  'SDSS_None',
  'TMASS_Invalid'})
```

### 4 Visualizing the content of cartons

If one wants to have a human-readable representation of the content of a carton one can use the _visualize\_content_ method.
Here we show to examples on how to use this method, outside and inside _process\_cartons_. In the first example we 'manually'
create the 'uvex1' CartonInfo object corresponding to carton='mwm\_cb\_uvex1', _plan_='0.5.0', and _category\_label_='science'.
Then, we check the content right after instantiation using _visualize\_content_ which indicates us that only the carton dependent
information has been determined for this carton. The method _visualize\_content_ is meant to print and save in log the resulting information
so one has to give as an input an SDSS log object which is defined as 'log' in cartons\_inventory. When running _visualize\_content_
inside the _process\_cartons_ method the log file is initialized with a name based on the input arguments of _process\_cartons_,
but to run it outside _process\_cartons_ one has to initialize the log file doing "log.start_file_logger(\{logfilename\}) which in
this case is ['uvex1.log'](https://github.com/sdss/cartons_inventory/blob/main/python/cartons_inventory/logs/uvex1.log).
The method _visualize\_content_ also uses the optional parameter _width_ to set the width of the message
displayed on screen and in the log which by default is 140 but in this case we used 120.
Then, we get the target dependent information of the carton using the assign_target_info method with
both arguments as True to calculate the parameter sets/ranges and the magnitude placeholders. Then, we run visualize_content()
again and see the full information for this cartons which is also stored in our log file
['uvex1.log'](https://github.com/sdss/cartons_inventory/blob/main/python/cartons_inventory/logs/uvex1.log)

```
[u0955901@operations:cartons_inventory]$ ipython -i cartons.py 
Python 3.7.7 (default, Mar 26 2020, 15:48:22) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: uvex1=CartonInfo('mwm_cb_uvex1','0.5.0','science')                                                                                                                                                    

In [2]: log.start_file_logger('./logs/uvex1.log')                                                                                                                                                             

In [3]: uvex1.visualize_content(log,width=120)                                                                                                                                                                
[INFO]:  
[INFO]: ########################################################################################################################
[INFO]: ###                                          CARTON DEPENDENT INFORMATION                                            ###
[INFO]: ###                                                                                                                  ###
[INFO]: ### carton: mwm_cb_uvex1                                                                                             ###
[INFO]: ### plan: 0.5.0                                                                                                      ###
[INFO]: ### category_label: science                                                                                          ###
[INFO]: ### stage: N/A                                                                                                       ###
[INFO]: ### active: N/A                                                                                                      ###
[INFO]: ### in_targetdb: True                                                                                                ###
[INFO]: ### program: mwm_cb                                                                                                  ###
[INFO]: ### version_pk: 83                                                                                                   ###
[INFO]: ### tag: 0.3.0                                                                                                       ###
[INFO]: ### mapper_pk: 0                                                                                                     ###
[INFO]: ### mapper_label: MWM                                                                                                ###
[INFO]: ### category_pk: 0                                                                                                   ###
[INFO]: ########################################################################################################################
[INFO]: ###                                   The list of values par target parameter has                                    ###
[INFO]: ###                                  not been calculated for this carton, to do so                                   ###
[INFO]: ###                                   first run assign_target_info on this carton                                    ###
[INFO]: ###                                       using calculate_sets=True (default)                                        ###
[INFO]: ########################################################################################################################
[INFO]: ###                                The list of mag placeholers for each photometric                                  ###
[INFO]: ###                               system has not been calculated for this carton yet,                                ###
[INFO]: ###                              to do so first run assign_target_info on this carton                                ###
[INFO]: ###                                using calculate_mag_placeholers=True (not default)                                ###
[INFO]: ########################################################################################################################

In [4]: uvex1.assign_target_info(True,True)                                                                                                                                                                   

In [5]: uvex1.visualize_content(log,width=120)                                                                                                                                                                
[INFO]:  
[INFO]: ########################################################################################################################
[INFO]: ###                                          CARTON DEPENDENT INFORMATION                                            ###
[INFO]: ###                                                                                                                  ###
[INFO]: ### carton: mwm_cb_uvex1                                                                                             ###
[INFO]: ### plan: 0.5.0                                                                                                      ###
[INFO]: ### category_label: science                                                                                          ###
[INFO]: ### stage: N/A                                                                                                       ###
[INFO]: ### active: N/A                                                                                                      ###
[INFO]: ### in_targetdb: True                                                                                                ###
[INFO]: ### program: mwm_cb                                                                                                  ###
[INFO]: ### version_pk: 83                                                                                                   ###
[INFO]: ### tag: 0.3.0                                                                                                       ###
[INFO]: ### mapper_pk: 0                                                                                                     ###
[INFO]: ### mapper_label: MWM                                                                                                ###
[INFO]: ### category_pk: 0                                                                                                   ###
[INFO]: ########################################################################################################################
[INFO]: ###                                      VALUES PER TARGET DEPENDENT PARAMETER                                       ###
[INFO]: ###                                                                                                                  ###
[INFO]: ### cadence_pk: {32, 1, 31}                                                                                          ###
[INFO]: ### cadence_label: {'dark_1x2', 'bright_1x1', 'dark_1x3'}                                                            ###
[INFO]: ### lambda_eff: {5400.0}                                                                                             ###
[INFO]: ### instrument_pk: {0}                                                                                               ###
[INFO]: ### instrument_label: {'BOSS'}                                                                                       ###
[INFO]: ### value range: 1.0 to 3.0                                                                                          ###
[INFO]: ### priority range: 1400 to 1400                                                                                     ###
[INFO]: ########################################################################################################################
[INFO]: ###                                  MAGNITUDE PLACEHOLDERS PER PHOTOMETRIC SYSTEM                                   ###
[INFO]: ###                                                                                                                  ###
[INFO]: ### magnitude_placeholders: {'TMASS_Invalid', 'SDSS_None', 'SDSS_-9999.0', 'SDSS_Invalid', 'GAIA_Invalid'}           ###
[INFO]: ########################################################################################################################
```
In the second example of how to use the _visuzlize\_content_ method we will use it within the _process\_cartons_ method
using _visualize_=True and the other arguments are the same as the ones used in the previous usage example, i.e. use the custom
carton list ['mwm_uvex.txt'](https://github.com/sdss/cartons_inventory/blob/main/python/cartons_inventory/files/custom/mwm_uvex.txt)
to assign the sets/ranges for the target dependent parameters and the magnitude placeholders (only this time we wont return the
objects since we are doing visual inspection). Since this time we are running
within _process\_cartons_  there is no need to initialize the log file which is automatically created with the name
['origin\_custom\_sets\_True\_mags\_True.log'](https://github.com/sdss/cartons_inventory/blob/main/python/cartons_inventory/logs/origin_custom_sets_True_mags_True.log)
and it is written using the default column width of 140. This log file and the message displayed on screen show the content of each
of these 5 cartons after calculating the target dependent parameter sets/ranges and the magnitude placeholders.

```
[u0955901@operations:cartons_inventory]$ ipython -i cartons.py 
Python 3.7.7 (default, Mar 26 2020, 15:48:22) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: process_cartons(origin='custom', inputname='mwm_uvex.txt', assign_sets=True, assign_placeholders=True, visualize=True)                                                                                
[INFO]: ############################################################
[INFO]: ###               STARTING CODE EXECUTION                ###
[INFO]: ############################################################
[INFO]: Ran process_cartons using the following arguments
[INFO]: origin=custom
[INFO]: files_folder=./files/
[INFO]: inputname=mwm_uvex.txt
[INFO]: delim=|
[INFO]: check_exists=False
[INFO]: verb=False
[INFO]: return_objects=False
[INFO]: write_input=False
[INFO]: write_output=False
[INFO]: assign_sets=True
[INFO]: assign_placeholders=True
[INFO]: visualize=True
[INFO]: overwrite=False
[INFO]: all_cartons=False
[INFO]: cartons_name_pattern=None
[INFO]: versions=latest
[INFO]: forced_versions=None
[INFO]: unique_version=None
[INFO]:  
[INFO]: Ran assign_target_info on carton mwm_cb_uvex1
[INFO]:  
[INFO]: ############################################################################################################################################
[INFO]: ###                                                    CARTON DEPENDENT INFORMATION                                                      ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### carton: mwm_cb_uvex1                                                                                                                 ###
[INFO]: ### plan: 0.5.0                                                                                                                          ###
[INFO]: ### category_label: science                                                                                                              ###
[INFO]: ### stage: srd                                                                                                                           ###
[INFO]: ### active: y                                                                                                                            ###
[INFO]: ### in_targetdb: True                                                                                                                    ###
[INFO]: ### program: mwm_cb                                                                                                                      ###
[INFO]: ### version_pk: 83                                                                                                                       ###
[INFO]: ### tag: 0.3.0                                                                                                                           ###
[INFO]: ### mapper_pk: 0                                                                                                                         ###
[INFO]: ### mapper_label: MWM                                                                                                                    ###
[INFO]: ### category_pk: 0                                                                                                                       ###
[INFO]: ############################################################################################################################################
[INFO]: ###                                                VALUES PER TARGET DEPENDENT PARAMETER                                                 ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### cadence_pk: {32, 1, 31}                                                                                                              ###
[INFO]: ### cadence_label: {'dark_1x3', 'dark_1x2', 'bright_1x1'}                                                                                ###
[INFO]: ### lambda_eff: {5400.0}                                                                                                                 ###
[INFO]: ### instrument_pk: {0}                                                                                                                   ###
[INFO]: ### instrument_label: {'BOSS'}                                                                                                           ###
[INFO]: ### value range: 1.0 to 3.0                                                                                                              ###
[INFO]: ### priority range: 1400 to 1400                                                                                                         ###
[INFO]: ############################################################################################################################################
[INFO]: ###                                            MAGNITUDE PLACEHOLDERS PER PHOTOMETRIC SYSTEM                                             ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### magnitude_placeholders: {'SDSS_Invalid', 'TMASS_Invalid', 'SDSS_None', 'GAIA_Invalid', 'SDSS_-9999.0'}                               ###
[INFO]: ############################################################################################################################################
[INFO]: Ran assign_target_info on carton mwm_cb_uvex2
[INFO]:  
[INFO]: ############################################################################################################################################
[INFO]: ###                                                    CARTON DEPENDENT INFORMATION                                                      ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### carton: mwm_cb_uvex2                                                                                                                 ###
[INFO]: ### plan: 0.5.0                                                                                                                          ###
[INFO]: ### category_label: science                                                                                                              ###
[INFO]: ### stage: srd                                                                                                                           ###
[INFO]: ### active: y                                                                                                                            ###
[INFO]: ### in_targetdb: True                                                                                                                    ###
[INFO]: ### program: mwm_cb                                                                                                                      ###
[INFO]: ### version_pk: 83                                                                                                                       ###
[INFO]: ### tag: 0.3.0                                                                                                                           ###
[INFO]: ### mapper_pk: 0                                                                                                                         ###
[INFO]: ### mapper_label: MWM                                                                                                                    ###
[INFO]: ### category_pk: 0                                                                                                                       ###
[INFO]: ############################################################################################################################################
[INFO]: ###                                                VALUES PER TARGET DEPENDENT PARAMETER                                                 ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### cadence_pk: {32, 1, 31}                                                                                                              ###
[INFO]: ### cadence_label: {'dark_1x3', 'dark_1x2', 'bright_1x1'}                                                                                ###
[INFO]: ### lambda_eff: {5400.0}                                                                                                                 ###
[INFO]: ### instrument_pk: {0}                                                                                                                   ###
[INFO]: ### instrument_label: {'BOSS'}                                                                                                           ###
[INFO]: ### value range: 1.0 to 3.0                                                                                                              ###
[INFO]: ### priority range: 1400 to 1400                                                                                                         ###
[INFO]: ############################################################################################################################################
[INFO]: ###                                            MAGNITUDE PLACEHOLDERS PER PHOTOMETRIC SYSTEM                                             ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### magnitude_placeholders: {'SDSS_Invalid', 'TMASS_Invalid', 'SDSS_None', 'GAIA_Invalid', 'SDSS_-9999.0'}                               ###
[INFO]: ############################################################################################################################################
[INFO]: Ran assign_target_info on carton mwm_cb_uvex3
[INFO]:  
[INFO]: ############################################################################################################################################
[INFO]: ###                                                    CARTON DEPENDENT INFORMATION                                                      ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### carton: mwm_cb_uvex3                                                                                                                 ###
[INFO]: ### plan: 0.5.0                                                                                                                          ###
[INFO]: ### category_label: science                                                                                                              ###
[INFO]: ### stage: srd                                                                                                                           ###
[INFO]: ### active: y                                                                                                                            ###
[INFO]: ### in_targetdb: True                                                                                                                    ###
[INFO]: ### program: mwm_cb                                                                                                                      ###
[INFO]: ### version_pk: 83                                                                                                                       ###
[INFO]: ### tag: 0.3.0                                                                                                                           ###
[INFO]: ### mapper_pk: 0                                                                                                                         ###
[INFO]: ### mapper_label: MWM                                                                                                                    ###
[INFO]: ### category_pk: 0                                                                                                                       ###
[INFO]: ############################################################################################################################################
[INFO]: ###                                                VALUES PER TARGET DEPENDENT PARAMETER                                                 ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### cadence_pk: {32, 1, 31}                                                                                                              ###
[INFO]: ### cadence_label: {'dark_1x3', 'dark_1x2', 'bright_1x1'}                                                                                ###
[INFO]: ### lambda_eff: {5400.0}                                                                                                                 ###
[INFO]: ### instrument_pk: {0}                                                                                                                   ###
[INFO]: ### instrument_label: {'BOSS'}                                                                                                           ###
[INFO]: ### value range: 1.0 to 3.0                                                                                                              ###
[INFO]: ### priority range: 1400 to 1400                                                                                                         ###
[INFO]: ############################################################################################################################################
[INFO]: ###                                            MAGNITUDE PLACEHOLDERS PER PHOTOMETRIC SYSTEM                                             ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### magnitude_placeholders: {'SDSS_Invalid', 'SDSS_None', 'GAIA_Invalid', 'TMASS_Invalid'}                                               ###
[INFO]: ############################################################################################################################################
[INFO]: Ran assign_target_info on carton mwm_cb_uvex4
[INFO]:  
[INFO]: ############################################################################################################################################
[INFO]: ###                                                    CARTON DEPENDENT INFORMATION                                                      ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### carton: mwm_cb_uvex4                                                                                                                 ###
[INFO]: ### plan: 0.5.0                                                                                                                          ###
[INFO]: ### category_label: science                                                                                                              ###
[INFO]: ### stage: srd                                                                                                                           ###
[INFO]: ### active: y                                                                                                                            ###
[INFO]: ### in_targetdb: True                                                                                                                    ###
[INFO]: ### program: mwm_cb                                                                                                                      ###
[INFO]: ### version_pk: 83                                                                                                                       ###
[INFO]: ### tag: 0.3.0                                                                                                                           ###
[INFO]: ### mapper_pk: 0                                                                                                                         ###
[INFO]: ### mapper_label: MWM                                                                                                                    ###
[INFO]: ### category_pk: 0                                                                                                                       ###
[INFO]: ############################################################################################################################################
[INFO]: ###                                                VALUES PER TARGET DEPENDENT PARAMETER                                                 ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### cadence_pk: {32, 1, 31}                                                                                                              ###
[INFO]: ### cadence_label: {'dark_1x3', 'dark_1x2', 'bright_1x1'}                                                                                ###
[INFO]: ### lambda_eff: {5400.0}                                                                                                                 ###
[INFO]: ### instrument_pk: {0}                                                                                                                   ###
[INFO]: ### instrument_label: {'BOSS'}                                                                                                           ###
[INFO]: ### value range: 1.0 to 3.0                                                                                                              ###
[INFO]: ### priority range: 1400 to 1400                                                                                                         ###
[INFO]: ############################################################################################################################################
[INFO]: ###                                            MAGNITUDE PLACEHOLDERS PER PHOTOMETRIC SYSTEM                                             ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### magnitude_placeholders: {'SDSS_Invalid', 'TMASS_Invalid', 'SDSS_None', 'GAIA_Invalid', 'SDSS_-9999.0'}                               ###
[INFO]: ############################################################################################################################################
[INFO]: Ran assign_target_info on carton mwm_cb_uvex5
[INFO]:  
[INFO]: ############################################################################################################################################
[INFO]: ###                                                    CARTON DEPENDENT INFORMATION                                                      ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### carton: mwm_cb_uvex5                                                                                                                 ###
[INFO]: ### plan: 0.5.0                                                                                                                          ###
[INFO]: ### category_label: science                                                                                                              ###
[INFO]: ### stage: srd                                                                                                                           ###
[INFO]: ### active: y                                                                                                                            ###
[INFO]: ### in_targetdb: True                                                                                                                    ###
[INFO]: ### program: mwm_cb                                                                                                                      ###
[INFO]: ### version_pk: 83                                                                                                                       ###
[INFO]: ### tag: 0.3.0                                                                                                                           ###
[INFO]: ### mapper_pk: 0                                                                                                                         ###
[INFO]: ### mapper_label: MWM                                                                                                                    ###
[INFO]: ### category_pk: 0                                                                                                                       ###
[INFO]: ############################################################################################################################################
[INFO]: ###                                                VALUES PER TARGET DEPENDENT PARAMETER                                                 ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### cadence_pk: {10}                                                                                                                     ###
[INFO]: ### cadence_label: {'bright_3x1'}                                                                                                        ###
[INFO]: ### lambda_eff: {16000.0}                                                                                                                ###
[INFO]: ### instrument_pk: {1}                                                                                                                   ###
[INFO]: ### instrument_label: {'APOGEE'}                                                                                                         ###
[INFO]: ### value range: 3.0 to 3.0                                                                                                              ###
[INFO]: ### priority range: 1400 to 1400                                                                                                         ###
[INFO]: ############################################################################################################################################
[INFO]: ###                                            MAGNITUDE PLACEHOLDERS PER PHOTOMETRIC SYSTEM                                             ###
[INFO]: ###                                                                                                                                      ###
[INFO]: ### magnitude_placeholders: {'SDSS_Invalid', 'SDSS_None', 'SDSS_-9999.0'}                                                                ###
[INFO]: ############################################################################################################################################
```

### 5 Getting a dataframe with all the targets from a carton

If we want the different parameters for all the targets from a carton and not just listing the different values found for that parameter in a carton,
one can use the method _return\_target\_dataframe_ on a CartonInfo object corresponding to a specific carton. This method returns a Pandas DataFrame
with multiple parameters and one entry for each target in the carton. For example in the following block we create the CartonInfo object for the
'ops_apogee\_std' carton, and then we return the Pandas DataFrame corresponding to the targets in that carton. Once we have the DataFrame we can
check information at the individual target level. For example, in here we calculate the average g-r and r-i colors for all the targets where gri
magnitudes are available. If we want to analyze further the content of the carton we can save the DataFrame into a .csv file like here where we
created file ['apogee\_stds\_content.csv'](https://github.com/sdss/cartons_inventory/blob/main/python/cartons_inventory/files/custom/apogee_stds_content.csv)
(here we only saved the first 1000 rows to avoid uploading an unnecesarily large file).

```
[u0955901@operations:cartons_inventory]$ ipython -i cartons.py 
Python 3.7.7 (default, Mar 26 2020, 15:48:22) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: apogee_stds=CartonInfo('ops_std_apogee','0.5.0','standard_apogee')                                                                                                                                      

In [2]: df = apogee_stds.return_target_dataframe()                                                                                                                                                              

In [3]: ind_valid = df['g'].notnull() & df['r'].notnull() & df['i'].notnull()                                                                                                                                   

In [4]: np.average((df['g']-df['r'])[ind_valid]), np.average((df['r']-df['i'])[ind_valid])                                                                                                                      
Out[4]: (0.19343229220832064, 0.11288633405227849)

In [5]: df[:1000].to_csv('./files/custom/apogee_stds_content.csv')
```

### 6 Saving the information from a group of cartons in a .csv file
