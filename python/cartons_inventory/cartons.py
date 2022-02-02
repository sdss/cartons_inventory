import csv
import time as time

import numpy as np
import pandas as pd
from sdssdb.peewee.sdss5db.targetdb import (Cadence, Carton, CartonToTarget,
                                            Category, Instrument, Magnitude,
                                            Mapper, Version)

import cartons_inventory


def get_range(set_p):
    """Gets the total range of a given set."""
    if set_p is None:
        minp, maxp = None, None
    else:
        minp, maxp = np.min(list(set_p)), np.max(list(set_p))
    return minp, maxp


def set_or_none(list_l):
    """Function to avoid list->set transformation to return set={None} or set={}."""
    res = set(list_l)
    if res == {None} or res == {}:
        res = None
    return res


def check_mag_outliers(datafr, bands, systems):
    """Returns a list with all the types of outliers found for each photometric system.

    Parameters
    ----------
    datafr: Pandas DataFrame containing the magnitudes from different photometric systems
        for the stars in a given carton
    bands: total list of bands to search each belonging to a given photometric system
    system: Photometric system to which each band listed belongs to. The options are
        'SDSS', TMASS', and 'GAIA'. The system to which band belongs is defined by the index
        of the band in the list (i.e. band[ind] belongs to systems[ind])

    Returns
    -------
    outs_list: A set of strings where each string starts with the photometric system,
        then an underscore and finally the type of magnitude outlier that at least one
        magnitude of the corresponding system has.
        The type of outliers are:
            None: For empy entries
            Invalid: For Nan's and infinite values
            Numbers: For values brighter than -9, dimmer than 50, or equal to zero. In this cases
            the number itself is returned as the outlier type.
       For example if a carton contains stars with g=-99.9, r=-99.9, j=None, and bp=Inf.
       This function will return {'SDSS_-99.9','TMASS_None','GAIA_Invalid'}

    """
    out_bands, out_systems = [], []
    for ind_band in range(len(bands)):
        maglist = datafr[bands[ind_band]]
        nonempty_maglist = [el for el in maglist if el is not None]
        magarr_filled = np.array(nonempty_maglist)
        ind_valid = np.where(np.isfinite(magarr_filled))[0]
        magarr_valid = magarr_filled[ind_valid]
        ind_out = np.where((magarr_valid < -9) | (magarr_valid > 50) | (magarr_valid == 0))[0]
        out_band = list(set([str(magarr_valid[indice]) for indice in ind_out]))
        if len(maglist) > len(nonempty_maglist):
            out_band.append('None')
        if len(magarr_filled) > len(magarr_valid):
            out_band.append('Invalid')
        n_out = len(out_band)
        out_bands = out_bands + out_band
        out_systems = out_systems + [systems[ind_band]] * n_out
    out = set_or_none([out_systems[idx] + '_' + out_bands[idx] for idx in range(len(out_bands))])
    return out


def gets_carton_list_file_info(carton_list_filename, header_length=2, delimiter='|'):
    """Get the necessary information from the input carton list file."""
    cat = np.loadtxt(carton_list_filename, dtype='str',
                     skiprows=header_length, delimiter=delimiter)
    cartons = [str.strip(cat[ind, 0]) for ind in range(len(cat))]
    plans = [str.strip(cat[ind, 1]) for ind in range(len(cat))]
    tags = [str.strip(cat[ind, 2]) for ind in range(len(cat))]
    return cartons, plans, tags


def query_carton_info(name, plan, tag):
    """Gets the targetdb information from a given version of a carton.


    Parameters
    ----------
    name: carton name
    plan: carton plan in targetdb.version table
    tag: carton tag in targetdb.version table

    Returns
    -------
    df: Pandas dataframe with necessary targetdb information. For the code to work
        this function needs to retrieve all the database fields needed to create the
        parameters defined in the configuration file column_names dictionary and all the
        magnitudes defined in the configuration file bands dictionary.

    """
    Car = Carton.alias()
    CarTar = CartonToTarget.alias()
    Cad = Cadence.alias()
    Inst = Instrument.alias()
    Categ = Category.alias()
    Map = Mapper.alias()
    Mag = Magnitude.alias()
    query = (
        Car
        .select(Map.label.alias('mapper_label'), Categ.label.alias('category_label'),
                Inst.label.alias('instrument_label'), Car.carton, Car.program, Car.version_pk,
                Car.category_pk.alias('category_pk'), Car.mapper_pk.alias('mapper_pk'),
                CarTar.lambda_eff, CarTar.cadence_pk.alias('cadence_pk'), CarTar.priority,
                CarTar.instrument_pk.alias('instrument_pk'), CarTar.value, Version.plan,
                Version.tag, Cad.label.alias('cadence_label'), Mag.g, Mag.r, Mag.i,
                Mag.z, Mag.h, Mag.j, Mag.k, Mag.bp, Mag.rp, Mag.gaia_g)
        .join(CarTar, on=(CarTar.carton_pk == Car.pk))
        .join(Version, on=(Version.pk == Car.version_pk))
        .join(Cad, 'LEFT JOIN', on=(Cad.pk == CarTar.cadence_pk))
        .join(Inst, 'LEFT JOIN', CarTar.instrument_pk == Inst.pk)
        .join(Categ, 'LEFT JOIN', Car.category_pk == Categ.pk)
        .join(Map, 'LEFT JOIN', Car.mapper_pk == Map.pk)
        .join(Mag, 'LEFT JOIN', CarTar.pk == Mag.carton_to_target_pk)
        .where(Car.carton == name)
        .where((Version.plan == plan) & (Version.tag == tag))
    )
    df = pd.DataFrame(list(query.dicts()))
    return df


