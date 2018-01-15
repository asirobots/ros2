import os
import shutil
import tarfile
from os.path import dirname as parent
from os.path import basename
import glob
import subprocess


cwd = os.getcwd()


def compile_message(idl_files, dest_dir, coredxdir, language):
    global cwd
    possible_coredx_ddls = glob.glob(coredxdir + "/host/bin/*coredx_ddl*")
    if len(possible_coredx_ddls) != 1:
        raise RuntimeError("Didn't find one coredx_ddl executable possibility, found", possible_coredx_ddls)
    if os.name == "posix":
        source_command = "source " + cwd + "/install/local_setup.bash"
        commands = source_command
        for idl_file in idl_files:
            this_dest_dir = dest_dir + '/' + basename(parent(parent(parent(idl_file)))) + '/' + basename(parent(parent(idl_file))) + '/' + basename(parent(idl_file))
            if not os.path.isdir(this_dest_dir):
                os.makedirs(this_dest_dir)
            commands += " && " + possible_coredx_ddls[0] + " -I " + cwd + "/install/share -d " + this_dest_dir + " -s -l " + language + " -f " + idl_file
        subprocess.run(commands, shell=True, executable='/bin/bash', check=True)
    else:
        commands = list()
        source_command = cwd + "/install/local_setup.bat"
        for idl_file in idl_files:
            this_dest_dir = dest_dir + '/' + basename(parent(parent(parent(idl_file)))) + '/' + basename(parent(parent(idl_file))) + '/' + basename(parent(idl_file))
            if not os.path.isdir(this_dest_dir):
                os.makedirs(this_dest_dir)
            commands.append(possible_coredx_ddls[0] + " -I " + cwd + "/install/share -d " + this_dest_dir + " -s -l " + language + " -f " + idl_file)
        num = 15
        for i in range(0, len(commands), num):
            my_commands = source_command
            i2 = i+num if i+num < len(commands) else len(commands)
            print(i, "to", i2, "of", len(commands))
            for c in commands[i : i2]:
                my_commands += " && " + c
            subprocess.run(my_commands, shell=True, check=True)

build_path = cwd + '/build'
cpp_messages_path = build_path + '/cpp_messages'
csharp_messages_path = build_path + '/csharp_messages'
possible_coredxdirs = glob.glob(cwd + "/install/coredx-*")
if len(possible_coredxdirs) != 1:
    raise RuntimeError("Didn't find one coredxdir possibility, found", possible_coredxdirs)
else:
    coredxdir = possible_coredxdirs[0]

if os.path.isdir(cpp_messages_path):
    shutil.rmtree(cpp_messages_path)
if os.path.isdir(csharp_messages_path):
    shutil.rmtree(csharp_messages_path)

idl_files = [i for i in glob.iglob(build_path + '/**/*.idl', recursive=True)]

compile_message(idl_files, cpp_messages_path, coredxdir, "cpp")
compile_message(idl_files, csharp_messages_path, coredxdir, "csharp")

with tarfile.open(parent(parent(cpp_messages_path)) + "/cpp_messages.tar.gz", "w:gz") as tar:
    for dir in os.listdir(cpp_messages_path):
        tar.add(cpp_messages_path + '/' + dir, arcname=dir)
with tarfile.open(parent(parent(csharp_messages_path)) + "/csharp_messages.tar.gz", "w:gz") as tar:
    for dir in os.listdir(csharp_messages_path):
        tar.add(csharp_messages_path + '/' + dir, arcname=dir)
