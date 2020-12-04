#!/usr/bin/env python
# coding=utf-8

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FormatStrFormatter
from matplotlib.dates import DateFormatter

plt.style.use("seaborn-ticks")
cmap = cm.tab10
cm_list = [cmap(i) for i in range(cmap.N)]


cbw_file = "/project/mrp/BLM/SERIES4/SurfaceData_Cabauw_May2008.txt"
start = "2008-05-08 00:00:00"
end = "2008-05-13 00:00:00"

def read_file(fic):
    """
    """

    ## Read data into a dataframe
    cbw_df = pd.read_csv(fic, sep="\s+")


    ## Create datetime series and make it the index for easy handling
    cbw_dtm = pd.to_datetime(cbw_df[["year", "month", "day", "hour"]],
                             format="%Y%m%d%f")
    cbw_df.index = cbw_dtm

    ## drop unnecessary columns and NaN values
    cbw_df = cbw_df.drop(["year", "month", "day", "hour"], axis=1)
    # cbw_df = cbw_df.dropna()

    return cbw_df


def ob_length(u_star, heat_flux, temp):

    kappa = 0.41
    g = 9.81

    tmp1 = - 1 / kappa
    tmp2 = u_star ** 3 / heat_flux
    tmp3 = (temp + 273.15) / g

    L = tmp1 * tmp2 * tmp3

    return L

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


def timeseries_plot(ax, data, label=None):

    ax.plot(data, marker=".", lw=0.5, markersize=3)
    ax.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)
    ax.set_ylabel(label)
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))

    return ax


def main(cbw_file, start, end):

    cbw_df = read_file(cbw_file)

    surf_fig = plt.figure(figsize=(15,6))
    grid = plt.GridSpec(4,1, wspace=1.0)

    ws_ax = surf_fig.add_subplot(grid[3,:])
    tt_ax = surf_fig.add_subplot(grid[2,:])
    rr_ax = surf_fig.add_subplot(grid[1,:])
    pp_ax = surf_fig.add_subplot(grid[0,:])

    timeseries_plot(pp_ax, cbw_df["Press"], label="Press [hPa]")
    timeseries_plot(tt_ax, cbw_df["Rain"], label="Rain [mm]")
    timeseries_plot(rr_ax, cbw_df["Ta002"], label="Temp [$^o$C]")
    timeseries_plot(ws_ax, cbw_df["U010"], label="WS [ms$^{-1}$]")

    ws_ax.set_xlabel("Datetime")

    plt.setp(pp_ax.get_xticklabels(), visible=False)
    plt.setp(rr_ax.get_xticklabels(), visible=False)
    plt.setp(tt_ax.get_xticklabels(), visible=False)

    week_df = cbw_df[start : end]

    ## Compute Obukov Length
    u_star = week_df["ust005"]
    heat_flux = week_df["wT005"]
    temp = week_df["Ta002"]

    L = ob_length(u_star, heat_flux, temp)
    hour = pd.to_timedelta(L.index.hour, unit="H")
    hour.name = "Hour"
    diurnal_L = L.groupby(hour)

    key_list = []
    dat_list = []
    for key, dat in diurnal_L:
        key_list.append(key)
        dat_list.append(dat)

    mean_diurnal_L = diurnal_L.mean()
    hour_tick = pd.to_datetime(mean_diurnal_L.index)
    myfmt = DateFormatter("%H:%M:%S")

    len_fig, ax = plt.subplots()
    ax.plot(hour_tick, mean_diurnal_L, marker=".")
    ax.xaxis.set_major_formatter(myfmt)
    ax.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)


    fig, host = plt.subplots(figsize=(15,3))
    fig.subplots_adjust(right=0.6)

    par2 = host.twinx()
    par3 = host.twinx()
    par4 = host.twinx()

    host.spines["left"].set_color(cm_list[0])
    par2.spines["right"].set_color(cm_list[1])

    par3.spines["right"].set_position(("axes", 1.1))
    make_patch_spines_invisible(par3)
    par3.spines["right"].set_visible(True)
    par3.spines["right"].set_color(cm_list[2])

    par4.spines["right"].set_position(("axes", 1.2))
    make_patch_spines_invisible(par4)
    par4.spines["right"].set_visible(True)
    par4.spines["right"].set_color(cm_list[3])


    p1, = host.plot(week_df["NRad"], color=cm_list[0], lw=0.75)
    p2, = par2.plot(week_df["H"], color=cm_list[1], lw=0.75)
    p3, = par3.plot(week_df["LE"], color=cm_list[2], lw=0.75)
    p4, = par4.plot(week_df["G"], color=cm_list[3], lw=0.75)

    host.set_xlabel("Datetime")
    host.set_ylabel("Net radiation [Wm$^{-2}$]")
    par2.set_ylabel("Sens. heat flux [Wm$^{-2}$]")
    par3.set_ylabel("Lat. heat flux [Wm$^{-2}$]")
    par4.set_ylabel("Ground heat flux [Wm$^{-2}$]")
    
    tkw = dict(size=4, width=1.5)
    host.tick_params(axis="y", colors=p1.get_color(), **tkw)
    par2.tick_params(axis="y", colors=p2.get_color(), **tkw)
    par3.tick_params(axis="y", colors=p3.get_color(), **tkw)
    par4.tick_params(axis="y", colors=p4.get_color(), **tkw)
    host.tick_params(axis="x", **tkw)

    host.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)

    return
