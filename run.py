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

    with open('2022benchmark/list/list-all-benchmark.csv') as f:
        for line in f:
            col, dat = line.strip().split(',')
            col = '2022benchmark/' + col
            dat = '2022benchmark/' + dat
            dataname = os.path.splitext(os.path.basename(dat))[0]

            out_filename = outdir + dataname + '_out.txt'
            err_filename = outdir + dataname + '_err.txt'
            time_filename = outdir + dataname + '_time.txt'

            try:
                with open(out_filename, 'w') as fout:
                    with open(err_filename, 'w') as ferr:
                        proc = subprocess.Popen([gnutime_pass, '-v', '-o', time_filename, 'ddreconf/ddreconf', col, '--st', '--stfile=' + dat, '-q', '--tj', '--indset', '--gc'], stdout = fout, stderr = ferr)
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
