import pymongo
import urllib
import csv
import pickle
import os

from bson.objectid import ObjectId
import os
from sys import argv

DB_NAME = "serengeti"

def nice_seasons():
  season_chars = list(seasons_string)
  return ", ".join(season_chars)

def load_all_subjects():
  if not os.path.exists("pickles"):
    os.makedirs("pickles")
  subject_filename = "pickles/%s-subjects.p" % seasons_string
  if os.path.isfile(subject_filename):
    print "Loading subject summaries for seasons %s from file..." % nice_seasons()
    return pickle.load( open( subject_filename, "rb" ) )
  else:
    subject_summaries = []
    client = pymongo.MongoClient()
    db = client[DB_NAME]
    subject_collection = db[DB_NAME + "_subjects"]
    print "Connecting to DB and extracting subject summaries for all subjects in seasons %s...\n" % nice_seasons()
    for ii, s in enumerate(subject_collection.find({"$or": season_or_list}, no_cursor_timeout=True)):
      if ii % 1000 == 0:
        print "%s..." % ii
      zooniverse_id = s["zooniverse_id"]
      urls = s["location"]["standard"]
      site_roll_code = s["metadata"]["site_roll_code"]
      if "retire_reason" in s["metadata"].keys():
        retire_reason = s["metadata"]["retire_reason"]
      else:
        retire_reason = "N/A"
      subject_summary = {
        "zooniverse_id": zooniverse_id,
        "urls": urls,
        "site_roll_code": site_roll_code,
        "retire_reason": retire_reason
      }
      subject_summaries.append(subject_summary)
    print "Saving subject summaries to avoid querying next time..."
    pickle.dump( subject_summaries, open( subject_filename, "wb" ) )
    return subject_summaries

