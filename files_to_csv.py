import argparse
import csv
import os
import pathlib
import mutagen
import pandas as pd
import pymongo
from bson import json_util
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

debug = False
output_csv = ''
base_dir = ''
file_extensions = ('.flac', '.wav','.mp3', '.m4a', '.aiff')
music_files = []
found_extensions = []
mongo_url = "mongodb://ira.local:27017"
error_count = 0
def main():
	global debug
	global output_csv
	global base_dir
	global file_extensions
	global music_files
	global found_extensions
	global mongo_url
	global error_count
	args = term_args()

	if args.path is None :
			print('input path not specified, using current folder as base')

	# '/Volumes/Storage/Music Library/Music/'  # args.path
	base_dir = '/Volumes/Storage/Music Library/Music/' #args.path #'/Users/benjamenalford/Downloads/Wilco/'
	print(f'Base Directory  = { base_dir}')

	file_count =0
	client = pymongo.MongoClient(mongo_url)
	db = client.MusicLibrary

	default_collection = db.MusicLibrary

	for root, subs, files in os.walk(base_dir):
		for file in files:
			file_ext = pathlib.Path(file).suffix
			if file_ext not in found_extensions:
				found_extensions.append(file_ext)
			if file.endswith(file_extensions):
				file_info = get_file_info(os.path.join(root, file))
				collection = db["Music"]
				collection.insert_one(file_info)
				file_count +=1
				print(f'Wrote file #{file_count}')

	#print(music_files)
	print("file extensions found")
	print(found_extensions)
	print(f"print error count -  {error_count}")
	# music_df = pd.DataFrame(music_files)
	# music_df.to_json("music.json")

def get_file_info(file):
	global error_count
	file_info = {}
	file_info['path'] = file

	try:
		info = mutagen.File(file)

		for keys in info.info.__dict__:
			file_info[keys] = info.info.__dict__[keys]

		#grab the raw tag info
		for item in info.tags.keys():
			if type(info.tags[item]) is not list and type(info.tags[item]) is not bool and item is not 'TDRC':
				if 'text' in info.tags[item].__dict__:
					file_info[item] = info.tags[item].text[0]
				elif 'desc' in info.tags[item].__dict__:
					file_info[item] = info.tags[item].desc[0]
				elif 'data' in info.tags[item].__dict__:
					file_info[item] = info.tags[item].data[0]
			else:
				if item is not 'TDRC':
					file_info[item] = info.tags[item]
				else:
					date =  info.tags[item]
					file_info[item] = date.text[0].text
	except:
		error_count +=1
		pass

	# populate meta data
	try:
		audio = EasyID3(file)
		valid_keys = EasyID3.valid_keys.keys()

		# populate ID3 data
		for keys in valid_keys:
			file_info[keys] = ''
			try:
				file_info[keys] = audio[keys][0]
			except KeyError as e:
				error_count +=1
				pass
	except:
		error_count += 1
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
