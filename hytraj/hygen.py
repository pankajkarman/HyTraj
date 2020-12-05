import numpy as np
import pandas as pd
import os, glob, subprocess
from tqdm import tqdm


class HyGen(object):
    def __init__(
        self,
        year,
        locations,
        height,
        run_time,
        working,
        metdir,
        outdir,
        met_type="ncep",
        exe="./hyts_std",
    ):
        self.year = year
        self.run_time = run_time
        self.height = height
        self.stations = list(locations.keys())
        self.locations = locations
        self.workpath = working
        self.metdir = metdir
        self.met_type = met_type
        self.outdir = outdir
        self.exe = exe
        self.loc = self.get_coordinates(self.stations, self.height)

    def run(self, dates, vertical=0, model_top=10000.0):
        # start = '02-01-'+str(self.year)+' 05:00:00'
        # end   = '02-20-'+str(self.year)+' 05:00:00'
        # self.dates =  pd.date_range(start, freq='24H', end=end)
        self.dates = dates
        os.chdir(self.workpath)
        for date in tqdm(self.dates):
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
            else:
                metfiles = self.get_gdas_metfiles(date)
            metfiles = [self.metdir + filename for filename in metfiles]
            self.create_control_file(
                start_time, metfiles, outfile, vertical=vertical, model_top=model_top
            )
            subprocess.call(self.exe)
        return self

    def create_control_file(
        self, start_time, metfiles, outfile, vertical=0, model_top=10000.0
    ):
        with open(self.workpath + "CONTROL", "w") as raus:
            raus.write(start_time + "\n")  # 1
            raus.write("{}\n".format(len(self.loc)))  # 2
            raus.write(
                "\n".join(["{:0.2f} {:0.2f} {:0.1f}".format(*i) for i in self.loc])
                + "\n"
            )  # 3
            raus.write("{:d}\n".format(self.run_time))  # 4
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

    def get_gdas_metfiles(self, date):
        gdas_file = lambda date: "gdas1.%s%s.w%s" % (
            date.month_name().lower()[:3],
            str(date.year)[-2:],
            np.round(date.day / 7) + 1,
        )
        step = self.run_time
        steps = np.arange(0, step // 24, np.sign(step))
        fnames = set([gdas_file(date + pd.Timedelta(s, unit="d")) for s in steps])
        return list(fnames)

    def get_coordinates(self, stations, height):
        locations = []
        for station in stations:
            lat, lon = self.locations[station]
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