def create_csv(csv_directory_name, csv_filename):
  if not os.path.exists(csv_directory_name):
    os.makedirs(csv_directory_name)
  wrfile = open("%s/%s" % (csv_directory_name, csv_filename), 'w')
  writer = csv.writer(wrfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
  writer.writerow(["url","zooniverse_id","image_no","season","site-roll-code","retire-reason","crowd-says","crowd-says-if-multi"])
  return {"handle": wrfile, "writer": writer}


def add_images_to_csv_for(subject, csvwriter):
  global task_counter_so_far, downloaded_images_so_far, downloaded_subjects_so_far, skipped_images_so_far, skipped_subjects_so_far, csved_images_so_far, csved_subjects_so_far,included_subjects_so_far,included_images_so_far
  urls = subject["urls"]
  csved_this_time = False
  subject_metadata = subjects_index[subject["zooniverse_id"]]
  site_roll_code = subject["site_roll_code"]
  retire_reason = subject["retire_reason"]
  season = subject_metadata["season"]
  type = subject_metadata["type"]
  if subject_metadata["species-list"] == "N/A":
    multi="N/A"
  else:
    multi = ';'.join(subject_metadata["species-list"])
  frame_no = 0
  for this_url in urls:
    csvwriter.writerow([this_url,subject["zooniverse_id"],frame_no,season,site_roll_code,retire_reason,type,multi])
    csved_images_so_far += 1
    csved_subjects_so_far += 1
    frame_no += 1
    task_counter_so_far += 1
  if csved_this_time:
    csved_subjects_so_far += 1


def download_images_for(subject, destination_directory_name):
  global task_counter_so_far, downloaded_images_so_far, downloaded_subjects_so_far, skipped_images_so_far, skipped_subjects_so_far,included_subjects_so_far,included_images_so_far
  if not os.path.exists(destination_directory_name):
    os.makedirs(destination_directory_name)
  urls = subject["urls"]
  slash_indices = [i.rfind("/") for i in urls]
  filenames = [str(i[j + 1:]) for i, j in zip(urls, slash_indices)]
  frame_no = 0
  downloaded_this_time = False
  skipped_this_time = False
  for this_url, filename in zip(urls, filenames):
    to_get = this_url
    to_save = "%s/%s_%s.jpg" % (destination_directory_name, subject["zooniverse_id"], str(frame_no))
    if not (os.path.isfile(to_save)):
      print "[subject %s frame %s] Saving %s to %s..." % (included_subjects_so_far, frame_no, to_get, to_save)
      urllib.urlretrieve(to_get, to_save)
      downloaded_images_so_far += 1
      downloaded_this_time = True
    else:
      skipped_images_so_far += 1
      skipped_this_time = True
    frame_no += 1
    task_counter_so_far += 1
  if downloaded_this_time:
    downloaded_subjects_so_far += 1
  if skipped_this_time:
    skipped_subjects_so_far += 1


seasons = {
  1: ObjectId("50c6197ea2fc8e1110000001"),
  2: ObjectId("50c61e51a2fc8e1110000002"),
  3: ObjectId("50c62517a2fc8e1110000003"),
  4: ObjectId("50e477293ae740a45f000001"),
  5: ObjectId("51ad041f3ae7401ecc000001"),
  6: ObjectId("51f158983ae74082bb000001"),
  7: ObjectId("5331cce91bccd304b6000001"),
  8: ObjectId("54cfc76387ee0404d5000001")
}

if len(argv) < 6:
  print "Usage: python subject-extractor.py <name-for-this-set> <limit|0> <season-numbers-without-spaces> <download|csv|both> <all|blank|multi|zebra|lionmale|...>"
  os._exit(-1)
else:
  set_name = argv[1]
  limit = int(argv[2])
  seasons_string = str(argv[3])
  download_csv_string = str(argv[4])
  if download_csv_string=="download":
    download = True
    generate_csv = False
  elif download_csv_string=="csv":
    download = False
    generate_csv = True
  else:
    download = True
    generate_csv = True
  type = argv[5]
  season_or_list = []
  for season_char in list(seasons_string):
    season_or_list.append({"group_id": seasons[int(season_char)]})

# print or_list

print "\nLoading subject data from CSV..."

# load subject data from CSV
subjects_index = {}
with open('consensus-detailed.csv', 'rb') as csvfile:
  reader = csv.reader(csvfile, delimiter=',', quotechar='"')
  for row in reader:
    if row[1]:
      season = int(row[1])
    else:
      season = "N/A"
    if row[3].strip() == '':
      species_list = "N/A"
    else:
      species_list = row[3].strip().split(";")
    subjects_index[row[0]] = {"season": season, "type": row[2].strip(), "species-list": species_list}

# print "\nSample data:"
# print "ASG000b3r2",subjects_index["ASG000b3r2"]
# print "ASG00000n7",subjects_index["ASG00000n7"]
# print "ASG00000n8",subjects_index["ASG00000n8"]
# print "ASG00000n9",subjects_index["ASG00000n9"]
# print ""

task_counter_so_far = 1
downloaded_images_so_far = 0
skipped_images_so_far = 0
downloaded_subjects_so_far = 0
skipped_subjects_so_far = 0
total_subjects_so_far = 0
total_images_so_far = 0
csved_images_so_far = 0
csved_subjects_so_far = 0
included_images_so_far = 0
included_subjects_so_far = 0
filtered_out_images_so_far = 0
filtered_out_subjects_so_far = 0

if generate_csv:
  csvwriter = create_csv(set_name, "manifest.csv")

matched_so_far = 0

subject_summaries = load_all_subjects()

print "Processing subject summary metadata...\n"

for subject in subject_summaries:
  if limit > 0 and matched_so_far == limit:
    break
  this_type = subjects_index[subject["zooniverse_id"]]["type"]
  if type=="all" or this_type == type:
    matched_so_far += 1
    included_subjects_so_far += 1
    # proceed to write the row
    if download:
      downloaded_images_before = downloaded_images_so_far
      download_images_for(subject, set_name)
      newly_downloaded_images = (downloaded_images_so_far - downloaded_images_before)
      newly_csved_images = 0
      included_this_time = True
    if generate_csv:
      csved_images_before = csved_images_so_far
      add_images_to_csv_for(subject, csvwriter["writer"])
      newly_csved_images = (csved_images_so_far - csved_images_before)
      newly_downloaded_images = 0
    newly_included_images = max(newly_csved_images,newly_downloaded_images)
    included_images_so_far += newly_included_images
  else:
    # skip because it doesn't match
    task_counter_so_far += 1

if generate_csv:
  csvwriter["handle"].close()

if (downloaded_images_so_far > 0 or downloaded_subjects_so_far > 0):
  print "Downloaded %s images from %s subjects." % (downloaded_images_so_far, downloaded_subjects_so_far)
if (skipped_images_so_far > 0 or skipped_subjects_so_far > 0):
  print "Skipped %s images (already downloaded) from at least %s subjects." % (
  skipped_images_so_far, skipped_subjects_so_far)
if (csved_images_so_far > 0 or csved_subjects_so_far > 0):
  print "Wrote CSV rows for %s images from %s subjects." % (csved_images_so_far, csved_subjects_so_far)
total_downloaded_images_so_far = downloaded_images_so_far + skipped_images_so_far
total_downloaded_subjects_so_far = downloaded_subjects_so_far + skipped_subjects_so_far
print "\nTotal images present on disk = %s, from %s subjects.\n" % (
total_downloaded_images_so_far, total_downloaded_subjects_so_far)
if (csved_images_so_far > 0 or csved_subjects_so_far > 0):
  print "Total images present in CSV = %s, from %s subjects.\n" % (csved_images_so_far, csved_subjects_so_far)

print "Total images that matched type = %s, from %s subjects.\n" % (included_images_so_far, included_subjects_so_far)
