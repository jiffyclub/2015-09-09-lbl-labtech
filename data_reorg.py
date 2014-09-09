"""
This script organizes reservoir data files into a directory structure
by reservoir name.

The data files are expected to look like this, with one
year of data per file:

    #NICASIO
    #Date    Storage (AF)
    01/2007     22430
    02/2007     22430
    03/2007     22430
    04/2007     22122
    05/2007     20546
    06/2007     18363
    07/2007     17011
    08/2007     13632

The reservoir name is read from the first line, and the year from
the third line.

"""
from __future__ import print_function

import argparse
import glob
import os
import re
import shutil
import sys
from datetime import datetime


def verify_destination(dest):
    """
    Veryify that the destination directory is a directory (if it exists)
    or create a new directory if it does not exist.

    Parameters
    ----------
    dist : str
        Name of destination directory.

    """
    if os.path.exists(dest):
        if not os.path.isdir(dest):
            raise RuntimeError(
                'Something already exists with the same name '
                'as destination directory!')
    else:
        os.makedirs(dest)


def parse_name_year(fname):
    """
    Grab a reservoir name and data year from a reservoir storage
    data file.

    Parameters
    ----------
    fname : str
        Name of data file.

    Returns
    -------
    reservoir : str
        Name of reservoir. (Will have whitespace removed.)
    year : str
        Year recorded within the file.

    """
    with open(fname, 'r') as f:
        line = f.readline()

        # regular expressions can get the name regardless of whether
        # there are spaces before/after the # comment indicator
        reservoir = re.search(r'#\s*(.*)', line).group(1)
        reservoir = reservoir.replace(' ', '')

        # burn a line to get to the first line of data
        f.readline()

        # first line of data
        date = f.readline().split()[0]
        date = datetime.strptime(date, '%m/%Y')

        return reservoir, str(date.year)


def copy_file(fname, dest, move=False):
    """
    Copy (or move) a file into the new organization structure.
    The file will also be renamed to <reservoir>_<year>.txt.

    Parameters
    ----------
    fname : str
        Name of file to copy.
    dest : str
        Name of destination directory.
    move : bool, False
        If True, move the file instead of copying.

    """
    if move:
        func = shutil.move
    else:
        func = shutil.copy

    reservoir, year = parse_name_year(fname)
    final_dest = os.path.join(dest, reservoir)
    verify_destination(final_dest)
    func(fname, os.path.join(final_dest, '{}_{}.txt'.format(reservoir, year)))


def describe_new_org(dest):
    """
    Print the new layout of the data files.

    Parameters
    ----------
    dest : str
        Destination directory for the data files.

    """
    files = glob.glob(os.path.join(dest, '**', '*.txt'))
    for f in files:
        print(f)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Reorganize reservoir storage data by year and reservoir.')
    parser.add_argument(
        'dest', type=str, help='New directory location for files.')
    parser.add_argument(
        'files', nargs='+', type=str, help='Files to copy or move.')
    parser.add_argument(
        '-m', '--move', action='store_true',
        help='Move files instead of copying.')
    parser.add_argument(
        '-s', '--show', action='store_true',
        help='Print new directory structure when done.')
    return parser.parse_args()


def main():
    args = parse_args()
    verify_destination(args.dest)

    for fname in args.files:
        copy_file(fname, args.dest, args.move)

    if args.show:
        describe_new_org(args.dest)


if __name__ == '__main__':
    sys.exit(main())
