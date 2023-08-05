# See LICENSE for license details.

import argparse
import os
import sys
import pkg_resources
import shutil

# Check if this is run from a local installation
milldir = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
if os.path.exists(os.path.join(milldir, "mill_bin")):
    sys.path[0:0] = [milldir]

from mill_bin import __version__

def get_resource_name(name):
    return pkg_resources.resource_filename(__name__, name)

def get_resource_string(name):
    return pkg_resources.resource_string(__name__, name)

source = get_resource_name('assets/mill')

class MILLBin:
    def create(self, args):
        jars_path = args.dest_path
        if not os.path.exists(jars_path):
            os.mkdir(jars_path)

        shutil.copyfile(source, os.path.join(jars_path, 'mill'))

def parse_args():
    parser = argparse.ArgumentParser()

    # Global actions
    parser.add_argument(
        "--version",
        help="Show the Mill Binary version",
        action="version",
        version=__version__,
    )

    parser.add_argument(
        'dest_path', metavar="destination", type=str, nargs='?',
        default='.', help='Copy to the destination path')
    parser.set_defaults(func=create)

    args = parser.parse_args()

    if hasattr(args, "func"):
        return args
    if hasattr(args, "subparser"):
        args.subparser.print_help()
    else:
        parser.print_help()
        return None

def create(args):
    sc = MILLBin()
    sc.create(args)

def main():
    args = parse_args()
    if not args:
        exit(0)

    # Run the function
    args.func(args)

if __name__ == "__main__":
    main()
