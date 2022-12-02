import argparse
import os

debug = False
output_csv = ""
base_dir = ""

def main():
	global debug
	global output_csv
	global base_dir

	args = term_args()

	if args.path is None :
			print('input path not specified, using current folder as base')
			exit(1)


def term_args():
	parser = argparse.ArgumentParser(prog='files_to_csv', description='Builds CSV of files')
	parser.add_argument("-p", "--path", type=str, help="Path to start from")
	parser.add_argument("-o", "--output_csv", type=str, help="Output CSV")
	parser.add_argument("-d", "--debug", type=bool,help="debug mode, will not change anything")

	return parser.parse_args()

if __name__ == '__main__':
	main()
