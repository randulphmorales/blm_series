#!/usr/bin/env python
# coding=utf-8

import os
import glob
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


fic_path = "/project/mrp/BLM/SERIES4/"
file_list = glob.glob(os.path.join(fic_path, "*UTC.txt"))


def create_dataframe(fic):
    """
    """


    def pot_temp(airtemp, press):

        press0 = 1000.0
        return airtemp * ((press0 / press) ** 0.286)


    def vapor_press(dew_temp):

        return 6.112 * np.exp((17.67 * dew_temp) / (dew_temp + 243.5))


    def spec_humid(vap_press, press):

        return (0.622 * vap_press) / (press - (0.378 * vap_press))

    df = pd.read_csv(fic, sep="\s+", index_col=0)
    df = df.dropna()

    df["theta"] = pot_temp(df["T"] + 273.15, df["press"])
    df["vap_press"] = vapor_press(df["Td"])
    df["spec_hum"] = spec_humid(df["vap_press"], df["press"])

    return df


mnight_09_df = create_dataframe(file_list[0])
noon_09_df = create_dataframe(file_list[1])
mnight_28_df = create_dataframe(file_list[2])
noon_28_df = create_dataframe(file_list[3])

fig, ax = plt.subplots(figsize=(6,6))
ax.plot(mnight_28_df["theta"], mnight_09_df.index, label="May 28_00_UTC", marker=".")
ax.plot(noon_28_df["theta"], noon_09_df.index, label="May 28_12_UTC", marker=".")
ax.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)
ax.set_xlabel("Potential temperature [K]")
ax.set_ylabel("Height [m]")
ax.legend()


fig, ax = plt.subplots(figsize=(6,6))
ax.plot(mnight_28_df["spec_hum"], mnight_09_df.index, label="May 28_00_UTC", marker=".")
ax.plot(noon_28_df["spec_hum"], noon_09_df.index, label="May 28_12_UTC", marker=".")
ax.grid(linewidth=0.5, color="grey", linestyle="dotted", alpha=0.5)
ax.set_xlabel("Specific humidity [kg/kg]")
ax.set_ylabel("Height [m]")
ax.legend()
