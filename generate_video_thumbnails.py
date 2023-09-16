#!/usr/bin/env python
import ffmpeg
import sys
import os
import traceback
import subprocess
import json


def generate_thumbnail(in_filename, out_filename, time, width):
    try:
        (
            ffmpeg.input(in_filename, ss=time)
            .filter("scale", width, -1)
            .output(out_filename, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)


def list_full_paths(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory)]


def get_exif_gps_coord(file, encoding="UTF-8"):
    try:
        command = subprocess.Popen(
            "exiftool -c '%%.6f' -GPSLatitude -GPSLongitude -CreateDate -json \"%(file_path)s\""
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
            return dict(lon=lon, lat=lat, date=meta_data["CreateDate"])
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        sys.exit()
    return None


def geotag_image(file, lat, lon, date):
    subprocess.run(
        'exiftool.exe -GPSLongitude*=%(lon)s -GPSLatitude*=%(lat)s -CreateDate="%(date)s" -Overwrite_Original "%(file_path)s"'
        % dict(file_path=file, lon=str(lon), lat=str(lat), date=date)
    )


def tag_image_create_date(file, date):
    subprocess.run(
        'exiftool.exe -CreateDate="%(date)s" -Overwrite_Original "%(file_path)s"'
        % dict(file_path=file, date=date)
    )


input_folder = r"E:\videos"
output_folder = r"E:\video_thumbnails"
thumbnail_suffix = "_video_thumbnail_"

files = list_full_paths(input_folder)
# files = [r"c:\Users\jack\Desktop\GH014102.MP4"]

extensions = [".mov", ".mp4"]

if __name__ == "__main__":
    for file in files:
        base, ext = os.path.splitext(file)
        if ext.lower() not in extensions:
            print("-------------warning----------------- file type not supported: " + file)
            continue
        print(os.path.basename(base))
        out_filename = (
            os.path.basename(base) + thumbnail_suffix + ext[1:] + ".JPG"
        )
        out_file_path = os.path.join(output_folder, out_filename)
        if os.path.exists(out_file_path):
            meta = get_exif_gps_coord(file)
            tag_image_create_date(out_file_path, meta["date"])
        #     continue
        # generate_thumbnail(file, out_file_path, 0, 800)
        # meta = get_exif_gps_coord(file)
        # print(meta)
        # if meta == None or meta["lat"] == 0:
        #     print("-------------error-----------------", file)
        #     sys.exit(1)
        # geotag_image(out_file_path, meta["lat"], meta["lon"], meta['date'])
