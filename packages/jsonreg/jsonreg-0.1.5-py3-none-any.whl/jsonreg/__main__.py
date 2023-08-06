import datetime
import os
import json
import pylog
import argparse
from colorama import Fore, Back, Style
try:
    import jsonreg
except:
    print("I see you don't have jsonreg installed can you install it using python -m pip install jsonreg")
    exit()
try:
    from tabulate import tabulate
except:
    print("I see you don't have tabulate installed can you install it using python -m pip install tabulate")
    exit()
global verbose
verbose = False
start_time = datetime.datetime.now().strftime("%b-%d-%Y")
parser = argparse.ArgumentParser(description='')
class log:
    def message(log_message):
        if verbose == True:
            print("[OK]"+log_message)
            pylog.log(start_time+".log",log_message)
    def error(log_message):
        if verbose == True:
            print("[ERROR]"+log_message)
            pylog.error(start_time+".log",log_message)
def list():
    print("JSONreg files in this directory:")
    num = 1
    names = []
    ids = []
    clashes_names = []
    clashes_ids = []
    current_dir = ""
    table = []
    for root, dir, files in os.walk("."):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                if data["name"] in names:
                    clashes_names.append(str(os.path.join(root, file)))
                elif data["id"] in ids:
                    clashes_ids.append(str(os.path.join(root, file)))
                num = num + 1 
                names .append(data["name"])
                ids.append(data["id"])
                table.append([str(data["name"]),str(data["id"]),str(data["data"]),len(str(data["data"]))])
    print(tabulate(table ,headers=["Name","ID","Data","Data Size"]))
    if len(clashes_ids) > 0:
        print(Fore.YELLOW+"The following JSONreg id's are clashing with another key consider changing them"+Style.RESET_ALL)
        print(clashes_ids)
    if len(clashes_names) > 0:
        print(Fore.YELLOW+"The following JSONreg names are clashing with another key consider changing them"+Style.RESET_ALL)
        print(clashes_names)   
def remove():
    print(Fore.RED+"Warning: This will PERMANENTLY delete the JSONreg file"+Style.RESET_ALL)
    file_name = input("Enter file or id>")
    for root, dir, files in os.walk("."):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file)) as f:
                    data = json.loads(f.read())
                if str(data["id"]) == file_name:
                    del data
                    os.remove(os.path.join(root, file))
                    return "Done"
    if file.endswith(".json") == False:
        print("This is not a JSONreg file. Please use a .json file")
    try:
        os.remove(file_name)
    except FileNotFoundError:
        log.error("File: "+file_name+" dose not exist")
        print(Fore.RED+"This file dose not exist"+Style.RESET_ALL)
def create():
    file_name = input("File location>")
    name = input("Name>")
    data = input("Data>")
    jsonreg.create(file_name,name,data)
def edit():
    print(Fore.YELLOW+"Warning this will override any data"+Style.RESET_ALL)
    file_name = input("File location>")
    data = input("Set data>")
    jsonreg.write(file_name,data)
def read():
    file_name = input("File location>")
    log.message("Reading: "+file_name)
    print(jsonreg.get.data(file_name))
if __name__ == "__main__":
    print(Fore.GREEN + 'Welcome to JSONreg editor'+Style.RESET_ALL)
    parser.add_argument("-ls",action='store_true')
    parser.add_argument("-rm",action='store_true')
    parser.add_argument("-mk",action='store_true')
    parser.add_argument("-r",action='store_true')
    parser.add_argument("-ed",action='store_true')
    parser.add_argument("-v",action='store_true')
    args = parser.parse_args()
    if args.v:
        verbose = True   
        print("Verbose mode activated")
    if args.ls:
        list()
    elif args.rm:
        remove()
    elif args.mk:
        create()
    elif args.r:
        read()
    elif args.ed:
        edit()   
  
    else:
        print("Next time use a argument to get started")
        print("\t-ls    List the JSONreg files in a dir")
        print("\t-rm    Remove a JSONreg file")
        print("\t-mk    Make a JSONreg file")
        print("\t-r     Read JSONreg file")
        print("\t-ed    Edit a JSONreg file")
