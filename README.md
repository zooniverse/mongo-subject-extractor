# mongo-subject-extractor
Scripts for extracting subjects and images from the mongoDB. Written for Serengeti, could be adapted for other projects.

## What is this?
Let's say you want to have a specific group of images to upload to a Panoptes builder project - or to test in some image analysis tool such as the MICO platform.
This script will let you specify certain parameters and find matching subjects, then automatically download those images and/or generate a CSV manifest file containing the URLs.

The initial implementation is Snapshot Serengeti-specific, but it is my intent that this tool can be extended to support other Ouroboros/MongoDB Zooniverse projects in future.

# Installation instructions

1. Install [python](https://www.python.org/downloads/)
2. Ensure that the python modules `pymongo`, `csv`, `urllib` and `bson` are installed:
   ```
   pip install pymongo
   pip install urllib
   pip install csv
   pip install bson
   ```
3. Install [mongodb](https://docs.mongodb.org/manual/installation/)
4. Download a MongoDB dump from S3 or elsewhere, unzip it, and use mongorestore to copy it into your local Mongo database server:
   ```
   cd /downloads
   mongorestore --db serengeti --drop serengeti_2015-10-21
   ```
5. Clone this repository and `cd` into it:
   ```
   cd /code
   git clone https://github.com/zooniverse/mongo-subject-extractor.git
   cd mongo-subject-extractor
   ```
6. Generate the subject metadata CSV file. You don't need to do this if you already have `consensus-detailed.csv` and it's up-to-date.

   This creates a CSV summarising the contents of each subject, based on aggregate user classifications, into three types: 
     - `blank` for blank images
     - `multi` for images containing more than one distinct species (only 6% of non-blank subjects have more than one species)
     - `<species-name>` where a distinct species is present. (e.g. `zebra`, `gazellegrants`, `lionmale` etc.)
   
   This is done as follows:
     1. Install and build the Ouroboros project (which includes installing Ruby) per the instructions at [https://github.com/zooniverse/Ouroboros](https://github.com/zooniverse/Ouroboros)
     2. Run the rails console in that directory by typing `rails c`
     3. From the rails console, load the script `load /code/mongo-subject-extractor/generate_detailed_consensus.rb`
     4. Copy the generated CSV file from the Ouroboros directory into /code/mongo-subject-extractor
   
7. You are now ready to run the `subject-extractor.py` script using the instructions above.
