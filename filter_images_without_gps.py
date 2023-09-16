import exiftool
import os
from os import listdir
from os.path import join, splitext
import glob
import sys
import subprocess
import traceback
import json

# path = r"C:\Users\jack\Desktop\heic"
# for filename in listdir(path):

# files = [
#     "d:\youtuber\dongjiang\iphone\IMG_9527.JPG",
#     r"c:\Users\jack\Desktop\GH014102.MP4",
#     r"d:\gopro\GH014011.MP4",
#     "d:\youtuber\dongjiang\iphone\DQWE7429.MP4",
#     "d:\youtuber\dongjiang\iphone\IMG_2351.PNG",
# ]
# files = listdir(path=r"d:\gopro")
# dir = r"D:\gopro"
# dir = r"d:\youtuber\dongjiang\iphone"
dir = r"E:\gopro"
# dir = r"E:\iphone"
exts = [".jpeg", ".png", ".jpg", ".mov", ".mp4"]


def find_case_insensitve(dirname, extensions):
    _files = []
    # for filename in listdir(dirname):
    for filename in glob.glob(dirname + r"\*"):
        base, ext = os.path.splitext(filename)
        if ext.lower() in extensions:
            _files.append(filename)
        else:
            print(filename)
    return _files

def get_exif_gps_coord(file, encoding="UTF-8"):
    try:
        command = subprocess.Popen(
            "exiftool -c '%%.6f' -GPSLatitude -GPSLongitude -json \"%(file_path)s\""
            % dict(file_path=file),
            stdout=subprocess.PIPE,
            encoding=encoding,
            shell=True,
        )
        # command_output = command.stdout.read()
        # print(command_output)
        meta_data = json.load(command.stdout)[0]
        print(meta_data)
        if meta_data.get("GPSLatitude") != None:
            gps_lon = str(meta_data["GPSLongitude"])
            gps_lat = str(meta_data["GPSLatitude"])
            multiplier = 1 if gps_lon[-1] == "E" else -1
            lon = multiplier * float(gps_lon[:-2].replace("'", ""))
            multiplier = 1 if gps_lat[-1] == "N" else -1
            lat = multiplier * float(gps_lat[:-2].replace("'", ""))
            return dict(lon=lon, lat=lat)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        sys.exit()
    return None


files = find_case_insensitve(dir, exts)

# files = [
#     "d:\media_no_gps\自行车发电机电压超高.MP4",
#     "E:\iphone\海战博物馆.JPG",
#     "e:\iphone\IMG_3406.JPG",
# ]
# print(files)
# sys.exit(0)
files_no_gps = []

for file in files:
    print("-------------------", file)
    if "GH" in file:
        continue
    location = get_exif_gps_coord(file)
    if location is None or location.lat == 0:
        print(file)
        files_no_gps.append(file)

if len(files_no_gps) > 0:
    files_path_str = ",".join(files_no_gps)
    p = os.system("show_in_file_manager.exe " + files_path_str)



# exiftool -ee -p gpx.fmt D:\media_no_gps\GH014044.MP4
