#! python3
from showinfm import show_in_file_manager
import sys
import os
import configparser
import urllib
import logging

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
config.read(ini_path)
folder_path = config["DEFAULT"]["path"].strip()
args = sys.argv[1:]
print(config['DEFAULT']['enable_log'])
if config['DEFAULT']['enable_log'] == 'true':
    logging.basicConfig(
        filename=os.path.join(os.path.abspath(os.path.dirname(ini_path)),logFile),
        filemode="a",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s: %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    logging.debug('sys.argv: ' + str(sys.argv))

# arg showinfilemanager:2.txt,3.txt
arg_str = args[0]
if len(args) == 1 and ":" in arg_str:
    args = urllib.parse.unquote(arg_str).split(":")[1].split(",")
files = [os.path.join(folder_path, file_path.strip()) for file_path in args]
print(files)
show_in_file_manager(files)
#pyinstaller --onefile show_in_file_manager.py
