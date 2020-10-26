import os
from scipy.integrate import odeint
import matplotlib as mpl
mpl.use('pdf')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import rans_ode.ode as rans
import pyabc.glob_var as g
import rans_ode.sumstat as sumstat
import rans_ode.workfunc_rans as workfunc

# plt.style.use('dark_background')

fig_width_pt = 1.5*246.0  # Get this from LaTeX using "The column width is: \the\columnwidth \\"
inches_per_pt = 1.0/72.27               # Convert pt to inches
golden_mean = (np.sqrt(5)-1.0)/2.0         # Aesthetic ratio
fig_width = fig_width_pt*inches_per_pt  # width in inches
fig_height = fig_width*golden_mean       # height in inches
fig_size = [fig_width, fig_height]

# mpl.rcParams['figure.figsize'] = 6.5, 2.2
# plt.rcParams['figure.autolayout'] = True

mpl.rcParams['font.size'] = 12
mpl.rcParams['axes.titlesize'] = 1.2 * plt.rcParams['font.size']
mpl.rcParams['axes.labelsize'] = plt.rcParams['font.size']
mpl.rcParams['legend.fontsize'] = plt.rcParams['font.size']-1
mpl.rcParams['xtick.labelsize'] = 0.8*plt.rcParams['font.size']
mpl.rcParams['ytick.labelsize'] = 0.8*plt.rcParams['font.size']

mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rc('text', usetex=True)

mpl.rcParams['xtick.major.size'] = 3
mpl.rcParams['xtick.minor.size'] = 3
mpl.rcParams['xtick.major.width'] = 1
mpl.rcParams['xtick.minor.width'] = 0.5
mpl.rcParams['ytick.major.size'] = 3
mpl.rcParams['ytick.minor.size'] = 3
mpl.rcParams['ytick.major.width'] = 1
mpl.rcParams['ytick.minor.width'] = 1
mpl.rcParams['legend.frameon'] = False
# plt.rcParams['legend.loc'] = 'center left'
plt.rcParams['axes.linewidth'] = 1


folder_valid = '/Users/olgadorr/Research/ABC_MCMC/rans_ode/valid_data/'


