import csv
import inspect
import os

import numpy as np
import pandas as pd
from astropy.io import ascii
from sdssdb.peewee.sdss5db.targetdb import (Cadence, Carton, CartonToTarget,
                                            Category, Instrument, Magnitude,
                                            Mapper, Version)

import cartons_inventory
from cartons_inventory import log, main


Car = Carton.alias()
CarTar = CartonToTarget.alias()
Cad = Cadence.alias()
Inst = Instrument.alias()
Categ = Category.alias()
Map = Mapper.alias()
Mag = Magnitude.alias()


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
    `list`
        A set of strings where each string starts with the photometric system,
        then an underscore and finally the type of magnitude outlier that at least one
        magnitude of the corresponding system has.
        The type of outliers are:
            None: For empty entries
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
    out = main.set_or_none([out_systems[idx] + '_' + out_bands[idx]
                           for idx in range(len(out_bands))])
    return out


def gets_carton_info(carton_list_filename, header_length=1, delimiter='|'):
    """Get the necessary information from the input carton list file."""
    cat = np.loadtxt(carton_list_filename, dtype='str',
                     skiprows=header_length, delimiter=delimiter)
    cartons = [str.strip(cat[ind, 1]) for ind in range(len(cat))]
    plans = [str.strip(cat[ind, 2]) for ind in range(len(cat))]
    categories = [str.strip(cat[ind, 3]) for ind in range(len(cat))]
    stages = [str.strip(cat[ind, 4]) for ind in range(len(cat))]
    actives = [str.strip(cat[ind, 5]) for ind in range(len(cat))]
    return cartons, plans, categories, stages, actives


