#!/usr/bin/python
# 2017-07-02 svc -- edit_initramfs.py
#
# override contents of cpio.gz files by concatenating
# new cpio blocks onto end of input cpio.gz after
# decompressing and truncating to remove the trailer block.
#
# this allows one to modify existing initrd images to speed
# up initrd hack development.  otherwise, it'd be necessary
# to first extract the initrd tree, modify the contents, then
# repack into a new cpio.gz.
#
# FIXME: use better variable names.
# FIXME: support command-line arguments.
# TODO: don't hard-code path, get from sys.argv.
# TODO: don't hard-code file list, get from command-line or,
#       xargs-like, stdin.
import gzip
import subprocess
import sys
import cStringIO

newc_header_len = 110
cpiogz_path = "initrd.img-3.16.0-4-amd64"
overwrite_file_list = ["init"]
data = gzip.open(cpiogz_path).read()
# find and chop off the cpio trailer block.
tail = data[-1024:]
trailer_index = tail.rindex("TRAILER")
data = data[:-1024] + tail[:trailer_index - newc_header_len]
# create the new cpio data to append to the old.
ph = subprocess.Popen("cpio -H newc -o".split(),
                      stdin = subprocess.PIPE,
                      stdout = subprocess.PIPE)
x = ph.communicate("\n".join(overwrite_file_list))
# FIXME: can the data be lost because ph is destroyed before
#        x[0] is accessed?
ph = subprocess.Popen(["gzip", "-c"],
                      stdin = subprocess.PIPE,
                      stdout = subprocess.PIPE)
y = ph.communicate(data + x[0])
sys.stdout.write(y[0])
