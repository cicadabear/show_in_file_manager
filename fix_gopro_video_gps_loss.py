#! python3
import gpxpy
import subprocess
import os
import exiftool
import json
import sys
import traceback

def list_full_paths(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory)]


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


def geotag_video(file):
    gpx_data = subprocess.run(
        'exiftool -ee -p gpx.fmt "%(file_path)s"' % dict(file_path=file),
        capture_output=True,
        shell=True,
        text=True,
    ).stdout
    gpx = gpxpy.parse(gpx_data)
    point = gpx.tracks[0].segments[0].points[10]
    # point_end = gpx.tracks[0].segments[0].points[-1]
    i = 1
    while point.latitude == 0:
        point = gpx.tracks[0].segments[i].points
        i += 1
    print(point.longitude, point.latitude)
    subprocess.run(
        'exiftool.exe -GPSLongitude*=%(lon)s -GPSLatitude*=%(lat)s -api largefilesupport=1 -Overwrite_Original "%(file_path)s"'
        % dict(file_path=file, lon=point.longitude, lat=point.latitude)
    )


# ------------------------------------------------------

dir = r"E:\gopro_no_gps"
files = list_full_paths(dir)
# files = [
#     # r"e:\gopro\GH014238.MP4",
#     # r"c:\Users\jack\Desktop\IGYR6307.MP4",
#     r"E:/gopro_no_gps/临江镇东江大桥.MP4",
#     r"E:\gopro\河源博物馆.MP4",
#     r"E:\gopro\河源西环路新丰江大桥.MP4",
#     r"d:\gopro\斗宴水库骑行.MP4",
#     r"d:\gopro\留车镇上游骑行下雨前.MP4",
# ]

for file in files:
    print(file)
    base, ext = os.path.splitext(file)
    if ext.lower() != ".mp4":
        continue
    location = get_exif_gps_coord(file, encoding="UTF-8")
    print(location)
    if location is not None and location["lat"] != 0:
        continue

    geotag_video(file)
