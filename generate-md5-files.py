import os
import subprocess
import sys
import argparse
import hashlib
from query_yes_no import query_yes_no


parser = argparse.ArgumentParser(description='genreate md5 files')
parser.add_argument(dest='path', help='root folder or filename')
parser.add_argument('--verify', dest="verify", action='store_true', default=False, help="verify only, not modify anything")
parser.add_argument('-R', dest="recursive", action='store_true', default=False)
parser.add_argument('-f', dest="force", action='store_true', default=False, help="overwrite md5 files if exists")
parser.add_argument('-q', dest='quite_mode',action='store_true', default=False)
parser.add_argument('--md5', dest='md5_switch',action='store_true', default=True)
parser.add_argument('--csv', dest='csv_switch',action='store_true', default=False)


args = parser.parse_args()

def md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def generate_md5_file(file_path, md5_file_path):
    hash = md5(file_path)
    with open(md5_file_path, 'w', encoding='ansi') as fpw:
        fpw.write(hash)
        
def verify_md5_file(file_path, md5_file_path):
    hash = md5(file_path)
    with open(md5_file_path, 'r', encoding='ansi') as fp:
        saved_hash = fp.read()
        return hash == saved_hash, saved_hash, hash
    
def handle_hash_mismatching(file_path, md5_file_path, old_hash, new_hash):
    print('{} has different md5 hash, it was {}, now it is {}'.format(file_path, old_hash, new_hash))
    if not args.verify:
        update = args.quite_mode
        if not args.quite_mode:
            update = query_yes_no('update md5 hash?')
        if update:
            with open(md5_file_path, 'w', encoding='ansi') as fpw:
                fpw.write(new_hash)
            

def do_file(file_path):
    if not os.path.isfile(file_path):
        raise os.error("no file at" + file_path)
    
    md5_file_path = file_path+".md5"
    if os.path.isfile(md5_file_path):
        equal, old_hash, new_hash = verify_md5_file(file_path, md5_file_path)
        if not equal:
            handle_hash_mismatching(file_path, md5_file_path, old_hash, new_hash)
    else:
        generate_md5_file(file_path, md5_file_path)
                
        
def do_folder(path):
    print(path, end='\n', flush=True)
    file_names = os.listdir(path)
    for file_name in file_names:
        _, ext = os.path.splitext(file_name)
        if os.path.isfile(file_name) and ext != '.md5':
            do_file(os.path.abspath(file_name))
        elif os.path.isdir(file_name) and args.recursive:
            do_folder(os.path.abspath(file_name))
    

if os.path.isfile(args.path):
    do_file(args.path)
    print()
else:
    do_folder(os.path.abspath(args.path))
    print()

# csv_file = args.csv_file

# with open(csv_file, 'r', encoding='utf8') as fp:
#     csv_reader = csv.reader(fp)
#     for row in csv_reader:
#         if row[2] == "False":
#             print(row[0], row[1])
#             subprocess.run(['C:/Users/luoyi/Desktop/Beyond Compare 4/BCompare.exe', row[0], row[1]])