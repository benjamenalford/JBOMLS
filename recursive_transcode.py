import os
import argparse

lossless_extensions = (".flac", ".wav")
destination_codec = 'alac'
debug = False
inplace = False
output_dir = ""
base_dir = ""


def main():
    global debug
    global inplace
    global lossless_extensions
    global output_dir
    global base_dir
    global destination_codec
    args = term_args()

    if args.debug:
        debug = True
        print("Debug mode on")
        print(args)

    if args.path is None or (args.output_path is None and args.inplace is False):
        print('input path or output path not specified')
        exit(1)
    if args.inplace is not None:
        inplace = True
    base_dir = args.path
    if inplace:
        output_dir = base_dir
    else:
        output_dir = args.output_path

    print(f'Base Directory  = { base_dir}')
    print(f'Output Directory = {output_dir}')
    print(f'Output Codec = {destination_codec}')

    for root, subs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(lossless_extensions):
                convert(file, root)


def convert(file, path):
    global debug
    global inplace
    global lossless_extensions
    global output_dir
    global base_dir
    global destination_codec

    print(file)
    file_folder = os.path.basename(path)

    destination_folder = os.path.join(output_dir, file_folder)
    if ((os.path.exists(destination_folder) is False) and (debug is False)) and (inplace is False):
        os.mkdir(destination_folder)

    for file_extension in lossless_extensions:
        if (file.endswith(file_extension)):
            out_file = file.split(file_extension)[0]

    cmd = f'ffmpeg -i "{os.path.join(path , file)}" -y -v 0 -vcodec copy -acodec {destination_codec} "{os.path.join(destination_folder,out_file)}.m4a"'

    if debug:
        print(cmd)
    else:
        os.system(cmd)


def term_args():
    parser = argparse.ArgumentParser(
        prog='recursive_transcode', description='Transcodes a folder recursively')
    parser.add_argument("-p", "--path", type=str,
                        help="Path to be transcoded.")
    parser.add_argument("-o", "--output_path", type=str, help="Output path")
    parser.add_argument("-c", "--output_codec", type=str, help="Output codec")
    parser.add_argument("-i", "--inplace", type=bool,
                        help="Transcode In Place")
    parser.add_argument("-d", "--debug", type=bool,
                        help="debug mode, will not change anything")

    return parser.parse_args()


if __name__ == '__main__':
    main()
