#!/usr/bin/python
# -*- coding: utf-8 -*-
# Alon Yoeli

# import py_phone.adb as adb
import json
import sys
import py_phone.adb as adb
import py_phone.AutoUI as autoui
import py_phone.message as message
from py_phone.uiautomator import device as d
from py_phone import Conditions as conditions
import os
from shutil import copytree
from shutil import copyfile
import shutil
import uiautomator
import time
import datetime
import config

# initiates the time at the start of the test
start_timestamp = int(time.time())

# get and display battery state
rawTemp, perc = conditions.state()
temp = float(rawTemp) / 10
print ('Battery temperature: %s' % temp)
print ('Battery percentage: %s' % perc)

for i in range(1, config.iterations + 1):

    # battery heater/cooler function (in conditions)
    # conditions.main function calls for 1 parameter (path), but doesn't actually use it in the function.
    # in order to bypass this, we concatinate 'None'
    conditions.main(None)
    print '\nBattery Conditions met!!!\n'

    adb.adb_start('com.primatelabs.geekbench', '.HomeActivity')

    if d(text="Accept"):
        d(text="Accept").click.wait()

    d(text="Run Benchmarks").wait.exists()
    d(text="Run Benchmarks").click.wait()

    while d(text="Cancel").exists:
        print 'Waiting for Benchmark test to finish running...'
        time.sleep(5)

    adb.adb_stop('com.primatelabs.geekbench')
    time.sleep(5)
    print '\nIteration %s/%s' % (i, config.iterations) + ' complete'
    progressPerc = float(i) / config.iterations * 100
    print 'Progress: %s percent complete' % progressPerc
    timestamp = int(time.time())
    runTime = timestamp - start_timestamp
    m, s = divmod(runTime, 60)
    h, m = divmod(m, 60)
    print "Test has been running for: "
    print "%d Hours, %02d Minutes, and %02d Seconds" % (h, m, s)

# pulls data file from geekbench
print adb.has_su()
adb.adb_run('cp -r /data/data/com.primatelabs.geekbench/files/ /sdcard/res', su=True)
adb.root_and_mount()

if not os.path.exists('../Results'):
    os.mkdir('../Results')
current_dir = os.getcwd()
os.chdir('../Results')
adb.adb_pull('/sdcard/res/')
os.chdir(current_dir)
adb.adb_run('rm -r /sdcard/res')
adb.adb_run('pm clear com.primatelabs.geekbench')

files = []

# opens the results file
for f1 in os.listdir("/home/user/SVN/Results"):
    if f1.endswith(".gb3"):
        files.append(os.path.join('/home/user/SVN/Results/', f1))

benchmarks = {}

for filename in files:
    with open(filename, "r") as f:
        # turns the results files into a dictionary called data
        data = json.load(f)

        file_scores = {
            'score': data['score'],
            'multicore_score': data['multicore_score'],
            'sections': {}
        }

        for s in data['sections']:
            section_scores = {
                'score': s['score'],
                'multicore_score': s['multicore_score']
            }

            file_scores['sections'][s['name']] = section_scores

        benchmarks[filename] = file_scores

with open("parsed_results.txt", "w") as out:
    def extract_scores(key, src):
        return [str(bm[key]) for bm in src.values()]

    def write_scores(name, key, src):
        out.write('%s Score: ' % name)
        out.write(', '.join(extract_scores(key, src)))
        out.write(os.linesep)

    def list2dict(lst):
        return dict(zip(range(len(lst)), lst))

    write_scores('Overall', 'score', benchmarks)
    write_scores('Overall Multicore', 'multicore_score', benchmarks)

    section_scores = [bm['sections'] for bm in benchmarks.values()]

    def take_each(t):
        return list2dict([s[t] for s in section_scores])

    for t in ['Integer', 'Floating Point', 'Memory']:
        write_scores(t, 'score', take_each(t))
        write_scores('%s Multicore' % t, 'multicore_score', take_each(t))
