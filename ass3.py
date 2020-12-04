#!/usr/bin/env python
# coding=utf-8

import os
import glob
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import norm


cbw_file = "/project/mrp/BLM/SERIES4/Cabauw_TimeSeries_09May2008_05000530_rotated.txt"


def readfile(cbw_file):

    df = pd.read_csv(cbw_file, sep="\s+", parse_dates=[["yyyy", "mm", "dd",
                                                        "HH", "MIN", "SEC"]],
                     index_col=0)

    df.index = pd.to_datetime(df.index, format="%Y %m %d %H %M %S.%f")
    df.index = pd.DatetimeIndex(df.index, name="datetime")

    return df

def getmeanandturb(df, sampling_time="30min"):

    mean_df = df.resample(sampling_time).mean()
    std_df = df.resample(sampling_time).std()

    mean_index = mean_df.index.values.astype(float)
    df_index = df.index.values.astype(float)

    df["u_bar"] = np.interp(df_index, mean_index, mean_df["u"])
    df["v_bar"] = np.interp(df_index, mean_index, mean_df["v"])
    df["w_bar"] = np.interp(df_index, mean_index, mean_df["w"])
    df["T_bar"] = np.interp(df_index, mean_index, mean_df["T"])

    df["sig.u"] = df["u"] - df["u_bar"]
    df["sig.v"] = df["v"] - df["v_bar"]
    df["sig.w"] = df["w"] - df["w_bar"]
    df["sig.T"] = df["T"] - df["T_bar"]

    return df


def timeseries_plot(ax, data, label=None):

    ax.plot(data, marker=".", lw=0.5, markersize=3)
    ax.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)
    ax.set_ylabel(label)
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))

    return ax


def stress_tensor(flux_one, flux_two, density):

    return flux_one * flux_two * density


def u_star(mean_uw, mean_vw):

    return (mean_uw**2 + mean_vw**2)**0.25


def ob_length(u_star, heat_flux, temp):

    kappa = 0.41
    g = 9.81

    tmp1 = - 1 / kappa
    tmp2 = u_star / heat_flux
    tmp3 = temp / g

 j   ol = tmp1 * tmp2 * tmp3

    return ol

def main(cbw_file):

    meteo_df = readfile(cbw_file)
    meteo_df = getmeanandturb(meteo_df, "30min")

    meteo_df["sig.uu"] = stress_tensor(meteo_df["sig.u"], meteo_df["sig.u"], 1.2)
    meteo_df["sig.uv"] = stress_tensor(meteo_df["sig.u"], meteo_df["sig.v"], 1.2)
    meteo_df["sig.uw"] = stress_tensor(meteo_df["sig.u"], meteo_df["sig.w"], 1.2)

    meteo_df["sig.vv"] = stress_tensor(meteo_df["sig.v"], meteo_df["sig.v"], 1.2)
    meteo_df["sig.vw"] = stress_tensor(meteo_df["sig.v"], meteo_df["sig.w"], 1.2)

    meteo_df["sig.ww"] = stress_tensor(meteo_df["sig.w"], meteo_df["sig.w"], 1.2)

    meteo_df["sig.wT"] = meteo_df["sig.w"]*meteo_df["T"]

    mean_df = meteo_df.resample("30min").mean()
    friction_vel = u_star((mean_df["sig.uv"] / 1.2), (mean_df["sig.uw"] / 1.2))
    ol = ob_length(friction_vel, mean_df["sig.wT"], mean_df["T"])

    surf_fig = plt.figure(figsize=(15,6))
    grid = plt.GridSpec(4,1, wspace=1.0)

    uu_ax = surf_fig.add_subplot(grid[3,:])
    vv_ax = surf_fig.add_subplot(grid[2,:])
    ww_ax = surf_fig.add_subplot(grid[1,:])
    tt_ax = surf_fig.add_subplot(grid[0,:])

    timeseries_plot(uu_ax, meteo_df["u"], label="U [ms$^{-1}$]")
    timeseries_plot(vv_ax, meteo_df["v"], label="V [ms$^{-1}$]")
    timeseries_plot(ww_ax, meteo_df["w"], label="W [ms$^{-1}$]")
    timeseries_plot(tt_ax, meteo_df["T"], label="T [K]")

    uu_ax.set_xlabel("Datetime")

    plt.setp(vv_ax.get_xticklabels(), visible=False)
    plt.setp(ww_ax.get_xticklabels(), visible=False)
    plt.setp(tt_ax.get_xticklabels(), visible=False)

    fig, ax = plt.subplots()
    ax.hist(meteo_df["sig.u"], bins=50)
    ax.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)
    ax.set_xlabel("U flux [m/s]")
    ax.set_ylabel("Frequency")

    fig, ax = plt.subplots()
    ax.hist(meteo_df["sig.v"], bins=50)
    ax.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)
    ax.set_xlabel("V flux [m/s]")
    ax.set_ylabel("Frequency")

    return


# ## create a gaussian curve plot
# u_mean = float(df["sig.uu"].mean())
# u_std = float(df["sig.uu"].std())
# u_min = np.min(df["sig.uu"])
# u_max = np.max(df["sig.uu"])
# z_min = (u_min - u_mean) / u_std
# z_max = (u_max - u_mean) / u_std
# 
# u_x = np.arange(z_min, z_max, 0.001)
# u_y = norm.pdf(u_x,0,1)


