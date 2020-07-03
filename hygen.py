import numpy as np
import pandas as pd
import os, glob, subprocess

class HyGen(object):
    def __init__(self, year, stations, height, run_time, working, metdir, outdir, met_type = 'ncep', hysplit='./hyts_std'):
        self.year = year
        self.run_time = run_time
        self.height   = height
        self.stations = stations
        self.workpath = working
        self.metdir   = metdir
        self.met_type = met_type
        self.outdir   = outdir
        self.hysplit  = hysplit
        
    def run(self, vertical=0, model_top=10000.0):
        self.loc = self.get_coordinates(self.stations, self.height)
        start = '01-01-'+str(self.year)+' 05:00:00'
        end   = '12-31-'+str(self.year)+' 05:00:00'
        self.dates =  pd.date_range(start, freq='24H', end=end)
        os.chdir(self.workpath)
        for date in self.dates:
            start_time = self.get_hydate(date)
            outfile    = self.outdir + self.met_type + '.' + str(self.height) + '.' +self.get_out_date(date)
            if self.met_type=='ncep':
                metfiles   = self.get_ncep_metfiles(date)
            else:
                metfiles   = self.get_gdas_metfiles(date)
            metfiles   = [self.metdir + filename for filename in metfiles]
            self.create_control_file(start_time, self.loc, self.run_time, metfiles, self.workpath, outfile, vertical=vertical, model_top=model_top)      
            #subprocess.call(self.hysplit)
        return self
    
    def create_control_file(self, start_time, locations, run_time, metfiles, workpath, outfile, vertical=0, model_top=10000.0):
        with open(workpath + 'CONTROL', 'w') as raus:
            raus.write(start_time + '\n')  # 1
            raus.write('{}\n'.format(len(locations)))  # 2
            raus.write('\n'.join(['{:0.2f} {:0.2f} {:0.1f}'.format(*i) for i in locations]) + '\n')  # 3
            raus.write('{:d}\n'.format(run_time))  # 4
            raus.write('{:d}\n'.format(vertical))  # 5
            raus.write('{:0.1f}\n'.format(model_top))  # 6
            raus.write('{:d}\n'.format(len(metfiles)))  # 7
            for fn in metfiles:
                folder, file = os.path.split(fn)
                raus.write(folder + '/' + '\n')  # 8
                raus.write(file + '\n')  # 9
            folder, file = os.path.split(outfile)
            raus.write(folder + '/' + '\n')
            raus.write(file + '\n')  # 11
            
    @staticmethod        
    def get_ncep_metfiles(date):
        mons = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        curr = 'RP.' + mons[date.month-1] + str(date.year) + '.1.gbl1'    
        if not date.month==1:
            prev = 'RP.' + mons[date.month-2] + str(date.year) + '.1.gbl1'  
        else:
            prev = 'RP.' + mons[-1] + str(date.year-1) + '.1.gbl1'     

        if not date.month==12:
            next = 'RP.' + mons[date.month] + str(date.year) + '.1.gbl1'  
        else:
            next = 'RP.' + mons[0] + str(date.year+1) + '.1.gbl1'
        return [curr, prev, next] 
       
    def get_gdas_metfiles(self, date):
        gdas_file = lambda date: 'gdas1.%s%s.w%s'%(date.month_name().lower()[:3], str(date.year)[-2:], np.round(date.day/7)+1)
        step  = self.run_time
        steps = np.arange(0, step//24, np.sign(step))
        fnames = set([gdas_file(date + pd.Timedelta(s, unit='d')) for s in steps])
        return list(fnames)
    
    @staticmethod  
    def get_coordinates(stations, height):
        locations = []
        loc = {'davs':(-69, 78), 'spol':(-90, 335), 'neum':(-71, 352), 'myth':(-70, 11),
               'syow':(-69, 40), 'marb':(-64, 303), 'mcmu':(-78, 167), 'mirn':(-66, 93)}
        for station in stations:
            lat, lon = loc[station]
            locations.append([lat, lon, height])
        return locations
    
    @staticmethod  
    def get_hydate(date):
        year  = str(date)[2:4]
        month = str(date)[5:7]
        day   = str(date)[8:10]
        hour  = str(date)[11:13]
        start = year + ' ' + month + ' ' + day + ' ' + hour
        return start 
    
    @staticmethod  
    def get_out_date(date):
        tt   =  str(date).split(':')[:-2][0].split('-')
        name = ''.join(tt)
        ts   =  name.split(' ')
        name =  ''.join(ts)
        return name     

height   = 500
year     = 2016
run_time = -360
stations = ['davs', 'marb', 'mcmu', 'spol', 'syow', 'neum']

working = '/home/pankaj/Desktop/hysplit/'
metdir  = '/home/pankaj/mount/repo/repo3/hysplit/gdas1/'
outdir  = '/home/pankaj/Desktop/hysplit/'
hysplit = '/home/pankaj/Desktop/hysplit/hyts_std'

hy = HyGen(year, stations, height, run_time, working, metdir, outdir, met_type = 'gdas', hysplit=hysplit)
hy = hy.run(vertical=0, model_top=10000.0)