def plot_impulsive(c_array, plot_folder):
    Truth = sumstat.TruthData(valid_folder=folder_valid, case='impulsive_k')
    Strain = workfunc.StrainTensor(valid_folder=folder_valid)
    u0 = [1, 1, 0, 0, 0, 0, 0, 0]
    # axisymmetric expansion
    if len(c_array.shape) == 1:
        c_array = np.array(c_array).reshape((1, -1))
    fig = plt.figure(figsize=(0.8 * fig_width, 1.3 * fig_height))
    ax = plt.gca()
    fig2 = plt.figure(figsize=(0.8 * fig_width, 1.3 * fig_height))
    ax2 = plt.gca()
    for c in c_array:
        tspan1 = np.linspace(0, 1.5 / np.abs(Strain.axi_exp[0]), 200)
        Ynke1 = odeint(rans.rans_impulsive, u0, tspan1, args=(c, Strain.axi_exp), atol=1e-8, mxstep=200)
        # axisymmetric contraction
        tspan2 = np.linspace(0, 1.5 / np.abs(Strain.axi_con[0]), 200)
        Ynke2 = odeint(rans.rans_impulsive, u0, tspan2, args=(c, Strain.axi_con), atol=1e-8, mxstep=200)
        # pure shear
        tspan3 = np.linspace(0, 5 / (2 * Strain.pure_shear[3]), 200)
        Ynke3 = odeint(rans.rans_impulsive, u0, tspan3, args=(c, Strain.pure_shear), atol=1e-8, mxstep=200)
        # plane strain
        tspan4 = np.linspace(0, 1.5 / Strain.plane_strain[0], 200)
        Ynke4 = odeint(rans.rans_impulsive, u0, tspan4, args=(c, Strain.plane_strain), atol=1e-8, mxstep=200)

        ax.plot(np.abs(Strain.axi_exp[0]) * tspan1, Ynke1[:, 0], label='axisymmetric expansion')
        ax.scatter(Truth.axi_exp_k[:, 0], Truth.axi_exp_k[:, 1], marker='o')

        ax.plot(np.abs(Strain.axi_con[0]) * tspan2, Ynke2[:, 0], label='axisymmetric contraction')
        ax.scatter(Truth.axi_con_k[:, 0], Truth.axi_con_k[:, 1], marker='o')

        ax.plot(2 * Strain.pure_shear[3] * tspan3, Ynke3[:, 0], label='pure shear')
        ax.scatter(Truth.shear_k[:, 0], Truth.shear_k[:, 1], marker='o')

        ax.plot(np.abs(Strain.plane_strain[0]) * tspan4, Ynke4[:, 0], label='plain strain')
        ax.scatter(Truth.plane_k[:, 0], Truth.plane_k[:, 1], marker='o')

        # gradient
        x_diff = np.abs(Strain.axi_exp[0]) * tspan1
        ax2.plot(np.abs(Strain.axi_exp[0]) * tspan1, np.gradient(Ynke1[:, 0], x_diff), label='axisymmetric expansion')
        ax2.scatter(Truth.axi_exp_k[:, 0], np.gradient(Truth.axi_exp_k[:, 1], Truth.axi_exp_k[:, 0]), marker='o')

        x_diff = np.abs(Strain.axi_con[0]) * tspan2
        ax2.plot(np.abs(Strain.axi_con[0]) * tspan2, np.gradient(Ynke2[:, 0], x_diff), label='axisymmetric contraction')
        ax2.scatter(Truth.axi_con_k[:, 0], np.gradient(Truth.axi_con_k[:, 1], Truth.axi_con_k[:, 0]), marker='o')

        x_diff = 2 * Strain.pure_shear[3] * tspan3
        ax2.plot(2 * Strain.pure_shear[3] * tspan3, np.gradient(Ynke3[:, 0], x_diff), label='pure shear')
        ax2.scatter(Truth.shear_k[:, 0], np.gradient(Truth.shear_k[:, 1], Truth.shear_k[:, 0]), marker='o')

        x_diff = np.abs(Strain.plane_strain[0]) * tspan4
        ax2.plot(np.abs(Strain.plane_strain[0]) * tspan4, np.gradient(Ynke4[:, 0], x_diff), label='plain strain')
        ax2.scatter(Truth.plane_k[:, 0], np.gradient(Truth.plane_k[:, 1], Truth.plane_k[:, 0]), marker='o')


    ax.set_xlabel(r'$S\cdot t$')
    ax.set_ylabel(r'$k/k_0$')
    # ax.axis(xmin=0, xmax=5, ymin=0, ymax=2.5)
    plt.legend()
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.14, top=0.95)
    fig.savefig(os.path.join(plot_folder, 'compare_impulsive_k'))

    Truth = sumstat.TruthData(valid_folder=folder_valid, case='impulsive_a')
    ax2.set_xlabel(r'$S\cdot t$')
    ax2.set_ylabel(r'$k/k_0$')
    # ax.axis(xmin=0, xmax=5, ymin=0, ymax=2.5)
    plt.legend()
    fig2.subplots_adjust(left=0.13, right=0.98, bottom=0.14, top=0.95)
    fig2.savefig(os.path.join(plot_folder, 'compare_impulsive_k_gradient'))

    for c in c_array:
        fig = plt.figure(figsize=(0.8 * fig_width, 1.3 * fig_height))
        ax = plt.gca()

        ax.plot(np.abs(Strain.axi_exp[0]) * tspan1, Ynke1[:, 2], label=r'axisymmetric expansion $a_{11}$')
        ax.scatter(Truth.axi_exp_a[:, 0], Truth.axi_exp_a[:, 1], marker='o')

        ax.plot(np.abs(Strain.axi_con[0]) * tspan2, Ynke2[:, 2], label=r'axisymmetric contraction $a_{11}$')
        ax.scatter(Truth.axi_con_a[:, 0], Truth.axi_con_a[:, 1], marker='o')

        ax.plot(np.abs(Strain.plane_strain[0]) * tspan4, Ynke4[:, 2], label=r'plain strain $a_{11}$')
        ax.scatter(Truth.plane_a11[:, 0], Truth.plane_a11[:, 1], marker='o')

        ax.plot(np.abs(Strain.plane_strain[0]) * tspan4, Ynke4[:, 3], label=r'plain strain $a_{22}$')
        ax.scatter(Truth.plane_a22[:, 0], Truth.plane_a22[:, 1], marker='o')

    ax.set_xlabel(r'$S\cdot t$')
    ax.set_ylabel(r'$a$')
    # ax.axis(xmin=0, xmax=1.5, ymin=0, ymax=2.5)
    plt.legend()
    fig.subplots_adjust(left=0.15, right=0.98, bottom=0.14, top=0.95)
    fig.savefig(os.path.join(plot_folder, 'compare_impulsive_a'))
    plt.close('all')


