#- Imported Modules

from ast import arg
import os #Built it
import webbrowser #Built in
import re
import sys

#-VAR for Prcs

directory = "{0}".format(os.getcwd())

# Main Demo

def demo():
    commands.demo()
    colors.demo()
#-Classes Module based

class arguments:
    base = sys.argv[0]
    command = sys.argv[1]
    value = sys.argv[2]

class commands:
    #demo of commands

    def demo():
        commands.clearTheScreen()
        commands.printDirectory()
        commands.ipConfig()
        
    #Clear the Screen Command
    def clearTheScreen():
        # for windows
        if os.name == 'nt':
            _ = os.system('cls')
    
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = os.system('clear')

    #print the Directory
    def printDirectory():
        print(directory)

    #ipConfigurations
    def ipConfig():
        os.system('ipconfig')

    #Change Directory
    def changeDirectory(dir):
        os.chdir(dir)
    
class colors:

    #Demo of colors
    def demo():
        print(f"{colors.blue}Hello World (.blue){colors.end}")
        print(f"{colors.red}Hello World (.red){colors.end}")
        print(f"{colors.yellow}Hello World (.yellow){colors.end}")
        print(f"{colors.cyan}Hello World (.cyan){colors.end}")
        print(f"{colors.green}Hello World (.green){colors.end}")
        print(f"{colors.pink}Hello World (.pink){colors.end}")
        print(f"{colors.bold}Hello World (.bold){colors.end}")
        print(f"{colors.underline}Hello World (.underline){colors.end}")

    #Color Table
    pink = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'    

    def cblue(string):
        print(f"{colors.blue}{string}{colors.end}")

    def cyellow(string):
        print(f"{colors.yellow}{string}{colors.end}")

    def cred(string):
        print(f"{colors.red}{string}{colors.end}")

    def cpink(string):
        print(f"{colors.pink}{string}{colors.end}")

    def cyan(string):
        print(f"{colors.cyan}{string}{colors.end}")

    def cgreen(string):
        print(f"{colors.green}{string}{colors.end}")

    def cbold(string):
        print(f"{colors.bold}{string}{colors.end}")

    def cunderline(string):
        print(f"{colors.underline}{string}{colors.end}")

#Sorting commands
def sort(argument='Hello world'):
    result = len(re.findall(r'[\w\.\,/\]\[\=\-\+\)\(\@\!\#\$\%\^\|\&\*\~\`]+', argument))
    number_of_words = int(result)
    return number_of_words



