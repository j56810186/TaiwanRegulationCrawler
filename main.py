# NOT GOOD TO USE, CANNOT DEBUGGIN MY SCRAPY PROJECT, DEPRECATED.

# This main.py file is used to call scrapy command, since it is not easy to call it with vscode debugger.
# This is a very simple utility, it probably have a lot of bugs, but in my usage it is ok.

import argparse
import subprocess

parser = argparse.ArgumentParser(description="This is the scrapy caller in this project, you can give any scrapy command here.")
parser.add_argument('commands_and_arguments', nargs='+', help='The scrapy commands and arguments you want to call.')
args = parser.parse_args()

commands_and_arguments = args.commands_and_arguments

subprocess.run(['scrapy'] + commands_and_arguments)
