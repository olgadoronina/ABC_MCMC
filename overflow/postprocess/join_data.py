import logging
import numpy as np
import os
import shutil
from overflow.sumstat import TruthData
from pyabc.distance import calc_err_norm2

# !!! don't change
N_PARAMS = 5    # output from overflow is always 5 parameters (some of them may be constant)


def load_data(folders, len_sumstat, check_length=False):
    N_total, diff = 0, 0
    result = np.empty((0, N_PARAMS + len_sumstat + 1))   # + 5 parameters in the beginning and distance in the end
    for i, folder in enumerate(folders):
        print('job {}'.format(i))
        with open(os.path.join(folder, 'result.dat')) as f:
            lines = f.readlines()
            for line in lines:
                d = np.fromstring(line[1:-1], dtype=float, sep=',')
                result = np.vstack((result, d))
        if check_length:
            N_total += len(np.loadtxt(os.path.join(folder, 'c_array_{}'.format(i))))
            if N_total != len(result):
                print('Job {} did not finish ({} out of {}), diff = {}'.format(i, len(result), N_total,
                                                                               N_total - len(result)))
    return result

def join_profiles(folders, cp, u, uv, u_surf):
    for i, folder in enumerate(folders):
        print('job {}'.format(i))
        cp = np.vstack((cp, np.fromfile(os.path.join(folder, 'cp_all.bin')).reshape(-1, 721)))
        u  = np.vstack((u, np.fromfile(os.path.join(folder, 'u_slice.bin')).reshape(-1, 800)))
        uv = np.vstack((uv, np.fromfile(os.path.join(folder, 'uv_slice.bin')).reshape(-1, 800)))
        u_surf = np.vstack((u_surf, np.fromfile(os.path.join(folder, 'u_surface.bin')).reshape(-1, 721)))
    return cp, u, uv, u_surf


def define_limits_for_uniform(c_array):
    N_params = c_array.shape[1]
    C_limits = np.empty((N_params, 2))
    for i in range(N_params):
        unique = np.unique(c_array[:, i])
        print(unique)
        dif = np.max(np.diff(unique))
        C_limits[i] = [unique[j] - (j+0.5)*dif for j in [0, -1]]
    print(C_limits)
    return C_limits


# def join_limits(limits, N_params):
#     all_lower_limits = np.ones((N_params, 1)) * (1000)
#     all_upper_limits = np.ones((N_params, 1)) * (-1000)
#     for limit in limits:
#         for i in range(N_params):
#             all_lower_limits[i] = min(limit[i, 0], all_lower_limits[i])
#             all_upper_limits[i] = max(limit[i, 1], all_upper_limits[i])
#     return np.hstack((all_lower_limits, all_upper_limits))


