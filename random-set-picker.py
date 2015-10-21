from os import listdir
from random import choice
import sys
from shutil import copy
import os, errno

seen = []

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def random_file():
  """returns the filename of a randomly chosen subject image in dir, and then ensures that image cannot be picked again"""
  image = choice(choice_set)
  choice_set.remove(image)
  return image

def get_set(n):
  """returns a set of N unique images randomly chosen from the directory"""
  files = []
  for _ in range(n):
    files.append(random_file())
  return files

if len(sys.argv) == 4:
  n = int(sys.argv[1])
  input_directory = sys.argv[2]
  output_directory = sys.argv[3]
  choice_set = [f for f in listdir(input_directory)]
  the_set = get_set(n)
  mkdir_p(output_directory)
  i=0
  for s in the_set:
    i += 1
    full_in = input_directory + "/" + s
    full_out = output_directory + "/" + s
    copy(full_in, output_directory)
    print "[%s/%s] Copying %s to %s..." % (i,n,full_in,full_out)
  print "\nDone.\n"
else:
  print "\nUsage:\n"
  print "python random-set-picker <number of files in set> <source directory> <destination directory>\n"