def plot_periodic(c_array, plot_folder):
    Truth = sumstat.TruthData(valid_folder=folder_valid, case='periodic')
    s0 = 3.3
    beta = [0.125, 0.25, 0.5, 0.75, 1]
    u0 = [1, 1, 0, 0, 0, 0, 0, 0]
    # Periodic shear(five different frequencies)
    tspan = np.linspace(0, 50 / s0, 500)
    fig = plt.figure(figsize=(1 * fig_width, 1.3 * fig_height))
    ax = plt.gca()
    if len(c_array.shape) == 1:
        c_array = np.array(c_array).reshape((1, -1))
    for c in c_array:
        for i in range(5):
            Ynke = odeint(rans.rans_periodic, u0, tspan, args=(c, s0, beta[i], workfunc.StrainTensor.periodic_strain),
                          atol=1e-8, mxstep=200)
            ax.semilogy(s0*tspan, Ynke[:, 0], label=r'$\omega/S_{max} = $' + ' {}'.format(beta[i]))
            ax.scatter(Truth.periodic_k[i][:, 0], Truth.periodic_k[i][:, 1], marker='o')

    ax.set_xlabel(r'$S\cdot t$')
    ax.set_ylabel(r'$k/k_0$')
    ax.axis(xmin=0, ymin=0, xmax=51)
    plt.legend(loc=2, labelspacing=0.2, borderpad=0.0)
    fig.subplots_adjust(left=0.16, right=0.98, bottom=0.14, top=0.95)
    fig.savefig(os.path.join(plot_folder, 'compare_periodic'))

    plt.close('all')


def plot_validation_exp(c_array, plot_folder):
    Truth = sumstat.TruthData(valid_folder=folder_valid, case='validation_exp')
    s0 = 3.3
    beta = 1
    u0 = [1, 1, 0, 0, 0, 0, 0, 0]
    # Periodic shear(five different frequencies)
    tspan = np.linspace(0, 50 / s0, 500)
    fig = plt.figure(figsize=(1 * fig_width, 1.3 * fig_height))
    ax = plt.gca()
    if len(c_array.shape) == 1:
        c_array = np.array(c_array).reshape((1, -1))
    for c in c_array:
        Ynke = odeint(rans.rans_periodic, u0, tspan, args=(c, s0, beta, workfunc.StrainTensor.periodic_strain),
                      atol=1e-8, mxstep=200)
        ax.semilogy(s0*tspan, Ynke[:, 0], label=r'$\omega/S_{max} = $' + f' {beta}')
        ax.scatter(Truth.validation_exp[:, 0], Truth.validation_exp[:, 1], marker='o')

    ax.set_xlabel(r'$S\cdot t$')
    ax.set_ylabel(r'$k/k_0$')
    ax.axis(xmin=0, ymin=0, xmax=51)
    plt.legend(loc=2, labelspacing=0.2, borderpad=0.0)
    fig.subplots_adjust(left=0.16, right=0.98, bottom=0.14, top=0.95)
    fig.savefig(os.path.join(plot_folder, 'compare_periodic_exp'))

    plt.close('all')


