#!/usr/bin/env python
# coding=utf-8

import os
import glob
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import norm


spec_file = "/project/mrp/BLM/SERIES4/Cabauw_SpecDens_09May2008_05000530.txt"


def readfile(cbw_file):

    df = pd.read_csv(cbw_file, sep="\s+")

    return df


def trapezoidal_rule(su, freq):

    N = len(su)
    su = np.asarray(su)
    freq = np.asarray(freq)

    area = 0.0
    for i in range(1,N):
        area += 0.5 * (su[i] + su[i-1]) * (freq[i] - freq[i-1])

    return area


def empirical(freq, z, u_bar):

    n = freq * (z / u_bar)

    empu = (79 * n) / (1 + (263 * n ** (5/3)))
    empv = (13 * n) / (1 + (32 * n ** (5/3)))
    empw = (3.5 * n) / (1 + (8.6 * n ** (5/3)))

    return n, empu, empv, empw

def dat_spec(freq, ss, u_star):

    return (freq * ss) / u_star**2


def tke(freq, alpha, ss, u_bar):

    tmp1 = (2 * np.pi * freq) / u_bar
    tmp2 = (freq * ss) / alpha

    epsilon = tmp1 * (tmp2 ** (3/2))

    return epsilon

u_bar = 2.706808
u_star = 0.209603
z = 3.0
spec_df = readfile(spec_file)
n, empu, empv, empw = empirical(spec_df.freq, z, u_bar)
spcu = dat_spec(spec_df.freq, spec_df.Su, u_star)
spcv = dat_spec(spec_df.freq, spec_df.Sv, u_star)
spcw = dat_spec(spec_df.freq, spec_df.Sw, u_star)


ratio_svsu = spec_df.Sv/spec_df.Su
ratio_swsu = spec_df.Sw/spec_df.Su

fig, ax = plt.subplots()
ax.plot(n, spcv, marker=".", linewidth=0.0)
ax.plot(n, empv, label="Olesen")
ax.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"$n=f \cdot z/u$")
ax.set_ylabel(r"$f \cdot S_v(f)/ u^2_*$")
ax.set_title("V Spectrum")


low_hline = 4/3 - 3/10
high_hline = 4/3 + 3/10
fig, ax = plt.subplots()
ax.plot(n, ratio_svsu, marker=".", linewidth=0.0)
ax.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)
# ax.set_xticks([1.2], minor=True)
ax.axhline(y=low_hline, color="r", lw=0.5)
ax.axhline(y=high_hline, color="r", lw=0.5)
ax.axvline(x=1.2, color="r", lw=0.5)
ax.set_title("Ratio Sv/Su")
ax.set_xlabel("Frequency")

tke_df = spec_df[spec_df.freq >= 1.2]
epsu = tke(tke_df.freq, 0.55, tke_df.Su, u_bar)
epsv = tke(tke_df.freq, 0.73, tke_df.Sv, u_bar)
epsw = tke(tke_df.freq, 0.73, tke_df.Sw, u_bar)
epsm = (epsu + epsv + epsw)/3

fig, ax = plt.subplots()
ax.plot(tke_df.freq, epsu, marker=".", lw=0.5, label=r"$\varepsilon_u$")
ax.plot(tke_df.freq, epsv, marker=".", lw=0.5, label=r"$\varepsilon_v$")
ax.plot(tke_df.freq, epsw, marker=".", lw=0.5, label=r"$\varepsilon_w$")
ax.plot(tke_df.freq, epsm, color="k", label="mean")
ax.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)
ax.set_xlabel("Frequency [1/s]")
ax.set_ylabel("Dissipation Rate")
ax.legend()