class CartonInfo(object):

    cfg = cartons_inventory.config

    def __init__(self, carton, plan, category_label, stage='N/A', active='N/A'):
        self.carton = carton
        self.plan = plan
        self.category_label = category_label
        self.stage = stage
        self.active = active

        self.mapper_label, self.program, self.version_pk = [], [], []
        self.tag, self.mapper_pk, self.category_pk = [], [], []
        self.in_targetdb = False
        self.sets_calculated = False
        self.mag_placeholders_calculated = False

        self.assign_carton_info()

    def assign_carton_info(self):

        cfg = cartons_inventory.config

        basic_info = (
            Car
            .select(Map.label.alias('mapper_label'), Car.version_pk.alias('version_pk'),
                    Car.category_pk.alias('category_pk'), Car.mapper_pk.alias('mapper_pk'),
                    Version.tag, Car.program)
            .join(Version, on=(Version.pk == Car.version_pk))
            .join(Categ, 'LEFT JOIN', Car.category_pk == Categ.pk)
            .join(Map, 'LEFT JOIN', Car.mapper_pk == Map.pk)
            .where(Car.carton == self.carton)
            .where(Version.plan == self.plan)
            .where(Categ.label == self.category_label).dicts()
        )

        if len(basic_info) > 0:  # If the carton is in targetdb assigns carton info
            res = basic_info[0]
            carton_parameter_names = cfg['db_fields']['carton_dependent']
            for parameter in carton_parameter_names:
                setattr(self, parameter, res[parameter])
            self.in_targetdb = True

        if self.in_targetdb is False:  # If not in targetdb still tries to get the Version info
            query_version = (
                Version
                .select(Version.tag, Version.pk)
                .where(Version.plan == self.plan).dicts()
            )
            if len(query_version) > 0:
                ver_info = query_version[0]
                self.tag = ver_info['tag']
                self.version_pk = ver_info['pk']

    def build_query_target(self):

        query_target = (
            Car
            .select(Inst.label.alias('instrument_label'), CarTar.cadence_pk.alias('cadence_pk'),
                    CarTar.lambda_eff, CarTar.instrument_pk.alias('instrument_pk'),
                    CarTar.priority, CarTar.value, Cad.label.alias('cadence_label'), Mag.g, Mag.r,
                    Mag.i, Mag.z, Mag.h, Mag.j, Mag.k, Mag.bp, Mag.rp, Mag.gaia_g)
            .join(Version, on=(Version.pk == Car.version_pk))
            .join(CarTar, on=(CarTar.carton_pk == Car.pk))
            .join(Cad, 'LEFT JOIN', on=(Cad.pk == CarTar.cadence_pk))
            .join(Inst, 'LEFT JOIN', CarTar.instrument_pk == Inst.pk)
            .join(Mag, 'LEFT JOIN', CarTar.pk == Mag.carton_to_target_pk)
            .where(Car.carton == self.carton)
            .where((Version.plan == self.plan) & (Version.tag == self.tag))
        )

        return query_target

    def return_target_dataframe(self):
        if not self.in_targetdb:
            print(self.carton, 'not in targetdb so we cant return the target dataframe')
            return
        target_query = self.build_query_target()
        df = pd.DataFrame(list(target_query.dicts()))
        return df

    def assign_target_info(self, calculate_sets=True, calculate_mag_placeholders=False):

        dataframe_created = False
        if not self.in_targetdb:
            print('carton', self.carton, 'version_pk', self.version_pk,
                  'category_label', self.category_label, 'not found in database',
                  'so we cant assign target info')
            return

        if calculate_sets:
            if self.sets_calculated:
                print('Sets already calculated for this carton')
            else:
                dataframe = self.return_target_dataframe()
                dataframe_created = True
                target_parameters = self.cfg['db_fields']
                set_names = target_parameters['sets']
                set_range_names = target_parameters['set_ranges']

                for set_name in set_names:
                    setattr(self, set_name, main.set_or_none(dataframe[set_name]))
                for set_name in set_range_names:
                    set_range = main.get_range(getattr(self, set_name))
                    setattr(self, set_name + '_min', set_range[0])
                    setattr(self, set_name + '_max', set_range[1])
                self.sets_calculated = True

        if calculate_mag_placeholders:
            if self.mag_placeholders_calculated:
                print('Magnitude placeholders already caclulated for this carton')
            else:
                if not dataframe_created:
                    dataframe = self.return_target_dataframe()
                    dataframe_created = True
                bands = self.cfg['bands']
                mags_names = [el for key in bands.keys() for el in bands[key]]
                systems_names = [key for key in bands.keys() for el in bands[key]]
                self.magnitude_placeholders = check_mag_outliers(dataframe, mags_names,
                                                                 systems_names)
                self.mag_placeholders_calculated = True

    def check_existence(self, log, verbose=True):

        df_data = {}
        msg = ''
        if self.in_targetdb is False:
            colnames = ['carton', 'plan', 'category_label', 'stage',
                        'active', 'tag', 'version_pk', 'in_targetdb']
            for index in range(len(colnames)):
                colname = colnames[index]
                locals()[colname] = []
                locals()[colname].append(getattr(self, colname))

            alternatives_info = (
                Car
                .select(Car.carton, Version.plan, Car.version_pk.alias('version_pk'),
                        Categ.label.alias('category_label'), Version.tag, Car.program)
                .join(Version, on=(Version.pk == Car.version_pk))
                .join(Categ, 'LEFT JOIN', Car.category_pk == Categ.pk)
                .where(Car.carton == self.carton).dicts()
            )
            if len(alternatives_info) == 0:
                msg = 'Wargning: Carton' + self.carton + ' not in targetdb'\
                    'not in targetdb and there is no carton with that name'
            else:
                msg = 'Carton ' + self.carton + ' not in targetdb, to avoid this you can replace '\
                    'the next\nline with the information that follows '\
                    'replacing (stage) and (active) if it corresponds\n'
                msg += '|' + self.carton.rjust(41) + ' | ' + self.plan.rjust(6) + ' | '\
                       + self.category_label.rjust(20) + ' |'\
                       + self.stage.rjust(6) + ' | ' + self.active.rjust(6) + ' | '\
                       + '--> Replace this line\n'
                for ind in range(len(alternatives_info)):
                    res = alternatives_info[ind]
                    res['stage'], res['active'] = 'N/A', 'N/A'
                    for colname in colnames[:-1]:
                        locals()[colname].append(res[colname])
                    locals()['in_targetdb'].append(True)
                    msg += '|' + res['carton'].rjust(41) + ' | ' + res['plan'].rjust(6) + ' | '\
                        + res['category_label'].rjust(20) + ' |   N/A |    N/A |\n'
            for index in range(len(colnames)):
                df_data[colnames[index]] = locals()[colnames[index]]

        if verbose is True and msg != '':
            log.debug(msg)

        df = pd.DataFrame(data=df_data)
        return df

    def visualize_content(self, log, width=140):

        pars = cartons_inventory.config['db_fields']
        log.info(' ')
        log.info('#' * width)
        print_centered_msg('CARTON DEPENDENT INFORMATION', width, log)
        print_centered_msg(' ', width, log)
        for par in ['carton'] + pars['input_dependent'] + ['in_targetdb']:
            self.print_param(par, width, log)
        for par in pars['carton_dependent']:
            self.print_param(par, width, log)
        log.info('#' * width)

        if not self.in_targetdb:
            print_centered_msg('Since the carton is not in targetdb', width, log)
            print_centered_msg('this is all the information we can get', width, log)
            log.info('#' * width)
            return

        if not(self.sets_calculated):
            print_centered_msg('The list of values par target parameter has', width, log)
            print_centered_msg('not been calculated for this carton, to do so', width, log)
            print_centered_msg('first run assign_target_info on this carton', width, log)
            print_centered_msg('using calculate_sets=True (default)', width, log)
            log.info('#' * width)

        else:
            print_centered_msg('VALUES PER TARGET DEPENDENT PARAMETER', width, log)
            print_centered_msg(' ', width, log)
            for par in [el for el in pars['sets'] if el not in pars['set_ranges']]:
                self.print_param(par, width, log)
            for par in pars['set_ranges']:
                self.print_range(par, width, log)
            log.info('#' * width)

        if not(self.mag_placeholders_calculated):
            print_centered_msg('The list of mag placeholers for each photometric', width, log)
            print_centered_msg('system has not been calculated for this carton yet,', width, log)
            print_centered_msg('to do so first run assign_target_info on this carton', width, log)
            print_centered_msg('using calculate_mag_placeholers=True (not default)', width, log)
            log.info('#' * width)

        else:
            print_centered_msg('MAGNITUDE PLACEHOLDERS PER PHOTOMETRIC SYSTEM', width, log)
            print_centered_msg(' ', width, log)
            self.print_param('magnitude_placeholders', width, log)
            log.info('#' * width)

    def print_param(self, par, width, log):
        log.info('### ' + par + ': ' + str(getattr(self, par)).ljust(width - len(par) - 10) +
                 ' ###')

    def print_range(self, par, width, log):
        left_msg = str(getattr(self, par + '_min'))
        right_msg = str(getattr(self, par + '_max'))
        log.info('### ' + par + ' range: ' + left_msg + ' to ' + right_msg +
                 ' ' * (width - len(left_msg) - len(right_msg) - len(par) - 20) + ' ###')


