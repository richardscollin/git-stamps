#!/usr/bin/env python3
import click
import os
import subprocess
import datetime
import dateutil.parser

@click.command()
@click.argument("screencast", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument("git_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
def git_stamps(screencast, git_dir):
    """
    This program takes a video file generate by obs studio and a git directory
    containing commits that were created during the screen cast. It then generates
    timestamps for youtube corresponding to the commit timestamps in the video.

    ./git-stamps.py 2020-11-04 23-28-02.mkv code/

    00:00:00 - Intro & Add i18n
    02:36:09 - Add app bar
    00:47:13 - Add vue router
    00:15:55 - Conclusion


    WARNING!! Do not use this script on untrusted user input!
    A carefully constructed file name could execute arbitrary code!
    """

    # Assume screencast file is in the following format:
    # 2020-11-04 23-28-02.mkv
    basename = os.path.basename(screencast)
    info = basename.split('.')[0]
    dateinfo = info.split()[0]
    timeinfo = info.split()[1]
    (year, month, day) = [int(x) for x in dateinfo.split('-')]
    (hour, minute, second) = [int(x) for x in timeinfo.split('-')]

    start_ts  = datetime.datetime(year, month, day, hour, minute, second).timestamp()

    # TODO on escape git_dir - code exec vuln here
    output = subprocess.check_output(["git", "-C", git_dir, "log",
        "--since=" + str(int(start_ts)),
        "--format=%ct\t%s"
        ]).decode()

    times = ['00:00:00']
    descriptions = []
    
    for line in output.split('\n'):
        if line.strip():
            (ts, subject) = line.split('\t')
            seconds = int(int(ts) - start_ts)
            (minutes, seconds) = divmod(seconds, 60)
            (hours, minutes) = divmod(minutes, 60)
            res = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
            times.append(res)
            descriptions.append(subject)

    descriptions[0] = "Intro & " + descriptions[0]
    descriptions.append('Conclusion')

    for (t, d) in zip(times, descriptions):
        print(t + " - " + d)

if __name__ == "__main__":
    git_stamps()