def plot_validation_nominal(c_array, plot_folder):
    Truth = sumstat.TruthData(valid_folder=folder_valid, case='validation_nominal')
    s0 = 3.3
    beta = 0.5
    u0 = [1, 1, 0, 0, 0, 0, 0, 0]
    # Periodic shear(five different frequencies)
    tspan = np.linspace(0, 50 / s0, 500)
    fig = plt.figure(figsize=(1 * fig_width, 1.3 * fig_height))
    ax = plt.gca()
    if len(c_array.shape) == 1:
        c_array = np.array(c_array).reshape((1, -1))
    for c in c_array:
        Ynke = odeint(rans.rans_periodic, u0, tspan, args=(c, s0, beta, workfunc.StrainTensor.periodic_strain),
                      atol=1e-8, mxstep=200)
        ax.semilogy(s0*tspan, Ynke[:, 0], label=r'$\omega/S_{max} = $' + f' {beta}')
        ax.scatter(Truth.validation_nominal[:, 0], Truth.validation_nominal[:, 1], marker='o')

    ax.set_xlabel(r'$S\cdot t$')
    ax.set_ylabel(r'$k/k_0$')
    ax.axis(xmin=0, ymin=0, xmax=51)
    plt.legend(loc=2, labelspacing=0.2, borderpad=0.0)
    fig.subplots_adjust(left=0.16, right=0.98, bottom=0.14, top=0.95)
    fig.savefig(os.path.join(plot_folder, 'compare_periodic_nominal'))

    plt.close('all')
##########################################################
# Decay
##########################################################
def plot_decay(c_array, plot_folder):

    Truth = sumstat.TruthData(valid_folder=folder_valid, case='decay')
    u0 = [1, 1, 0.36, -0.08, -0.28, 0, 0, 0]
    tspan = np.linspace(0, 0.3, 200)

    fig = plt.figure(figsize=(0.8*fig_width, 1.3*fig_height))
    ax = plt.gca()
    ax.scatter(Truth.decay_a11[:, 0], Truth.decay_a11[:, 1], color='m', label='exp')
    ax.scatter(Truth.decay_a22[:, 0], Truth.decay_a22[:, 1], color='b')
    ax.scatter(Truth.decay_a22[:, 0], Truth.decay_a33[:, 1], color='r')
    if len(c_array.shape) == 1:
        c_array = np.array(c_array).reshape((1, -1))
    for c in c_array:
        Ynke = odeint(rans.rans_decay, u0, tspan, args=(c,), atol=1e-8, mxstep=200)
        plt.plot(tspan, Ynke[:, 2], 'm--', label='a11')
        plt.plot(tspan, Ynke[:, 3], 'b--', label='a22')
        plt.plot(tspan, Ynke[:, 4], 'r--', label='a33')

    ax.set_xlabel(r'$\tau$')
    ax.set_ylabel(r'$a$')
    # ax.axis(xmin=0, xmax=0.5, ymin=-0.4, ymax=0.4)
    plt.legend(loc=0)
    fig.subplots_adjust(left=0.15, right=0.98, bottom=0.14, top=0.95)
    fig.savefig(os.path.join(plot_folder, 'compare_decay'))
    plt.close('all')


# ##########################################################
# # Strain-relax
# ##########################################################
def plot_strained(c_array, plot_folder):

    Truth = sumstat.TruthData(valid_folder=folder_valid, case='strain-relax')
    Strain = workfunc.StrainTensor(folder_valid)
    u0 = [1, 1, 0.36, -0.08, -0.28, 0, 0, 0]
    # strain-relaxation
    tspan = np.linspace(0.0775, 0.953, 500)

    fig = plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    ax.scatter(Truth.strain_relax_a11[:, 0], Truth.strain_relax_a11[:, 1], label='exp')

    if len(c_array.shape) == 1:
        c_array = np.array(c_array).reshape((1, -1))
    for c in c_array:
        Ynke = odeint(rans.rans_strain_relax, u0, tspan, args=(c, Strain.strain_relax), atol=1e-8, mxstep=200)
        plt.plot(tspan, Ynke[:, 2], 'm--', label='a11')
    ax.set_xlabel(r'$\tau$')
    ax.set_ylabel(r'$a$')
    ax.axis(xmin=0, xmax=1, ymin=-1, ymax=1)
    plt.legend(loc=0)
    fig.subplots_adjust(left=0.15, right=0.95, bottom=0.14, top=0.95)
    fig.savefig(os.path.join(plot_folder, 'compare_strained'))
    plt.close('all')


