import argparse
import os
import csv
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

debug = False
output_csv = ''
base_dir = ''
file_extensions = ('.flac', '.wav','.mp3', '.m4a', '.aiff')

def main():
	global debug
	global output_csv
	global base_dir
	global file_extensions

	args = term_args()

	if args.path is None :
			print('input path not specified, using current folder as base')

	base_dir = args.path
	print(f'Base Directory  = { base_dir}')

	music_files = []

	for root, subs, files in os.walk(base_dir):
		for file in files:
			if file.endswith(file_extensions):
				file_info = get_file_info(os.path.join(root, file))
				music_files.append(file_info)

	print(music_files)

def get_file_info(file):
	file_info = {}
	info = mutagen.File(file)

	file_info['path'] = file
	# populate meta data
	for keys in info.info.__dict__:
		file_info[keys] = info.info.__dict__[keys]

	audio = EasyID3(file)
	valid_keys = EasyID3.valid_keys.keys()

	# populate ID3 data
	for keys in valid_keys:
		file_info[keys] = ''
		try:
			file_info[keys] = audio[keys][0]
		except KeyError as e:
			pass

	return file_info

def term_args():
	parser = argparse.ArgumentParser(prog='files_to_csv', description='Builds CSV of files')
	parser.add_argument('-p', '--path', type=str, help='Path to start from',default='.')
	parser.add_argument('-o', '--output_csv', type=str, help='Output CSV')
	parser.add_argument('-d', '--debug', type=bool,help='debug mode, will not change anything')

	return parser.parse_args()

if __name__ == '__main__':
	main()
