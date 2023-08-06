""" Utility methods

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-08-06
:Copyright: 2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from .data_model import KISAO_ALGORITHM_MAP
from biosimulators_utils.config import Config  # noqa: F401
from biosimulators_utils.model_lang.xpp.validation import get_xpp_input_configuration_from_directory
from biosimulators_utils.report.data_model import VariableResults
from biosimulators_utils.sedml.data_model import ModelAttributeChange, UniformTimeCourseSimulation, Symbol, Variable  # noqa: F401
from biosimulators_utils.simulator.utils import get_algorithm_substitution_policy
from biosimulators_utils.warnings import warn, BioSimulatorsWarning
from kisao.data_model import AlgorithmSubstitutionPolicy, ALGORITHM_SUBSTITUTION_POLICY_LEVELS
from kisao.utils import get_preferred_substitute_algorithm_by_ids
import collections  # noqa: F401
import decimal
import os
import pandas
import re
import subprocess
import tempfile

__all__ = [
    'get_simulation_method_kisao_map',
    'validate_variables',
    'apply_model_changes',
    'set_up_simulation',
    'write_xpp_parameter_file',
    'write_xpp_initial_conditions_file',
    'write_method_to_xpp_simulation_file',
    'exec_xpp_simulation',
    'get_results_of_sed_variables',
]


def get_simulation_method_kisao_map():
    """ Invert the map from KiSAO ids to simulation methods

    Returns:
        :obj:`dict`: inverted map
    """
    simulation_method_kisao_map = {}
    for alg_props in KISAO_ALGORITHM_MAP.values():
        simulation_method_kisao_map[alg_props['id']] = {
            'kisao_id': alg_props['kisao_id'],
            'parameters': {
            },
        }
        for param_props in alg_props['parameters'].values():
            if param_props['enabled']:
                simulation_method_kisao_map[alg_props['id']]['parameters'][param_props['id']] = param_props['kisao_id']
    return simulation_method_kisao_map


def validate_variables(xpp_model, sed_variables):
    """ Validate the SED variables for a XPP model

    Args:
        xpp_model (:obj:`dict`): XPP model
        sed_variables (:obj:`list` of :obj:`Variable`): SED variables
    """
    variable_ids = [key.upper() for key in (xpp_model.get('initial_conditions', None) or {}).keys()]
    aux_variable_ids = [key.upper() for key in (xpp_model.get('auxiliary_variables', None) or {}).keys()]

    invalid_symbols = []
    invalid_targets = []
    for sed_variable in sed_variables:
        if sed_variable.symbol:
            if sed_variable.symbol != Symbol.time.value:
                invalid_symbols.append(sed_variable.symbol)

        else:
            target = sed_variable.target.upper()
            if target not in variable_ids and target not in aux_variable_ids:
                invalid_targets.append(sed_variable.target)

    if invalid_symbols:
        msg = 'The following symbols are not supported:\n  - {}\n\nThe following symbols are supported:\n  - {}'.format(
            '\n  - '.join(sorted(invalid_symbols)),
            '\n  - '.join([Symbol.time.value]),
        )
        raise NotImplementedError(msg)

    if invalid_targets:
        msg = 'The following targets are not supported:\n  - {}\n\nThe following targets are supported:\n  - {}'.format(
            '\n  - '.join(sorted(invalid_targets)),
            '\n  - '.join(sorted(list(variable_ids) + list(aux_variable_ids))),
        )
        raise ValueError(msg)


def apply_model_changes(xpp_model, sed_changes):
    """ Validate the SED variables for a XPP model

    Args:
        xpp_model (:obj:`dict`): XPP model
        sed_changes (:obj:`list` of :obj:`ModelAttributeChange`): SED model attribute changes
    """
    parameters = xpp_model.get('parameters', None) or {}
    variables = xpp_model.get('initial_conditions', None) or {}
    xpp_model['parameters'] = parameters
    xpp_model['initial_conditions'] = variables

    parameter_ids = [key.lower() for key in parameters.keys()]
    variable_ids = [key.upper() for key in variables.keys()]

    invalid_targets = []
    for change in sed_changes:
        if change.target.lower() in parameter_ids:
            block = parameters
            target = change.target.lower()

            for existing_target in block.keys():
                if existing_target.lower() == target:
                    target = existing_target
                    break

        elif change.target.upper() in variable_ids:
            block = variables
            target = change.target.upper()

            for existing_target in block.keys():
                if existing_target.upper() == target:
                    target = existing_target
                    break

        else:
            invalid_targets.append(change.target)
            continue

        block[target] = change.new_value

    if invalid_targets:
        msg = (
            'Model changes with the following targets could not be executed:\n  - {}\n\n'
            'The following targets are supported:\n  - {}'
        ).format(
            '\n  - '.join(sorted(invalid_targets)),
            '\n  - '.join(sorted(
                list(parameter_ids) +
                list(variable_ids)
            ))
        )
        raise ValueError(msg)


def set_up_simulation(sed_sim, xpp_sim, config=None):
    """ Apply SED simulation settings to the configuration of a XPP simulation

    Args:
        sed_sim (:obj:`UniformTimeCourseSimulation`): SED simulation
        xpp_sim (:obj:`dict`): XPP simulation
        config (:obj:`Config`, optional): configuration

    Returns:
        :obj:`tuple`:

            * :obj:`dict`: XPP simulation
            * :obj:`str`: KiSAO id of the algorithm to execute
    """
    substitution_policy = get_algorithm_substitution_policy(config=config)
    exec_kisao_id = get_preferred_substitute_algorithm_by_ids(
        sed_sim.algorithm.kisao_id, KISAO_ALGORITHM_MAP.keys(),
        substitution_policy=substitution_policy)

    alg_props = KISAO_ALGORITHM_MAP[exec_kisao_id]
    xpp_sim['meth'] = alg_props['id']

    for temp_alg_props in KISAO_ALGORITHM_MAP.values():
        for param_props in temp_alg_props['parameters'].values():
            if param_props['enabled']:
                xpp_sim.pop(param_props['id'], None)

    if exec_kisao_id == sed_sim.algorithm.kisao_id:
        for change in sed_sim.algorithm.changes:
            param_props = alg_props['parameters'].get(change.kisao_id, None)
            if param_props and param_props['enabled']:
                xpp_sim[param_props['id']] = change.new_value
            else:
                msg = (
                    'Algorithm `{}` ({}) does not support parameter `{}`. '
                    'The algorithm supports the following parameters:\n  - {}'
                ).format(
                    exec_kisao_id, alg_props['id'], change.kisao_id,
                    sorted('\n  - '.join(
                        '{}: {}'.format(param_props['kisao_id'], param_props['id'])
                        for param_props in alg_props['parameters'].values()
                        if param_props['enabled']
                    )),
                )
                if (
                    ALGORITHM_SUBSTITUTION_POLICY_LEVELS[substitution_policy]
                    > ALGORITHM_SUBSTITUTION_POLICY_LEVELS[AlgorithmSubstitutionPolicy.NONE]
                ):
                    warn(msg, BioSimulatorsWarning)
                else:
                    raise NotImplementedError(msg)

    xpp_sim['t0'] = str(sed_sim.initial_time)
    if sed_sim.output_start_time != sed_sim.initial_time:
        xpp_sim['trans'] = str(sed_sim.output_start_time)
    xpp_sim['total'] = str(sed_sim.output_end_time - sed_sim.initial_time)
    if xpp_sim['meth'] in [
        # '2rb',
        # '5dp',
        # '83dp',
        'adams',
        'backeul',
        # 'cvode',
        # 'discrete',
        'euler',
        # 'gear',
        'modeuler',
        # 'qualrk',
        'rungekutta',
        # 'stiff',
        'volterra',
        'ymp',
    ]:
        if 'dt' not in xpp_sim:
            xpp_sim['dt'] = '0.05'
        xpp_sim['njmp'] = str(round(
            (decimal.Decimal(sed_sim.output_end_time) - decimal.Decimal(sed_sim.output_start_time)) /
            decimal.Decimal(xpp_sim['dt']) / decimal.Decimal(sed_sim.number_of_points)
        ))
    else:
        xpp_sim['dt'] = str(
            (decimal.Decimal(sed_sim.output_end_time) -
             decimal.Decimal(sed_sim.output_start_time)) / decimal.Decimal(sed_sim.number_of_points)
        )
        xpp_sim['njmp'] = str(1)

    transient = decimal.Decimal(sed_sim.output_start_time) - decimal.Decimal(sed_sim.initial_time)
    freq_transient_samples = decimal.Decimal(1)
    if transient != 0:
        dt = decimal.Decimal(xpp_sim['dt'])
        while True:
            num_transient_steps = transient / (dt / freq_transient_samples)
            transient_steps_error = abs(num_transient_steps - round(num_transient_steps))
            if transient_steps_error < 1e-8:
                break
            freq_transient_samples += 1

        xpp_sim['dt'] = str(dt / freq_transient_samples)

    freq_transient_samples = int(freq_transient_samples)
    return xpp_sim, exec_kisao_id, freq_transient_samples


def write_xpp_parameter_file(parameters, filename):
    """ Write a set of parameters to a XPP parameter (``.par``) file

    Args:
        parameters (:obj:`dict`): dictionary that maps the id of each parameter to its value
        filename (:obj:`str`): path to save the parameters
    """
    with open(filename, 'w') as file:
        file.write('{} Number params\n'.format(len(parameters)))
        for key, val in parameters.items():
            file.write('{} {}\n'.format(val, key))


def write_xpp_initial_conditions_file(initial_conditions, filename):
    """ Write a set of initial conditions to a XPP initial conditions (``.ic``) file

    Args:
        initial_conditions (:obj:`collections.OrderedDict`): dictionary that maps the id of each parameter to its value
        filename (:obj:`str`): path to save the initial conditions
    """
    with open(filename, 'w') as file:
        for val in initial_conditions.values():
            file.write('{}\n'.format(val))


def write_method_to_xpp_simulation_file(simulation_method, in_filename, out_filename):
    """ Overwrite the simulation method settings in an XPP simulation file

    Args:
        simulation_method (:obj:`dict`): dictionary of simulation method settings
        in_filename (:obj:`str`): base XPP simulation file
        out_filename (:obj:`str`): path to save modified XPP simulation file
    """
    lines = []
    with open(in_filename, 'rb') as file:
        for line in file:
            if line.startswith(b'@'):
                continue

            last_line = line
            i_comment = last_line.find(b'#')
            if i_comment >= 0:
                last_line = last_line[0:i_comment]
            last_line = last_line.strip()
            last_line = last_line.lower()
            if last_line in [b'd', b'done']:
                # check for "done" line; note just the singular character ``d`` defines the "done" line
                break

            lines.append(line)

    for key, val in simulation_method.items():
        line = '@ {}={}\n'.format(key, val)
        line = line.encode()
        lines.append(line)

    with open(out_filename, 'wb') as file:
        for line in lines:
            file.write(line)


def exec_xpp_simulation(sim_filename, simulation,
                        set_filename=None,
                        overwrite_parameters=True,
                        overwrite_initial_conditions=True,
                        overwrite_method=True):
    """ Execute an XPP simulation, optionally overwriting its default parameters and initial conditions

    Args:
        sim_filename (:obj:`str`): path to the XPP file
        simulation (:obj:`dict`): simulation parameters, initial conditions, and method to override defaults
        set_filename (:obj:`str`, optional): path to XPP set file
        overwrite_parameters (:obj:`bool`, optional): whether to overwrite the default parameters
        overwrite_initial_conditions (:obj:`bool`, optional): whether to overwrite the default initial conditions
        overwrite_method (:obj:`bool`, optional): whether to overwrite the default simulation method and its settings

    Returns:
        :obj:`pandas.DataFrame`: simulation results
    """
    if sim_filename and os.path.isdir(sim_filename):
        sim_filename, temp_set_filename, _, _ = get_xpp_input_configuration_from_directory(sim_filename)
        set_filename = set_filename or temp_set_filename

    # set up XPP command
    fid, out_filename = tempfile.mkstemp(suffix='.dat')
    os.close(fid)
    cmd = ["xppaut", sim_filename, '-silent', '-outfile', out_filename]
    if set_filename:
        cmd.append('-setfile')
        cmd.append(set_filename)

    # write parameters and initial conditions to files
    if overwrite_parameters:
        fid, parameters_filename = tempfile.mkstemp(suffix='.par')
        os.close(fid)
        write_xpp_parameter_file(simulation['parameters'], parameters_filename)
        cmd.append('-parfile')
        cmd.append(parameters_filename)
    else:
        parameters_filename = None

    if overwrite_initial_conditions:
        fid, initial_conditions_filename = tempfile.mkstemp(suffix='.ic')
        os.close(fid)
        write_xpp_initial_conditions_file(simulation.get('initial_conditions', None) or {}, initial_conditions_filename)
        cmd.append('-icfile')
        cmd.append(initial_conditions_filename)
    else:
        initial_conditions_filename = None

    if overwrite_method:
        fid, temp_sim_filename = tempfile.mkstemp(suffix='.ode')
        os.close(fid)
        options = {
            **simulation['simulation_method'],
            **(simulation.get('other_numerics', None) or {}),
            **(simulation.get('other', None) or {}),
        }
        write_method_to_xpp_simulation_file(options, sim_filename, temp_sim_filename)
        cmd[1] = temp_sim_filename
    else:
        temp_sim_filename = None

    temp_filenames = [
        out_filename,
        parameters_filename,
        initial_conditions_filename,
        temp_sim_filename,
    ]

    # execute simulation
    result = subprocess.run(cmd,
                            cwd=os.path.dirname(sim_filename),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            check=False)

    # raise exception if XPP failed
    stdout = result.stdout.decode("utf-8")
    if (
        result.returncode != 0
        or 'Integration not completed' in stdout
        or 'out of bounds' in stdout
        or 'Incompatible parameters' in stdout
        or 'initial conditions but only found' in stdout
        or re.search('File<.*?> not found in', stdout)
        or 'Problem with creating table !!' in stdout
    ):
        remove_files(temp_filenames)
        raise RuntimeError('XPP failed ({}): {}'.format(result.returncode, stdout))

    # read results
    results = pandas.read_csv(
        out_filename,
        sep=' ',
        header=None,
    )

    # validate results
    column_names = simulation['outfile_column_names']
    if len(results.columns) - 1 != len(column_names):
        remove_files(temp_filenames)
        raise ValueError('Simulation results has {}, not {} variables'.format(len(results.columns) - 1, len(column_names)))

    # drop last empty column
    results = results.iloc[:, :-1]

    # drop duplicate columns and column names
    unique_column_names = []
    duplicate_column_indices = []
    for i_column, column_name in enumerate(column_names):
        if column_name in unique_column_names:
            duplicate_column_indices.append(i_column)
        else:
            unique_column_names.append(column_name)

    if duplicate_column_indices:
        results.drop(axis=1, columns=results.columns[duplicate_column_indices], inplace=True)

    # set column names
    results.columns = unique_column_names

    # cleanup temporary files
    remove_files(temp_filenames)

    # return results
    return results


def remove_files(filenames):
    """ Delete a list of files.

    Used to delete temporary simulation files generated by :obj:`exec_xpp_simulation`

    Args:
        filenames (:obj:`list` of :obj:`str`): names of files to remove
    """
    for filename in filenames:
        if filename:
            os.remove(filename)


def get_results_of_sed_variables(sed_simulation, xpp_results, sed_variables):
    """ Get the results of a list of SED variables

    Args:
        sed_simulation (:obj:`UniformTimeCourseSimulation`): SED simulation
        xpp_results (:obj:`pandas.DataFrame`): raw results generated by XPP
        sed_variables (:obj:`list` of :obj:`Variable`): SED variables

    Returns:
        :obj:`VariableResults`: results
    """
    variable_results = VariableResults()
    for sed_variable in sed_variables:
        if sed_variable.symbol:
            col = sed_variable.symbol

        else:
            col = sed_variable.target.upper()

        variable_results[sed_variable.id] = xpp_results.loc[:, col][-(sed_simulation.number_of_points + 1):].to_numpy()

    return variable_results
