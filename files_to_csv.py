import argparse
import os
import pathlib
import mutagen
import pymongo
from mutagen.easyid3 import EasyID3

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

	print("file extensions found")
	print(found_extensions)
	print(f"print error count -  {error_count}")

def get_file_info(file):
	global error_count
	file_info = {}
	file_info['path'] = file

	try:
		info = mutagen.File(file)

		for keys in info.info.__dict__:
			k,v = sanitize(keys, info.info.__dict__[keys])
			file_info[k] = v

		#grab the raw tag info
		for item in info.tags.keys():
			if type(info.tags[item]) is not list and type(info.tags[item]) is not bool and item not in ['TDRC', 'TDTG', 'TDOR','TDEN'] :
				if 'text' in info.tags[item].__dict__:
					k, v = sanitize(item, info.tags[item].text)
					file_info[k]=v
				elif 'desc' in info.tags[item].__dict__:
					k, v = sanitize(item, info.tags[item].desc)
					file_info[k] = v
				elif 'data' in info.tags[item].__dict__:
					k, v = sanitize(item, info.tags[item].data)
					file_info[k] = v
			else:
				if item not in ['TDRC', 'TDTG', 'TDOR','TDEN']:
					k, v = sanitize(item, info.tags[item])
					file_info[k] = v
				else:
					k, v = sanitize(item, info.tags[item].text[0].text)
					file_info[k] = v
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
			if keys in audio.__dict__:
				k,v = sanitize(keys, audio[keys])
				file_info[k] = v
	except:
		error_count += 1
		pass

	return file_info

def sanitize(key, value):
	key = key.replace('\x00', '0')
	value = value
	key = key
	if (type(value) is list):
		value = value[0].strip()
	elif(type(value) is bool):
		value = value
	elif (type(value)  is str):
		value = value.strip()
	else:
		value= value
	return key, value

def term_args():
	parser = argparse.ArgumentParser(prog='files_to_csv', description='Builds CSV of files')
	parser.add_argument('-p', '--path', type=str, help='Path to start from',default='.')
	parser.add_argument('-o', '--output_csv', type=str, help='Output CSV')
	parser.add_argument('-d', '--debug', type=bool,help='debug mode, will not change anything')

	return parser.parse_args()

if __name__ == '__main__':
	main()
