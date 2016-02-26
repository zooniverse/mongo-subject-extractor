require 'bson'

def string_compress_behavior_counters_values(behavior_counters_data)
  behavior_counters_vals = ""
  behavior_counters_data.values().each do |behaviors_for_this_species|
    subvals = ""
    behaviors_for_this_species.each do |k,v|
      if subvals != ""
        subvals += "!"
      end
      subvals += "#{k}:#{v}"
    end
    if behavior_counters_vals != ""
      behavior_counters_vals += ";"
    end
    behavior_counters_vals += subvals
  end
  return behavior_counters_vals
end

def get_average_time_of_day(timestamps_data)
  timestamps = timestamps_data.collect{ |t| Time.parse(t.sub(/-05:00$/, ' UTC')).to_i }
  timestamp = Time.at(timestamps.inject(:+) / timestamps.length.to_f).utc
  timestamp < Time.parse('2000-01-01') ? nil : timestamp.strftime("%H:%M")
rescue
  nil
end

def string_compress_species_counts_values(species_counts_data)
  species_counts_vals = ""
  for sub in species_counts_data.values()
    substr = sub.join("|")
    if species_counts_vals != ""
      species_counts_vals += ";"
    end
    species_counts_vals += substr
  end
  return species_counts_vals
end

File.open('consensus-detailed.csv', 'w') do |out|
  # Selecting retire_reason => consensus will find only completed, consensus subjects
  total = SerengetiSubject.collection.find({}).count
  index = 0
  seasons = {
  1 => BSON::ObjectId("50c6197ea2fc8e1110000001"),
  2 => BSON::ObjectId("50c61e51a2fc8e1110000002"),
  3 => BSON::ObjectId("50c62517a2fc8e1110000003"),
  4 => BSON::ObjectId("50e477293ae740a45f000001"),
  5 => BSON::ObjectId("51ad041f3ae7401ecc000001"),
  6 => BSON::ObjectId("51f158983ae74082bb000001"),
  7 => BSON::ObjectId("5331cce91bccd304b6000001"),
  8 => BSON::ObjectId("54cfc76387ee0404d5000001"),
  0 => BSON::ObjectId("55a3d6cf3ae74036bc000001"), # actually Lost Season
  9 => BSON::ObjectId("56a63b3b41479b0042000001")
  }

  # write titles
  out.puts "zooniverse_id,season,site_id,roll_id,number_of_frames,frame1_url,frame2_url,frame3_url,time_of_day,classifications,crowd_says,total_species,total_animals,crowd_says_if_multi,retire_reason,counters_keys,counters_values,species_counts_keys,species_counts_values,behavior_counters_keys,behavior_counters_values,aggregate_species_names,aggregate_species_counts"

  SerengetiSubject.collection.find({}, { timeout: false }) do |cursor|
    while cursor.has_next?
      puts "#{ index += 1 } / #{ total }"
      subject = SerengetiSubject.new cursor.next_document

      # calculate field values for CSV
      if subject.likely_classification.keys.length == 0
        blank = true
        multi = false
      elsif subject.likely_classification.keys.length == 1
        multi = false
        blank = false
      else
        multi = true
        blank = false
      end
      zooniverse_id = subject.zooniverse_id
      season = seasons.invert[subject.attributes['group_id']]

      site_and_roll = subject.metadata['site_roll_code'].split('_',2).last().split('_')
      site_id = site_and_roll.first()
      roll_id = site_and_roll.last()

      if subject.metadata.has_key?("old_timestamps")
        no_of_frames = subject.metadata["old_timestamps"].length
        time_of_day = get_average_time_of_day(subject.metadata['old_timestamps'])
      else
        no_of_frames = 1
        time_of_day = nil
      end
      frame1_url = frame2_url = frame3_url = nil
      if no_of_frames>2
        frame3_url = subject.location['standard'][2]
      end
      if no_of_frames>1
        frame2_url = subject.location['standard'][1]
      end
      frame1_url = subject.location['standard'][0]
      classification_count = subject.classification_count
      if multi
        determination = "multi"
        determination_list_if_multi = subject.likely_classification.keys.join(';')
      elsif blank
        determination = "blank"
        determination_list_if_multi = "blank"
      else
        determination = subject.likely_classification.keys[0]
        determination_list_if_multi = subject.likely_classification.keys[0]
      end
      total_animals_present = subject.likely_species_counts.values.inject{|sum,x| sum + x }
      if total_animals_present.nil?
        total_animals_present = 0
      end
      total_species_present = subject.likely_species_counts.keys.length
      if total_species_present.nil?
        total_species_present = 0
      end
      if subject.metadata.has_key?("retire_reason")
        retire_reason = subject.metadata["retire_reason"]
      else
        retire_reason = "N/A"
      end
      if subject.metadata.has_key?("counters")
        counters_keys = subject.metadata["counters"].keys().join(";")
        counters_values = subject.metadata["counters"].values().join(";")
      else
        counters_keys = ""
        counters_values = ""
      end
      if subject.metadata.has_key?("species_counts")
        species_counts_keys = subject.metadata["species_counts"].keys().join(";")
        species_counts_values = string_compress_species_counts_values(subject.metadata["species_counts"])
      else
        species_counts_keys = ""
        species_counts_values = ""
      end
      if subject.metadata.has_key?("behavior_counters")
        behavior_counters_keys = subject.metadata["behavior_counters"].keys().join(";")
        behavior_counters_values = string_compress_behavior_counters_values(subject.metadata["behavior_counters"])
      else
        behavior_counters_keys = ""
        behavior_counters_values = ""
      end
      if blank
        aggregate_species_names = "blank"
        aggregate_species_counts = "N/A"
      else
        aggregate_species_names = subject.likely_species_counts.keys().join(";")
        aggregate_species_counts = subject.likely_species_counts.values().join(";")
      end

      # write to CSV

      # This will make the line look like
      # <zoo ID>, <season>, <site ID>, <roll ID>, <number of frames>, <frame 1 URL>, <frame 2 URL>, <frame 3 URL>, <time of day>, <number of classifications>,
      #    <determination: blank|multi|zebra|lionmale|etc..>, <total species>, <total animals>, <species list if multi>,
      #    <retire reason|N/A>, <counters keys>, <counters values>, <species counts keys>, <species counts values>,
      #    <behavior counters keys>, <behaviour counters values>, <list of which species present>, <counts per species>

      out.puts "#{zooniverse_id},#{season},#{site_id},#{roll_id},#{no_of_frames},#{frame1_url},#{frame2_url},#{frame3_url},#{time_of_day},#{classification_count},#{determination},#{total_species_present},#{total_animals_present},#{determination_list_if_multi},#{retire_reason},#{counters_keys},#{counters_values},#{species_counts_keys},#{species_counts_values},#{behavior_counters_keys},#{behavior_counters_values},#{aggregate_species_names},#{aggregate_species_counts}"

    end
  end
end