import numpy as np
import pandas as pd
import os, glob, subprocess
from tqdm import tqdm
import shutil
from shutil import copyfile, copy2
import multiprocessing as mp
from joblib import Parallel, delayed, parallel_backend


class HyGen(object):
    def __init__(
        self,
        locations,
        height,
        run_time,
        working,
        metdir,
        outdir,
        met_type="ncep",
        exe="./hyts_std",
    ):
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
            if self.met_type == "ncep_old":
                metfiles = self.get_old_ncep_metfiles(date)

            if self.met_type == "ncep_new":
                metfiles = self.get_new_ncep_metfiles(date)

            if self.met_type == "gdas_1":
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
    def get_new_ncep_metfiles(date):
        curr = "RP%s%02d.gbl" % (date.year, date.month)
        if not date.month == 12:
            next = "RP%s%02d.gbl" % (date.year, date.month + 1)
        else:
            next = "RP%s%02d.gbl" % (date.year + 1, date.month - 11)

        if not date.month == 1:
            prev = "RP%s%02d.gbl" % (date.year, date.month - 1)
        else:
            prev = "RP%s%02d.gbl" % (date.year - 1, date.month - 1 + 12)
        return [curr, prev, next]

    @staticmethod
    def get_old_ncep_metfiles(date):
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


class HyControl(HyGen):
    def __init__(
        self,
        locations,
        height,
        run_time,
        working,
        metdir,
        outdir,
        met_type="ncep",
        exe="./hyts_std",
    ):
        super().__init__(
            locations, height, run_time, working, metdir, outdir, met_type, exe
        )

    def run(
        self,
        dates,
        vertical=0,
        model_top=10000.0,
        cdir="/home/geoschem/hysplit/trajectories/ncep/all/control/",
    ):
        self.dates = dates
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
            if self.met_type == "ncep_old":
                metfiles = self.get_old_ncep_metfiles(date)

            if self.met_type == "ncep_new":
                metfiles = self.get_new_ncep_metfiles(date)

            if self.met_type == "gdas_1":
                metfiles = self.get_gdas_metfiles(date)
            metfiles = [self.metdir + filename for filename in metfiles]
            self.create_control_file(
                start_time, metfiles, outfile, vertical=vertical, model_top=model_top
            )
            copy2(self.workpath + "CONTROL", cdir + self.get_out_date(date))
        return self


class HyParallel:
    def __init__(
        self,
        files,
        ncpu=4,
        temp_folder="/home/pankaj/phd/code/hytraj/test",
        working="/home/pankaj/phd/code/hytraj/working",
    ):
        self.files = files
        self.ncpu = ncpu
        self.temp_folder = temp_folder
        self.working = working

    def run(self):
        files = glob.glob(self.working + "/*")
        files = [os.path.abspath(filename) for filename in files]
        exe = [filename for filename in files if "hyts" in filename]
        if len(exe) == 0:
            print("HySPLIT Executable (hyts_std) is missing. Put executable in the working directory")
        if not os.path.exists(self.temp_folder):
            os.mkdir(os.path.abspath(self.temp_folder))

        for i in np.arange(self.ncpu):
            fold = self.temp_folder + "/cpu%s" % i
            if not os.path.exists(fold):
                os.mkdir(os.path.abspath(fold))
            [shutil.copy2(filename, fold) for filename in files]

        try:
            Parallel(n_jobs=self.ncpu)(
                delayed(self.run_parallel)(i) for i in np.arange(self.ncpu)
            )
            shutil.rmtree(self.temp_folder)
        except:
            shutil.rmtree(self.temp_folder)
            pass
            

        print("HySPLIT run over!!!!")

    def run_parallel(self, i):
        nfiles = np.array_split(self.files, self.ncpu)[i]
        fold = self.temp_folder + "/cpu%s" % i
        os.chdir(fold)
        for filename in nfiles:
            shutil.copy2(filename, fold + "/CONTROL")
            subprocess.call("./hyts_std")