def analyze_carton_query(carton_df):
    """Transforms the dataframe from query_carton_info into a list of string and sets to be saved.

    Parameters
    ----------
    carton_df: Pandas dataframe obtained with query_carton_info. This dataframe has to contain
        all the database fields in the configuration file column_names dictionary and all the
        magnitudes bands dictionary.



    Returns
    -------
    curr_cartoninfo: A list of string and sets each one associated with a given parameter of the
        carton using the information contained in the configuration file (cfg).
        For each parameter in cfg['db_fields']['sets'] creates a set with all the different values
        found for the stars in the carton. Then, calculates the range lists (parameter)_min"
        and "(parameter)_max" for each parameter in cfg['db_fields']['set_range']
        Then, for each parameter in cfg['db_fields']['carton_dependent'] calculates the (single)
        value associated with the carton.
        Then it creates the list of magnitude placeholders preent in each photometric system
        (SDSS, GAIA, TMASS), using check_mag_outliers.
        Finally it covers cfg[column_names] dictionary and for each key retrieves the variable
        previously defined with that name and appends it to the final output list.
        Since the function header uses the same cfg[column_names] to create the header
        each variable name defined for a given key is associated with the output column name
        cfg[column_names][key]. For example the verion variable is stored as "verion_pk".

    """
    cfg = cartons_inventory.config

    set_names = cfg['db_fields']['sets']
    set_range_names = cfg['db_fields']['set_ranges']
    for set_name in set_names:
        locals()[set_name] = set_or_none(carton_df[set_name])
    for set_name in set_range_names:
        locals()[set_name + '_min'], locals()[set_name + '_max'] = get_range(locals()[set_name])
    carton_parameter_names = cfg['db_fields']['carton_dependent']
    first_entry = carton_df.iloc[0]
    for carton_parname in carton_parameter_names:
        locals()[carton_parname] = first_entry[carton_parname]

    bands = cfg['bands']
    mags_names = [el for key in bands.keys() for el in bands[key]]
    systems_names = [key for key in bands.keys() for el in bands[key]]
    magnitude_placeholders_list = check_mag_outliers(carton_df, mags_names, systems_names)

    curr_cartoninfo = []
    colnames = cfg['column_names']
    for colkey in colnames.keys():
        curr_cartoninfo.append(locals()[colkey])
    return curr_cartoninfo


def create_header(conf):
    """Creates a header based on the configuration file dictionary."""
    head = []
    colnames = conf['column_names']
    for colkey in colnames.keys():
        head.append(colnames[colkey])
    return head


def write_csv(inputname='', outputname='', onlydo=False, delim='|'):
    """Creates a .csv file with the targetdb information of each carton.

    The function writes the file with name outputname containing all the information needed
    for each carton listed in file inputname. The full list of parameters stored per carton
    is defined in the configuration file column_names dictionary, where the keys have the
    variable names defined in the code and the values the name used to be stored in the .csv

    Parameters
    ----------
    inputname: List of cartons to be queried along with their associated plans and tags.
        If the parameter is not defined it uses the inputname defined in the configuration file

    outputname: Output name of final .csv file. If the parameter is not defined it uses the
        outputname defined in the configuration file
    onlydo: Number of cartons to cover from the file inputname. If it is not defined it used
        the full list of cartons in the file
    delim: Delimiter to use in the output .csv file. If not defined it used "|"
    """

    ti = time.time()
    cfg = cartons_inventory.config
    filenames = cfg['filenames']
    if inputname == '':
        inputname = filenames['input_name']
    if outputname == '':
        outputname = filenames['output_name']
    cartons, plans, tags = gets_carton_list_file_info(carton_list_filename=inputname)
    if onlydo:
        cartons, plans, tags = cartons[onlydo], plans[onlydo], tags[onlydo]
    f = open(outputname, 'w')
    writer = csv.writer(f, delimiter=delim)
    file_header = create_header(cfg)
    writer.writerow(file_header)
    ncartons = len(cartons)

    for ind in range(ncartons):
        print('Running carton', ind + 1, '/', ncartons, cartons[ind])
        carton_dataframe = query_carton_info(cartons[ind], plans[ind], tags[ind])
        print('Found', len(carton_dataframe), 'stars\n')
        curr_cartoninfo = analyze_carton_query(carton_dataframe)
        writer.writerow(curr_cartoninfo)
    f.close()
    tf = time.time()
    dt = tf - ti
    st_dt = '%5.1f' % (dt / 60.)
    print(' ')
    print('The script took', st_dt, 'minutes to check', ncartons, 'cartons')
