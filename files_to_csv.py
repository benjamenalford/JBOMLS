import argparse
import os
import csv
import mutagen

debug = False
output_csv = ""
base_dir = ""
file_extensions = (".flac", ".wav",".mp3", ".m4a", ".aiff")

def main():
	global debug
	global output_csv
	global base_dir
	global file_extensions

	args = term_args()

	if args.path is None :
			print('input path not specified, using current folder as base')
			exit(1)

	for root, subs, files in os.walk(base_dir):
		for file in files:
			if file.endswith(file_extensions):
				file_info = get_file_info(file)


def get_file_info():
	info = mutagen.File("11. The Way It Is.ogg")
	return info

def term_args():
	parser = argparse.ArgumentParser(prog='files_to_csv', description='Builds CSV of files')
	parser.add_argument("-p", "--path", type=str, help="Path to start from")
	parser.add_argument("-o", "--output_csv", type=str, help="Output CSV")
	parser.add_argument("-d", "--debug", type=bool,help="debug mode, will not change anything")

	return parser.parse_args()

if __name__ == '__main__':
	main()
