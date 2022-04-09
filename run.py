#!/usr/bin/env python3

import argparse
import csv
import os
import subprocess

# args and flags to the script
parser = argparse.ArgumentParser()
parser.add_argument('path', nargs='*', help="dagger do action path")
parser.add_argument('--cue', help="cue version", default="v0.4.3-beta.2")
parser.add_argument('--dagger', help="dagger version", default="v0.2.4")
parser.add_argument('--go', help="go version", default="1.18")
parser.add_argument('--fmt', help="dagger log format", default="plain")
args = parser.parse_args()

# get full list from cue
p = os.popen("cue eval -e actions.csv --out text")
out = p.read().strip()
actions = list(csv.reader(out.split("\n")))

# build up the injected version CUE code
versT = (args.cue, args.dagger, args.go)
versS = 'cue: "{0}", dagger: "{1}", go: "{2}"'.format(*versT)
dagger_with = f"'actions: versions: {{ {versS} }}'"
flags = ["--log-format", args.fmt, "--with", dagger_with]

for action in actions:
    # enable pass through of dagger do args
    match = True
    for i, p in enumerate(args.path):
        if p != action[i]:
            match = False
            break

    if match:
        cmd = ["dagger", "do"] + action + flags
        print("Running:", " ".join(cmd))
        subprocess.run(["bash", "-c", " ".join(cmd)], check=True)
