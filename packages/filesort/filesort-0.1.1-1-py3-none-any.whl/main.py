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
from yaspin import yaspin

TITLE = "filesort CLI v0.1.1"


@click.command()
def cli():
    """Primary entry point for GUI operations"""
    instr = input()
    verify(instr)
    outstr = output()
    verify(outstr)
    nameout = outname()
    if nameout == None:
        exit()
    elif nameout == "":
        nameout = None
    outpath = os.path.join(outstr, nameout)
    method = choosemethod()
    if method == None:
        exit()
    out = confirm(instr, outstr, nameout, method)
    if out == None:
        exit()
    elif out == False:
        cli()
    else:
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
        with yaspin(text="Moving files..."):
            for filename in os.listdir(path):
                f = os.path.join(path, filename)
                if os.path.isdir(f):
                    traversedir(f, outpath, method)
                elif os.path.isfile(f):
                    copy(f, outpath, method)


def copy(filepath, outpath, method):
    """Main copy method"""
    if method == "Day" or method == "Month" or method == "Year":
        ctime = time.ctime(os.path.getctime(filepath)).split()
        if method == "Day":
            dest = os.path.join(outpath, ctime[-1], ctime[1], ctime[2])
        elif method == "Month":
            dest = os.path.join(outpath, ctime[-1], ctime[1])
        elif method == "Year":
            dest = os.path.join(outpath, ctime[-1])
    elif method == "File extension":
        dest = outpath + "/" + os.path.splitext(filepath)[1].replace(".", "")
    try:
        if os.path.isdir(dest):
            #! Need to handle filenotfound exception
            shutil.copy2(filepath, dest)
        else:
            os.makedirs(dest)
            shutil.copy2(filepath, dest)
    except PermissionError:
        pass


def input():
    """Queries the user for t/home/vivi/Documents/testing/outdirhe input directory"""
    instr = input_dialog(title=TITLE, text="Path of input:").run()
    if instr == "":
        input()
    else:
        return instr


def output():
    """Queries the user for the output parent directory"""
    outstr = input_dialog(title=TITLE, text="Path of output:").run()
    if outstr == "":
        output()
    else:
        return outstr


def outname():
    """Queries the user for the output folder name"""
    name = input_dialog(title=TITLE, text="Name of output folder:").run()
    if name == "":
        outname()
    else:
        return name


def choosemethod():
    """Prompts the user for the sort method to be used"""
    result = radiolist_dialog(
        title=TITLE,
        text="Sort method:\n[Press space to select]",
        values=[
            ("Day", "/YYYY/MM/DD/"),
            ("Month", "/YYYY/MM/"),
            ("Year", "/YYYY/"),
            ("File extension", "/xxx/ (File extension)"),
        ],
    ).run()
    return result


def confirm(instr, outstr, nameout, method):
    """Queries the user to confirm the validity of their data"""
    out = button_dialog(
        title=TITLE,
        text="Confirm:\nInput folder: "
        + instr
        + "\nOutput folder: "
        + outstr
        + "\nName of output folder: "
        + instr
        + "/"
        + nameout
        + "\nMethod: "
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
    message_dialog(title=TITLE, text=astring + "\nPress ENTER to quit.").run()


# def progressbar(instr):
#     """Displays the progress of the copy"""
# TODO make this like actually work
# for root, dirs, files in os.walk(instr, topdown=False)


if __name__ == "__main__":
    cli()