def plot_experiment(plot_folder, indices=None):

    # impulsive
    Truth = sumstat.TruthData(valid_folder=folder_valid, case='impulsive_k')
    fig = plt.figure(figsize=(0.8 * fig_width, 1 * fig_height))
    ax = plt.gca()
    ax.scatter(Truth.axi_exp_k[:, 0], Truth.axi_exp_k[:, 1], marker='o', label='axisymmetric expansion')
    ax.scatter(Truth.axi_con_k[:, 0], Truth.axi_con_k[:, 1], marker='o', label='axisymmetric contraction')
    ax.scatter(Truth.shear_k[:, 0], Truth.shear_k[:, 1], marker='o', label='pure shear')
    ax.scatter(Truth.plane_k[:, 0], Truth.plane_k[:, 1], marker='o', label='plain strain')
    if indices is not None:
        truth = np.vstack((Truth.axi_exp_k, Truth.axi_con_k, Truth.shear_k, Truth.plane_k))
        ax.scatter(truth[indices, 0], truth[indices, 1], color='k',  marker='o')
    ax.set_xlabel(r'$S\cdot t$')
    ax.set_ylabel(r'$k/k_0$')
    # ax.axis(xmin=0, xmax=5, ymin=0, ymax=2.5)
    plt.legend(frameon=True)
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.14, top=0.95)
    fig.savefig(os.path.join(plot_folder, 'impulsive_k'))

    Truth = sumstat.TruthData(valid_folder=folder_valid, case='impulsive_a')
    fig = plt.figure(figsize=(0.8 * fig_width, 1.3 * fig_height))
    ax = plt.gca()
    ax.scatter(Truth.axi_exp_a[:, 0], Truth.axi_exp_a[:, 1], marker='o', label=r'axisymmetric expansion $a_{11}$')
    ax.scatter(Truth.axi_con_a[:, 0], Truth.axi_con_a[:, 1], marker='o', label=r'axisymmetric contraction $a_{11}$')
    ax.scatter(Truth.plane_a11[:, 0], Truth.plane_a11[:, 1], marker='o',  label=r'plain strain $a_{11}$')
    ax.scatter(Truth.plane_a22[:, 0], Truth.plane_a22[:, 1], marker='o', label=r'plain strain $a_{22}$')

    ax.set_xlabel(r'$S\cdot t$')
    ax.set_ylabel(r'$a$')
    # ax.axis(xmin=0, xmax=1.5, ymin=0, ymax=2.5)
    plt.legend()
    fig.subplots_adjust(left=0.15, right=0.98, bottom=0.14, top=0.95)
    fig.savefig(os.path.join(plot_folder, 'impulsive_a'))
    # Decay
    Truth = sumstat.TruthData(valid_folder=folder_valid, case='decay')
    fig = plt.figure(figsize=(0.8 * fig_width, 1.3 * fig_height))
    ax = plt.gca()

    ax.scatter(Truth.decay_a11[:, 0], 2 * Truth.decay_a11[:, 1], marker='o', label=r'$a_{11}$')
    ax.scatter(Truth.decay_a22[:, 0], 2 * Truth.decay_a22[:, 1], marker='o', label=r'$a_{22}$')
    ax.scatter(Truth.decay_a33[:, 0], 2 * Truth.decay_a33[:, 1], marker='o', label=r'$a_{33}$')

    ax.set_xlabel(r'$S\cdot t$')
    ax.set_ylabel(r'$a$')
    # ax.axis(xmin=0, xmax=1.5, ymin=0, ymax=2.5)
    plt.legend()
    fig.subplots_adjust(left=0.15, right=0.98, bottom=0.14, top=0.95)
    fig.savefig(os.path.join(plot_folder, 'decay_a'))
    plt.close('all')