def print_centered_msg(st, width, log):
    left = round((width - len(st) - 7) / 2.0)
    right = width - len(st) - 7 - left
    log.info('###' + ' ' * left + st + ' ' * right + ' ###')


def create_header(conf):
    """Creates a header based on the configuration file dictionary."""
    head = []
    colnames = conf['column_names']
    for colkey in colnames.keys():
        head.append(colnames[colkey])
    return head


def process_cartons(origin='rsconfig', files_folder='./files/', inputname=None,
                    delim='|', check_exists=True, verb=True, return_objects=False,
                    write_input=False, write_output=True, assign_sets=True,
                    assign_placeholders=False, visualize=False, overwrite=False,
                    all_cartons=True, cartons_name_pattern=None, versions='latest',
                    forced_versions=None, unique_version=None):

    cfg = cartons_inventory.config
    # Check that we have a valid origin parameter
    assert origin in ['targetdb', 'rsconfig', 'custom'], f'{origin!r} is not a valid'\
        ' option for origin parameter'

    fullfolder = files_folder + origin + '/'

    # If an input file is used check that it exists and that we are not trying to overwrite it
    if origin in ['rsconfig', 'custom']:

        assert write_input is False, 'write_input=True only available for origin=\'targetdb\''
        assert inputname is not None, f'for origin={origin!r} an inputname has to be provided'
        inputread_filename = fullfolder + inputname
        assert os.path.isfile(inputread_filename), 'file: ' + \
            os.path.realpath(inputread_filename) + '\n' + f' required for origin={origin!r}'\
            f'and inputname={inputname!r} but file doesn\'t exist'

        outputbase_filename = fullfolder + 'Info_' + inputname.replace('.txt', '')

    if origin == 'targetdb':

        # First check if the input arguments are valid
        assert check_exists is False, 'check_exists=True option only valid for origin'\
            '\'rsconfig\' or \'custom\''
        assert versions in ['latest', 'all', 'single'], f'{versions!r} is not a valid option'\
            ' for versions parameter'
        assert forced_versions is None or type(forced_versions) == dict, 'if used, '\
            f'forced_versions has to be type=dict not type={type(forced_versions)}'
        assert all_cartons is True or cartons_name_pattern is not None, ' carton_name_pattern'\
            ' needed when all_cartons=False (e.g. cartons_name_pattern=\'bhm_rm_*\')'
        assert versions != 'single' or type(unique_version) == int, 'If versions=\'single\' then'\
            ' unique version has to be an integer'
        assert write_input is True or write_output is False, 'To create an output file'\
            ' an input file has to be created as well to help keep record'

        # Then I calculate the base name for input and output files based on selection criteria
        if all_cartons is True:
            basename = 'Cartons_all'
        if all_cartons is False:
            basename = 'Cartons_sample'
        if versions != 'unique':
            basename += '_Versions_' + versions
        if versions == 'unique':
            basename += '_Version_' + str(unique_version)
        if forced_versions is not None:
            basename += '_and_forced'

        inputwrite_filename = fullfolder + basename + '.txt'
        outputbase_filename = fullfolder + 'Info_' + basename

        if write_input is True and overwrite is False:
            assert not os.path.isfile(inputwrite_filename), 'input file '\
                f'{os.path.realpath(inputwrite_filename)}\n already exists and overwrite=False'

    # If write_output set the final output_filename and check overwritting
    if write_output is True:
        assert assign_sets is True or assign_placeholders is True, 'to create an output .csv'\
            'at least one of assign_sets or assign_placeholders has to be True'
        if assign_sets is True and assign_placeholders is False:
            output_filename = outputbase_filename + '_sets.csv'
        if assign_sets is False and assign_placeholders is True:
            output_filename = outputbase_filename + '_magplaceholers.csv'
        if assign_sets is True and assign_placeholders is True:
            output_filename = outputbase_filename + '_all.csv'

        if overwrite is False:
            assert not os.path.isfile(output_filename), 'output file '\
                f'{os.path.realpath(output_filename)}\n already exists and overwrite=False'

    if origin in ['rsconfig', 'custom']:
        cartons, plans, categories, stages, actives = gets_carton_info(inputread_filename)

    if origin == 'targetdb':
        if all_cartons is True:
            pattern = '%%'
        if all_cartons is False:
            pattern = cartons_name_pattern.replace('*', '%')

        cartons_list = (
            Car
            .select(Car.carton, Version.pk.alias('version_pk'), Version.plan,
                    Categ.label.alias('category_label'))
            .join(Version, on=(Version.pk == Car.version_pk))
            .join(Categ, 'LEFT JOIN', Car.category_pk == Categ.pk)
            .where(Car.carton ** pattern)
            .dicts()
        )

        cart_results = pd.DataFrame(cartons_list)
        cartons_unique = np.sort(list(set(cart_results['carton'])))
        all_indices = []
        for name in cartons_unique:
            indcart = np.where(cart_results['carton'] == name)[0]
            if forced_versions and name in forced_versions.keys():
                inds = np.where((cart_results['carton'] == name) &
                                (cart_results['version_pk'] == forced_versions[name]))[0]
            elif versions == 'single':
                inds = np.where((cart_results['carton'] == name) &
                                (cart_results['version_pk'] == unique_version))[0]
            elif versions == 'all':
                inds = indcart
            elif versions == 'latest':
                max_version = np.max(cart_results['version_pk'][indcart])
                inds = np.where((cart_results['carton'] == name) &
                                (cart_results['version_pk'] == max_version))[0]
            all_indices += list(inds)
        assert len(all_indices) > 0, 'There are no carton/version_pk pairs matching the selection'\
            ' criteria used'
        carts_sel = cart_results.iloc[all_indices]
        cartons = carts_sel['carton'].values.tolist()
        plans = carts_sel['plan'].values.tolist()
        categories = carts_sel['category_label'].values.tolist()
        stages, actives = ['N/A'] * len(carts_sel), ['N/A'] * len(carts_sel)

    # Here we start the corresponding log based on the origin, assign_sets,
    # and assign_placeholders value
    print(f'./logs/origin_{origin}_sets_{assign_sets}_mags_{assign_placeholders}.log')
    log.start_file_logger(f'./logs/origin_{origin}_sets_{assign_sets}'
                          f'_mags_{assign_placeholders}.log')
    log.info('#' * 60)
    print_centered_msg('STARTING CODE EXECUTION', 60, log)
    log.info('#' * 60)
    log.info('Ran process_cartons using the following arguments')
    signature = inspect.signature(process_cartons)
    # First thing we log is the parameters used in process_cartons function
    for param in signature.parameters.keys():
        arg = locals()[param]
        log.info(f'{param}={arg}')
    log.info(' ')

    # Here we write an input-like file if requested
    if origin == 'targetdb' and write_input is True:
        data = np.transpose([cartons, plans, categories, stages, actives])
        ascii.write(data, inputwrite_filename, format='fixed_width',
                    names=['carton', 'plan', 'category', 'stage', 'active'],
                    overwrite=overwrite)
        log.info(f'Wrote file {inputwrite_filename}')

    # If write_output then we prepare the .csv writer
    if write_output is True:
        fields = cfg['db_fields']
        f = open(output_filename, 'w')
        writer = csv.writer(f, delimiter=delim)
        columns = ['carton'] + fields['input_dependent'] + fields['carton_dependent']
        if assign_sets is True:
            new_cols = [x for x in fields['sets'] if x not in fields['set_ranges']]
            columns += new_cols
            for col in fields['set_ranges']:
                columns += [col + '_min', col + '_max']
        if assign_placeholders is True:
            columns += ['magnitude_placeholders']
        writer.writerow(columns)

    # Here we start the actual processing of the cartons
    objects, diffs = [], []
    for index in range(len(cartons)):

        # First we instantiate the CartonInfo objects with the information we have
        obj = CartonInfo(cartons[index], plans[index], categories[index],
                         stages[index], actives[index])
        objects.append(obj)

        # If check_exists we run check_existence on the cartons and return the diff dataframe
        if check_exists:
            output = None
            diff = obj.check_existence(log, verbose=verb)
            if len(diff) > 0:
                diffs.append(diff)
            if index == len(cartons) - 1:
                log.info('Ran check_existence to compare input file '
                         f'{inputname} with targetdb content')
                if len(diffs) > 0:
                    output = pd.concat(diffs)
                return output
            continue

        if obj.in_targetdb is False:
            log.debug(f'carton={obj.carton} plan={obj.plan} version_pk={obj.version_pk}'
                      f'category={obj.category_label} not found in targetdb')
        # Here we assign sets and or mag placeholders info based on input arguments
        # And we visualize and write in output .csv if it corresponds
        if obj.in_targetdb is True:
            obj.assign_target_info(calculate_sets=assign_sets,
                                   calculate_mag_placeholders=assign_placeholders)
            objects.append(obj)
            log.info(f'Ran assign_target_info on carton {obj.carton}')

            if visualize is True:
                obj.visualize_content(log)

            if write_output:
                curr_info = [getattr(obj, attr) for attr in columns]
                writer.writerow(curr_info)
                log.info(f'wrote row to output csv for carton={obj.carton}'
                         f' ({index + 1}/{len(cartons)})')

    if write_output is True:
        f.close()
        log.info(f'Saved output file={output_filename}')

    if return_objects is True:
        return objects
