import argparse
import os
import pathlib
import mutagen
import pymongo
import eyed3
import mutagen.easyid3
from mutagen.easyid3 import EasyID3

debug = False
output_csv = ''
base_dir = ''
file_extensions = ('.flac', '.wav', '.mp3', '.m4a', '.aiff', '.m4p', '.mp4')
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
				file_info = get_file_info_new(os.path.join(root, file))
				collection = db["Music"]
				collection.insert_one(file_info)
				file_count +=1
				print(f'Wrote file #{file_count}')

	print("file extensions found")
	print(found_extensions)
	print(f"print error count -  {error_count}")

def get_file_info_new(file):
	global error_count
	file_info = {}
	file_info['path'] = file
	try:
		audio_file = mutagen.File(file)
		if audio_file:
			if audio_file.info:
				file_info['bitrate'] = audio_file.info.bitrate
				file_info['sample_rate'] = audio_file.info.sample_rate
				file_info['time'] = audio_file.info.length
			else:
				print(f'error parsing info: {file}')
			if audio_file.tags:
				file_info['artist'] = audio_file.tags.get('TPE1')
				file_info['album_artist'] = audio_file.tags.get('TCOM')
				file_info['title'] = audio_file.tags.get('TIT1')
				file_info['album'] = audio_file.tags.get('TALB')
				file_info['track_num'] = audio_file.tags.get('TRCK')
				file_info['disc_num'] = audio_file.tags.get('TPOS')
			else:
				print(f'error parsing tags: {file}')
		else:
			print(f'error loading file: {file}')
	except mutagen.mp4.MP4MetadataError as e :
		print(file,"error",e)
	except mutagen.mp3.HeaderNotFoundError as e:
		print(file,"error" ,e)
	finally:
		error_count += 1

	try:
		audio_file = EasyID3(file)
		# populate ID3 data
		if audio_file:
			file_info['time'] = audio_file.get('length')
			file_info['artist'] = audio_file.get('artist')
			file_info['album_artist'] = audio_file.get('albumartist')
			file_info['title'] = audio_file.get('title')
			file_info['album'] = audio_file.get('album')
			file_info['track_num'] = audio_file.get('tracknumber')
			file_info['disc_num'] = audio_file.get('discnumber')
			file_info['compilation'] = audio_file.get('compilation')
	except Exception as e:
		print("error",file, e)
	for key,value in file_info.items():
		if type(value) not in [str, int, float] and value != None:
			if type(value) is list:
				file_info[key] = value[0]
			else:
				file_info[key]=value.text[0]
		elif file_info[key] == None:
			file_info[key] =''
		else:
			file_info[key] = value
	return file_info
def get_file_info_eyed3(file):
	file_info = {}
	file_info['path'] = file
	audio_file = eyed3.load(file)
	if audio_file:
		if audio_file.info:
			file_info['bitrate'] = audio_file.info.bit_rate_str
			file_info['endcode_mode'] = audio_file.info.mode
			file_info['sample_rate'] = audio_file.info.sample_freq
			file_info['time'] = audio_file.info.time_secs
			file_info['file_size'] = audio_file.info.size_bytes
		else:
			print(f'error parsing info: {file}')
		if audio_file.tag:
			file_info['artist'] = audio_file.tag.artist
			file_info['album_artist'] = audio_file.tag.album_artist
			file_info['disc_num'] = audio_file.tag.disc_num.count
			file_info['disc_total'] = audio_file.tag.disc_num.total
			file_info['title'] = audio_file.tag.title
			file_info['track_num'] = audio_file.tag.track_num.count
			file_info['track_count'] = audio_file.tag.track_num.total
		else:
			print(f'error parsing tags: {file}')
	else:
		print(f'error loading file: {file}')
	return file_info
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
		print(f'Error opening: {file}' )
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
