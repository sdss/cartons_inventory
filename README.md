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
