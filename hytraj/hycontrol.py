import numpy as np, pandas as pd
import os, glob, subprocess
from shutil import copyfile, copy2

class HyControl(object):
    def __init__(
        self,
        year,
        stations,
        height,
        run_time,
        working,
        metdir,
        outdir,
        met_type="ncep",
        hysplit="./hyts_std",
    ):
        self.year = year
        self.run_time = run_time
        self.height = height
        self.stations = stations
        self.workpath = working
        self.metdir = metdir
        self.met_type = met_type
        self.outdir = outdir
        self.hysplit = hysplit

    def run(
        self,
        vertical=0,
        model_top=10000.0,
        cdir="/home/geoschem/hysplit/trajectories/ncep/all/control/",
    ):
        self.loc = self.get_coordinates(self.stations, self.height)
        start = "01-01-" + str(self.year) + " 05:00:00"
        end = "12-31-" + str(self.year) + " 05:00:00"
        self.dates = pd.date_range(start, freq="24H", end=end)
        os.chdir(self.workpath)
        for date in self.dates:
            start_time = self.get_hydate(date)
            outfile = (
                self.outdir
                + self.met_type
                + "."
                + str(self.height)
                + "."
                + self.get_out_date(date)
            )
            if self.met_type == "ncep":
                metfiles = self.get_ncep_metfiles(date)
            metfiles = [self.metdir + filename for filename in metfiles]
            self.create_control_file(
                start_time,
                self.loc,
                self.run_time,
                metfiles,
                self.workpath,
                outfile,
                vertical=vertical,
                model_top=model_top,
            )
            copy2(self.workpath + "CONTROL", cdir + self.get_out_date(date))
        return self

    def create_control_file(
        self,
        start_time,
        locations,
        run_time,
        metfiles,
        workpath,
        outfile,
        vertical=0,
        model_top=10000.0,
    ):
        with open(workpath + "CONTROL", "w") as raus:
            raus.write(start_time + "\n")  # 1
            raus.write("{}\n".format(len(locations)))  # 2
            raus.write(
                "\n".join(["{:0.2f} {:0.2f} {:0.1f}".format(*i) for i in locations])
                + "\n"
            )  # 3
            raus.write("{:d}\n".format(run_time))  # 4
            raus.write("{:d}\n".format(vertical))  # 5
            raus.write("{:0.1f}\n".format(model_top))  # 6
            raus.write("{:d}\n".format(len(metfiles)))  # 7
            for fn in metfiles:
                folder, file = os.path.split(fn)
                raus.write(folder + "/" + "\n")  # 8
                raus.write(file + "\n")  # 9
            folder, file = os.path.split(outfile)
            raus.write(folder + "/" + "\n")
            raus.write(file + "\n")  # 11

    @staticmethod
    def get_ncep_metfiles(date):
        mons = [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ]
        curr = "RP." + mons[date.month - 1] + str(date.year) + ".1.gbl1"
        if not date.month == 1:
            prev = "RP." + mons[date.month - 2] + str(date.year) + ".1.gbl1"
        else:
            prev = "RP." + mons[-1] + str(date.year - 1) + ".1.gbl1"

        if not date.month == 12:
            next = "RP." + mons[date.month] + str(date.year) + ".1.gbl1"
        else:
            next = "RP." + mons[0] + str(date.year + 1) + ".1.gbl1"
        return [curr, prev, next]

    @staticmethod
    def get_coordinates(stations, height):
        locations = []
        loc = {
            "davs": (-69, 78),
            "spol": (-90, 335),
            "neum": (-71, 352),
            "myth": (-70, 11),
            "syow": (-69, 40),
            "marb": (-64, 303),
            "mcmu": (-78, 167),
            "mirn": (-66, 93),
        }
        for station in stations:
            lat, lon = loc[station]
            locations.append([lat, lon, height])
        return locations

    @staticmethod
    def get_hydate(date):
        year = str(date)[2:4]
        month = str(date)[5:7]
        day = str(date)[8:10]
        hour = str(date)[11:13]
        start = year + " " + month + " " + day + " " + hour
        return start

    @staticmethod
    def get_out_date(date):
        tt = str(date).split(":")[:-2][0].split("-")
        name = "".join(tt)
        ts = name.split(" ")
        name = "".join(ts)
        return name


heights = [500]
run_time = -360
years = np.arange(1980, 2019)

stations = ["davs", "marb", "mcmu", "spol", "syow", "neum"]
metdir = "/home/geoschem/hysplit/ncep/"
outbase = "/home/geoschem/hysplit/trajectories/ncep/all/"
working = "./"

for height in heights:
    outdir = outbase + str(height) + "/"
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    for year in years:
        hy = HyGen(
            year,
            stations,
            height,
            run_time,
            working,
            metdir,
            outdir,
            met_type="ncep",
            hysplit="/home/geoschem/hysplit/bin/hyts_std",
        )
        hy = hy.run(vertical=0, model_top=10000.0)
