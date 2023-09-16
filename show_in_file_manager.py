#! python3
from showinfm import show_in_file_manager
import sys
import os
import configparser
import urllib
import logging
import json

logFile = "show_in_file_manager.log"
exe_dir = os.path.abspath(os.path.dirname(sys.executable))
script_dir = os.path.abspath(os.path.dirname(__file__))

exe_ini_path = os.path.join(exe_dir, "show_in_file_manager.ini")
script_ini_path = os.path.join(script_dir, "show_in_file_manager.ini")

ini_path = ""
if os.path.isfile(exe_ini_path):
    ini_path = exe_ini_path
elif os.path.isfile(script_ini_path):
    ini_path = script_ini_path

if ini_path == "":
    raise RuntimeError("ini configuration file cannot be found.")

config = configparser.ConfigParser()
config.read(ini_path, encoding="UTF-8")
folder_path = config["DEFAULT"]["path"].strip()
# if paths is configured in ini file and not empty, path will be ignored.
folder_paths = config.get("DEFAULT", "paths")


if config["DEFAULT"]["enable_log"] == "true":
    logging.basicConfig(
        filename=os.path.join(os.path.abspath(os.path.dirname(ini_path)), logFile),
        filemode="a",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s: %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    logging.debug("sys.argv: " + str(sys.argv))

args = sys.argv[1:]
# arg showinfilemanager:2.txt,3.txt
# arg_str = args[0]
args = ["GH014055_video_thumbnail_mp4.JPG"]
files = []
is_abs_path = False
# process opening from web or showinfm.exe 1.txt,2.txt
if len(args) == 1 and ("showinfilemanager:" in args[0] or "," in args[0]):
    args = (
        urllib.parse.unquote(args[0])
        .split("showinfilemanager:")[1 if "showinfilemanager:" in args[0] else 0]
        .split(",")
    )
elif len(args) == 1 and "_files.txt" in args[0]:
    is_abs_path = True
    with open(args[0]) as file:
        files = [line.strip().replace("/", os.sep) for line in file]

if len(files) == 0:
    files = [file_path.strip() for file_path in args]

thumbnail_suffix = "_video_thumbnail_"

if not is_abs_path:
    if thumbnail_suffix in files[0]:
        for i in range(len(files)):
            file = files[i]
            base, ext = os.path.splitext(file)
            files[i] = base.split(thumbnail_suffix)[0] + "." + base.split("_")[-1]

    folder_path_from_paths = ""
    if folder_paths is not None and folder_paths != "":
        if "\\" in folder_paths:
            folder_paths = folder_paths.replace("\\", "\\\\")
        folder_paths = json.loads(folder_paths)
    if len(folder_paths) > 0:
        for path in folder_paths:
            if os.path.exists(os.path.join(path.strip(), files[0])):
                folder_path_from_paths = path.strip()
                break

    if folder_path_from_paths != "":
        folder_path = folder_path_from_paths

    files = [os.path.join(folder_path, file_path) for file_path in files]

logging.debug("show_in_file_manager files: " + str(files))

show_in_file_manager(files)
# pyinstaller --onefile show_in_file_manager.py

# show_in_file_manager.exe showinfilemanager:IMG_2312.JPG,IMG_2308.JPG
# show_in_file_manager.exe IMG_2312.JPG,IMG_2308.JPG
# show_in_file_manager.exe IMG_2312.JPG IMG_2308.JPG
# show_in_file_manager.exe xxx_files.txt
# xxx_files.txt
# d:\youtuber\dongjiang\iphone\IMG_2537.JPG
# d:\youtuber\dongjiang\iphone\IMG_2541.JPG
# d:\youtuber\dongjiang\iphone\IMG_2558.JPG
