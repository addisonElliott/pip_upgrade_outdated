#!/usr/bin/env python2
"""
This script upgrades all outdated python packages.
"""


## based on https://gist.github.com/serafeimgr/b4ca5d0de63950cc5349d4802d22f3f0
## __author__ = "serafeimgr"
## modified by AHJ to allow different pip executables (pip2, pip3, etc)
## do we really want to do this with multiprocessing, or just a single giant call to pip?
## does the parsing really work given the new-style headers in the formatting?
##  -- no: needed to add --format legacy; could also use freeze (split with "==")
##  -- changed to use --format json to let someone else do the parsing for me...

from __future__ import print_function

from multiprocessing import Pool, cpu_count
from subprocess import PIPE, Popen

import json
import argparse
import functools

__version__ = "0.9"

def run_command(command):
    """
    Executes a command.
    @param: command
    """
    stdout, stderror = Popen(command,
                             stdout=PIPE,
                             stderr=PIPE,
                             shell=True).communicate()
    return stdout, stderror


def upgrade_package(package, pip_cmd="pip", dry_run=False, verbose=False):
    """
    Upgrade a package.

    @param: package
    """
    upgrade_command = " ".join((pip_cmd,"install --upgrade {}".format(package)))

    if verbose and upgrade_command:
        print("Upgrade command: ", upgrade_command)

    if not dry_run:
        stdout, stderr = run_command(upgrade_command)
        if stderr:
            print("Error:", stderr)
        print(stdout)
            

def collect_packages(pip_cmd="pip", verbose=False):
    """
    Collect outdated packages.

    @returns : packages
    """

    outdated_command = " ".join((pip_cmd,"list --outdated --format json"))
    stdout, stderr = run_command(outdated_command)
    
    if stderr:
        print("Error:", stderr)
    
    if verbose and stdout and stdout!='[]\n':
        print(stdout)

    pkgs = json.loads(stdout)
    return [p['name'] for p in pkgs]
    

def main():
    """Upgrade outdated python packages."""
    
    ## AHJ: all argparse stuff new
    descr = 'upgrade outdated python packages with pip.'
    
    parser = argparse.ArgumentParser(description=descr)
    group=parser.add_mutually_exclusive_group()
    group.add_argument("-3", dest="pip_cmd", action="store_const", const="pip3", default="pip", help="use pip3")
    group.add_argument("-2", dest="pip_cmd", action="store_const", const="pip2", default="pip", help="use pip2")
    group.add_argument("--pip_cmd", action="store", default="pip", help="use PIP_CMD (default pip)")
    parser.add_argument("--verbose", "-v", action="count", default=0, help="may be specified multiple times")
    parser.add_argument("--dry_run", "-n", action="store_true", help="get list, but don't upgrade")
    parser.add_argument("--serial", "-s", action="store_true", help="upgrade in serial rather than parallel")
    parser.add_argument('--version', action='version', 
                        version='%(prog)s '+__version__)

    args = parser.parse_args()

    pip_cmd = args.pip_cmd
        
    if args.verbose>1:
        print(args)
        print("pip_cmd=%s" % pip_cmd)

    
    packages = collect_packages(pip_cmd=pip_cmd, verbose=args.verbose)
    if args.verbose and packages:
        print("Collected: ", packages)
    if not args.serial:
        if args.verbose>1: 
            print("Parallel execution")
        pool = Pool(cpu_count())
        pool.map(functools.partial(upgrade_package, 
                                   pip_cmd=pip_cmd, dry_run=args.dry_run, verbose=args.verbose), 
                 packages)
        pool.close()
        pool.join()
    else:
        if args.verbose>1: 
            print("Serial execution")

        all_packages = " ".join(packages)
        upgrade_package(all_packages, pip_cmd=pip_cmd, dry_run=args.dry_run, verbose=args.verbose)

# 
# 
# if __name__ == '__main__':
#     main()
