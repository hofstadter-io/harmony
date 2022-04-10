#!/usr/bin/env python3

#
# this is taken from harmony-cue as an example
#

import argparse
import csv
import os
import subprocess

# args and flags to the script
parser = argparse.ArgumentParser()
parser.add_argument('path', nargs='*', help="dagger do action path")
parser.add_argument('--cuepath', help="path to local cue repository")
parser.add_argument('--cue', help="cue version")
parser.add_argument('--dagger', help="dagger version")
parser.add_argument('--go', help="go version")
parser.add_argument('--fmt', help="dagger log format", default="plain")
parser.add_argument('--no-cache', help="disable dagger (buildkit) cache" , action='store_true', default=False)
args = parser.parse_args()

# get full list from cue
p = os.popen("cue eval -e actions.csv --out text")
out = p.read().strip()
actions = list(csv.reader(out.split("\n")))

# start `--with` content
dagger_with = "'actions: { "

# possibly add CUE path
if args.cuepath is not None:
    dagger_with += f"pathToCUE: \"{args.cuepath}\""
    args.cue = "local"

# build up the injected version CUE code
vers = ""
if args.cue is not None:
    if args.cue == "local":
        dagger_with += ", "
    vers += f'cue: "{args.cue}"'
if args.go is not None:
    if vers != "":
        vers += ", "
    vers += f'go: "{args.go}"'
if args.dagger is not None:
    if vers != "":
        vers += ", "
    vers += f'dagger: "{args.dagger}"'

if vers != "":
    dagger_with += f"versions: {{ {vers} }}"

dagger_with += "}'"
# done constructing '--with' content

flags = ["--log-format", args.fmt, "--with", dagger_with]
if args.no_cache:
    flags.append("--no-cache")

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
