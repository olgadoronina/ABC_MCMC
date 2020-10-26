import os
import sys
import logging
import yaml
import numpy as np
sys.path.append('/Users/olgadorr/Research/ABC_MCMC')
import pyabc.parallel as parallel
import pyabc.abc_alg as abc_alg
import pyabc.glob_var as g
# import postprocess.postproc_abc as postproc_abc
import sumstat
from workfunc_rans import StrainTensor, define_work_function


def main():

    # # Initialization
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = os.path.join('./', 'params.yml')
    input = yaml.load(open(input_path, 'r'))

    ### Paths
    g.path = input['path']
    print(g.path)
    if not os.path.isdir(g.path['output']):
        os.makedirs(g.path['output'])
    if input['abc_algorithm'] == 'abc_IMCMC':
        g.path['calibration'] = os.path.join(g.path['output'], 'calibration')
        if not os.path.isdir(g.path['calibration']):
            os.makedirs(g.path['calibration'])
    logging.basicConfig(
        format="%(levelname)s: %(name)s:  %(message)s",
        handlers=[logging.FileHandler("{0}/{1}.log".format(g.path['output'], 'ABC_log')), logging.StreamHandler()],
        level=logging.DEBUG)

    g.N_params = len(input['C_limits'])
    # ABC algorithm
    algorithm_input = input['algorithm'][input['abc_algorithm']]
    # RANS ode specific
    g.Truth = sumstat.TruthData(valid_folder=g.path['valid_data'], case=input['case'])
    g.Strain = StrainTensor(valid_folder=g.path['valid_data'])
    g.case = input['case']
    g.work_function = define_work_function()
    C_limits = np.array(input['C_limits'])
    C_nominal = input['C_nominal']
    ####################################################################################
    # Run
    ####################################################################################
    g.par_process = parallel.Parallel(1, input['parallel_threads'])
    logging.info('C_limits: {}'.format(C_limits))
    np.savetxt(os.path.join(g.path['output'], 'C_limits_init'), C_limits)
    if input['abc_algorithm'] == 'abc':    # classical abc algorithm (accepts all samples for further postprocessing)
        logging.info("Classic ABC algorithm")
        C_array = abc_alg.sampling(algorithm_input['sampling'], C_limits, algorithm_input['N'])
        # if estimating of fewer parameters
        if len(C_limits) < len(C_nominal):
            logging.info('Using nominal values: {}'.format(C_nominal))
            add = [C_nominal[len(C_limits):], ]*(algorithm_input['N']**len(C_limits))
            C_array = np.hstack((C_array, add))
        abc_alg.abc_classic(C_array)
        ################################################################################################################
    elif input['abc_algorithm'] == 'abc_IMCMC':    # MCMC with calibration step (Wegmann 2009)
        logging.info("ABC-MCMC algorithm")
        logging.info('Calibration')
        abc_alg.one_calibration(algorithm_input, C_limits)
        logging.info('Chains')
        g.N_per_chain = algorithm_input['N_per_chain']
        g.t0 = algorithm_input['t0']
        abc_alg.mcmc_chains(n_chains=g.par_process.proc)
        ################################################################################################################
    elif input['abc_algorithm'] == 'abc_MCMC_adaptive':
        logging.info("ABC-MCMC algorithm with adaptation")
        logging.info('Chains')
        g.C_limits = C_limits
        g.N_per_chain = algorithm_input['N_per_chain']
        g.target_acceptance = algorithm_input['target_acceptance']
        g.t0 = algorithm_input['t0']
        C_start = abc_alg.sampling('random', C_limits, input['parallel_threads'])
        np.savetxt(os.path.join(g.path['calibration'], 'C_start'), C_start)
        abc_alg.mcmc_chains(n_chains=g.par_process.proc)
    else:
        logging.warning('{} algorithm does not exist'.format(input['abc_algorithm']))
    ####################################################################################################################
    # if input['abc_algorithm'] == 'abc':
    #     postproc_abc.main(sys.argv)


if __name__ == '__main__':
    main()
