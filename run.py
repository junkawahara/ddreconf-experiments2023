#!/usr/bin/python3
# -*- coding: utf-8 -*-

gnutime_pass = '/usr/bin/time'
outdir = 'out/'
timeout_seconds = 7300

import os
import sys
import subprocess
import signal

def main():

    if not os.path.exists(gnutime_pass):
        print('GNU time not found', file = sys.stderr)
        exit(1)

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if not os.path.exists('2022benchmark/ordered'):
        os.mkdir('2022benchmark/ordered')

    with open('2022benchmark/list/list-all-benchmark.csv') as f:
        for line in f:
            col, dat = line.strip().split(',')
            col = '2022benchmark/' + col
            dat = '2022benchmark/' + dat
            dataname = os.path.splitext(os.path.basename(dat))[0]

            ordered_col = col.replace('/benchmark/', '/ordered/')
            ordered_col_dir = os.path.dirname(ordered_col)
            if not os.path.exists(ordered_col_dir):
                os.mkdir(ordered_col_dir)
            out_filename = outdir + dataname + '_out.txt'
            err_filename = outdir + dataname + '_err.txt'
            nc_time_filename = outdir + dataname + '_nc_time.txt'
            rec_time_filename = outdir + dataname + '_rec_time.txt'

            try:
                with open(col) as fin:
                    with open(ordered_col, 'w') as fout:
                        with open(err_filename, 'w') as ferr:
                            proc = subprocess.Popen([gnutime_pass, '-v', '-o', nc_time_filename, 'python3', 'ndscut/ndscut.py', '-d'], stdin = fin, stdout = fout, stderr = ferr)
                            proc.wait(timeout = timeout_seconds)
            except subprocess.TimeoutExpired:
                result = subprocess.run(['pgrep', '-P', str(proc.pid)], stdout = subprocess.PIPE, encoding = 'utf-8')
                child_pid = int(result.stdout.strip())
                os.kill(child_pid, signal.SIGKILL)
            #finally:

            if os.path.exists(ordered_col) and os.path.getsize(ordered_col) > 0:
                try:
                    with open(out_filename, 'w') as fout:
                        with open(err_filename, 'a') as ferr:
                            proc = subprocess.Popen([gnutime_pass, '-v', '-o', rec_time_filename, 'ddreconf/ddreconf', ordered_col, '--st', '--stfile=' + dat, '-q', '--tj', '--indset', '--gc'], stdout = fout, stderr = ferr)
                            proc.wait(timeout = timeout_seconds)
                except subprocess.TimeoutExpired:
                    result = subprocess.run(['pgrep', '-P', str(proc.pid)], stdout = subprocess.PIPE, encoding = 'utf-8')
                    child_pid = int(result.stdout.strip())
                    os.kill(child_pid, signal.SIGKILL)
                finally:
                    if os.path.exists(out_filename) and os.path.getsize(out_filename) == 0:
                        os.remove(out_filename)
                    if os.path.exists(err_filename) and os.path.getsize(err_filename) == 0:
                        os.remove(err_filename)

if __name__ == '__main__':
    main()
