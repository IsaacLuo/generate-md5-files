import os
import sys
import argparse
import hashlib
from query_yes_no import query_yes_no
from sqlitedict import SqliteDict
import subprocess

parser = argparse.ArgumentParser(description='genreate md5 files')
parser.add_argument(dest='path', help='root folder or filename')
parser.add_argument('--verify', dest="verify", action='store_true', default=False, help="verify only, not modify anything")
parser.add_argument('-R', dest="recursive", action='store_true', default=False)
parser.add_argument('-f', dest="force", action='store_true', default=False, help="overwrite md5 files if exists")
parser.add_argument('-q', dest='quite_mode',action='store_true', default=False)
parser.add_argument('--md5', dest='md5_switch',action='store_true', default=False)
# parser.add_argument('--csv', dest='csv_switch',action='store_true', default=False)
parser.add_argument('--db', dest='db_switch',action='store_true', default=False)
parser.add_argument('--clear-md5', dest='clear_md5',action='store_true', default=False)


args = parser.parse_args()
    
def md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def save_hash(hash, file_path, md5_file_path):
    if args.md5_switch:
        with open(md5_file_path, 'w', encoding='ansi') as fpw:
            fpw.write(hash)
    if args.db_switch:
        db[file_path] = hash

def generate_md5_file(file_path, md5_file_path):
    hash = md5(file_path)
    save_hash(hash, file_path, md5_file_path)
        
def verify_md5_file(file_path, md5_file_path):
    hash = md5(file_path)
    with open(md5_file_path, 'r', encoding='ansi') as fp:
        saved_hash = fp.read()
    return hash == saved_hash, saved_hash, hash
    
def verify_md5_db(file_path):
    saved_hash = db[file_path]
    hash = md5(file_path)
    return hash == saved_hash, saved_hash, hash
    
    
def handle_hash_mismatching(file_path, md5_file_path, old_hash, new_hash):
    print('{} has different md5 hash, it was {}, now it is {}'.format(file_path, old_hash, new_hash))
    if not args.verify:
        update = args.quite_mode
        if not args.quite_mode:
            update = query_yes_no('update md5 hash?')
        if update:
            save_hash(new_hash, file_path, md5_file_path)

def do_file(file_path):
    if not os.path.isfile(file_path):
        raise os.error("no file at" + file_path)
    
    md5_file_path = file_path+".md5"
    if os.path.isfile(md5_file_path):
        equal, old_hash, new_hash = verify_md5_file(file_path, md5_file_path)
        if not equal:
            handle_hash_mismatching(file_path, md5_file_path, old_hash, new_hash)
    elif args.db_switch and file_path in db:
        equal, old_hash, new_hash = verify_md5_db(file_path)
        if not equal:
            handle_hash_mismatching(file_path, md5_file_path, old_hash, new_hash)
    else:
        generate_md5_file(file_path, md5_file_path)
                
        
def do_folder(path):
    main_name, _ = os.path.splitext(os.path.basename(path))
    # ignore special folders
    if main_name == '' or main_name[0] == '.' or main_name[0] == '_':
        return
    print(path, end='\n', flush=True)
    if path == os.getcwd():
        return
    try:
        file_names = os.listdir(path)
    except:
        return
    for file_name in file_names:
        file_path = os.path.join(path, file_name)
        _, ext = os.path.splitext(file_path)
        if ext == ".md5" and args.clear_md5 and not args.md5_switch:
            os.remove(file_path)
        if os.path.isfile(file_path) and ext != '.md5':
            do_file(file_path)
        elif os.path.isdir(file_path) and args.recursive:
            do_folder(file_path)
    if args.db_switch:
        db.commit()
    

if os.path.isfile(args.path):
    do_file(args.path)
    print()
else:
    if args.db_switch:
        md5_folder = os.path.abspath(os.path.join(args.path, '.md5'))
        if not os.path.isdir(md5_folder):
            os.makedirs(md5_folder)
        db = SqliteDict(os.path.join(md5_folder, 'md5.sqlite'))
    do_folder(os.path.abspath(args.path))
    
    if args.db_switch:
        db.close()
        print()