def main():

    ######################################
    # Define parameters
    #####################################
    basefolder = '../../'
    ######### 4 params bb
    # path = {'output': os.path.join(basefolder, 'overflow_results/output_4/'),
    #         'valid_data': '../overflow/valid_data/'}
    # N_jobs = [120, 200]
    # raw_folders = ['output_4_part1', 'output_4_part2']
    # N_params = 4  # number of non-constant parameters
    # take_slice = False   # takes 4D slice at sigma = 0.55
    # b_bstar = True
    ######## 4 params
    basefolder = '../../'
    path = {'output': os.path.join(basefolder, 'overflow_results/output_4_bb/', ),
            'valid_data': os.path.join(basefolder, 'overflow/valid_data/', ),
            'nominal_data': os.path.join(basefolder, 'overflow_results/nominal_data', )}
    N_jobs = [120, 200]

    raw_folders = ['output_4_bb/output_4_part1', 'output_4_bb/output_4_part2']
    N_params = 4  # number of non-constant parameters
    take_slice = False  # takes 4D slice at sigma = 0.55
    b_bstar = True
    ######## 5 params inflow
    basefolder = '../../'
    path = {'output': os.path.join(basefolder, 'overflow_results/output_inflow/', ),
            'valid_data': os.path.join(basefolder, 'overflow/valid_data/', ),
            'nominal_data': os.path.join(basefolder, 'overflow_results/nominal_data', )}
    N_jobs = [45, 60]

    raw_folders = ['output_inflow/output_inflow_part1', 'output_inflow/output_inflow_part2']
    N_params = 5  # number of non-constant parameters
    take_slice = False  # takes 4D slice at sigma = 0.55
    b_bstar = False
    ##################################
    # ######### 5 params bb
    # path = {'output': os.path.join(basefolder, 'overflow_results/output_5_bb/'),
    #         'valid_data': os.path.join(basefolder,'overflow/valid_data/'),
    #         'nominal_data': os.path.join(basefolder, 'overflow_results/nominal_data', )}
    # N_jobs = [45, 60]
    #
    # raw_folders = ['output_5_bb/output5_part1', 'output_5_bb/output5_part2']
    # N_params = 5  # number of non-constant parameters
    # take_slice = False  # takes 4D slice at sigma = 0.55
    # b_bstar = True
    ##################################
    if not os.path.isdir(path['output']):
        os.makedirs(path['output'])
    logging.basicConfig(
        format="%(levelname)s: %(name)s:  %(message)s",
        handlers=[logging.FileHandler(os.path.join(path['output'], 'ABC_postprocess.log')), logging.StreamHandler()],
        level=logging.DEBUG)
    data_folders = [os.path.join(basefolder, 'overflow_results', folder) for folder in raw_folders]
    print('data folders to join:', data_folders)
    # We need truth statistics only to know length when loading data
    Truth = TruthData(path['valid_data'], ['cp', 'u', 'uv', 'x_separation'])
    sumstat_length = len(Truth.sumstat_true)

    logging.info('Loading data')
    c_array = np.empty((0, N_params))
    sumstat_all = np.empty((0, sumstat_length))
    dist = []


    # for i, data_folder in enumerate(data_folders):
    #     folders = [os.path.join(data_folder, 'calibration_job{}'.format(n), ) for n in range(N_jobs[i])]
    #     result = load_data(folders, sumstat_length, check_length=False)  # to check length need c_array_* files
    #
    #
    #     if b_bstar:
    #         result[:, 2] /= result[:, 0]    # beta1/beta*
    #         result[:, 3] /= result[:, 0]    # beta2/beta*
    #
    #     if N_params == 4:
    #         result = np.delete(result, 1, axis=1)
    #
    #     c_array = np.vstack((c_array, result[:, :N_params]))
    #     sumstat_all = np.vstack((sumstat_all, result[:, N_params:-1]))
    #     dist.append(np.min(result[:, -1]))
    # print('min stores dist:', np.min(dist))
    #
    # N_total = len(c_array)
    # print(f'There are {N_total} samples in {N_params}D space')
    # C_limits = define_limits_for_uniform(c_array)
    # np.savez(os.path.join(path['output'], 'joined_data.npz'),
    #          c_array=c_array, sumstat_all=sumstat_all, C_limits=C_limits, N_total=N_total)

    cp_nominal = np.fromfile(os.path.join(path['nominal_data'], 'cp_all.bin'), dtype=float)
    u_nominal = np.fromfile(os.path.join(path['nominal_data'], 'u_slice.bin'), dtype=float)
    uv_nominal = np.fromfile(os.path.join(path['nominal_data'], 'uv_slice.bin'), dtype=float)
    u_surf_nominal = np.fromfile(os.path.join(path['nominal_data'], 'u_surface.bin'), dtype=float)

    cp_profile = np.empty((0, len(cp_nominal)))
    u_profile = np.empty((0, len(u_nominal)))
    uv_profile = np.empty((0, len(uv_nominal)))
    u_surf_profile = np.empty((0, len(u_surf_nominal)))
    for i, data_folder in enumerate(data_folders):
        folders = [os.path.join(data_folder, 'calibration_job{}'.format(n), ) for n in range(N_jobs[i])]
        cp_profile, u_profile, uv_profile, u_surf_profile = join_profiles(folders, cp_profile,
                                                                      u_profile, uv_profile, u_surf_profile)

    N_total = len(cp_profile)
    print(f'There are {N_total} samples in {N_PARAMS}D space')
    np.savez(os.path.join(path['output'], 'joined_profiles.npz'),
             cp=cp_profile, u=u_profile, uv=uv_profile, u_surface=u_surf_profile)
    ####################################################################################################
    # # ### taking slice
    if N_params == 5 and take_slice:
        c_array = np.load(os.path.join(path['output'], 'joined_data.npz'))['c_array']
        sumstat_all = np.load(os.path.join(path['output'], 'joined_data.npz'))['sumstat_all']
        C_limits = np.load(os.path.join(path['output'], 'joined_data.npz'))['C_limits']
        ind = np.where(c_array[:, 1] == 0.55)[0]
        c_array = c_array[ind]
        sumstat_all = sumstat_all[ind]
        c_array = np.delete(c_array, 1, axis=1)
        C_limits = np.delete(C_limits, 1, axis=0)
        print(f'There are {len(c_array)} samples in 4d slice')
        np.savez(os.path.join(path['output'], '4d_slice.npz'),
                 c_array=c_array, sumstat_all=sumstat_all, C_limits=C_limits, N_total=len(c_array))


if __name__ == '__main__':
    main()