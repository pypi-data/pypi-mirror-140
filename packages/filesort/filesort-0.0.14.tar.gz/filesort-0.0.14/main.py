#!/usr/bin/env python

from unicodedata import name
from prompt_toolkit.shortcuts import (
    input_dialog,
    message_dialog,
    button_dialog,
    radiolist_dialog,
    ProgressBar,
)
import os
import shutil
import time
import click


@click.command()
def cli():
    # TODO later on make it so that I could also just call directly from the command line

    instr = input()
    verify(instr)
    outstr = output()
    verify(outstr)
    nameout = outname()
    if nameout == "":
        nameout = None
    outpath = os.path.join(outstr, nameout)
    method = choosemethod()
    confirm(instr, outstr, nameout, method)
    # progressbar(instr)
    # ! Add an option for copy vs move and to only copy files with a certain file extension
    sort(instr, outpath, method)
    genericmessage("Sort complete!")


def sort(instr, outpath, method):
    """Sorts the input directory into the output directory via the defined sort method"""
    os.mkdir(outpath)
    traversedir(instr, outpath, method)


def traversedir(path, outpath, method):
    """Traverses the input directory recursively until it finds a file. Then calls separate methods for in and out paths and copying."""
    if os.path.isdir(path):
        for filename in os.listdir(path):
            f = os.path.join(path, filename)
            if os.path.isdir(f):
                traversedir(f)
            elif os.path.isfile(f):
                copy(f, outpath, method)


def copy(filepath, outpath, method):
    """Handles days only"""
    ctime = time.ctime(os.path.getctime(filepath)).split()
    if method == "Day":
        dest = outpath + "/" + ctime[-1] + "/" + ctime[1] + "/" + ctime[2] + "/"
    elif method == "Month":
        dest = outpath + "/" + ctime[-1] + "/" + ctime[1] + "/"
    elif method == "Year":
        dest = outpath + "/" + ctime[-1] + "/"
    # TODO Add some more sort methods here
    if os.path.isdir(dest):
        #! Need to handle filenotfound exception
        shutil.copy2(filepath, dest)
    else:
        os.makedirs(dest)
        shutil.copy2(filepath, dest)


def input():
    """Queries the user for t/home/vivi/Documents/testing/outdirhe input directory"""
    instr = input_dialog(title="filesort CLI", text="Path of input:").run()
    if instr == "":
        input()
    else:
        return instr


def output():
    """Queries the user for the output parent directory"""
    outstr = input_dialog(title="filesort CLI", text="Path of output:").run()
    if outstr == "":
        output()
    else:
        return outstr


def outname():
    """Queries the user for the output folder name"""
    name = input_dialog(title="filesort CLI", text="Name of output folder:").run()
    if name == "":
        outname()
    else:
        return name


def choosemethod():
    """Prompts the user for the sort method to be used"""
    result = radiolist_dialog(
        title="filesort CLI",
        text="Sort method:\n[Press space to select]",
        values=[("Day", "/YYYY/MM/DD/"), ("Month", "/YYYY/MM/"), ("Year", "/YYYY/")],
    ).run()
    return result


def confirm(instr, outstr, nameout, method):
    """Queries the user to confirm the validity of their data"""
    out = button_dialog(
        title="filesort CLI",
        text="Confirm:\nInput folder:"
        + instr
        + "\nOutput folder:"
        + outstr
        + "\nName of output folder:"
        + instr
        + "/"
        + nameout
        + "\nMethod:"
        + method
        + "\nIs this information correct?",
        buttons=[("Yes", True), ("No", False), ("Cancel", None)],
    ).run()
    return out


def verify(checkstr):
    """Exits the program if the string is none"""
    if checkstr == None:
        exit()


def genericmessage(astring):
    """Generates a generic message based on astring"""
    message_dialog(title="filesort CLI", text=astring + "\nPress ENTER to quit.").run()


# def progressbar(instr):
#     """Displays the progress of the copy"""
# TODO make this like actually work
# for root, dirs, files in os.walk(instr, topdown=False)


if __name__ == "__main__":
    cli()
