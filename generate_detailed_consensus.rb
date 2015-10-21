require 'bson'

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
  8 => BSON::ObjectId("54cfc76387ee0404d5000001")
  }
  SerengetiSubject.collection.find({}, { timeout: false }) do |cursor|
    while cursor.has_next?
      puts "#{ index += 1 } / #{ total }"
      subject = SerengetiSubject.new cursor.next_document
      season = seasons.invert[subject.attributes['group_id']]
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
      # This will make the line look like
      # ASV121321,<season>,specific_species|blank|multi,<species_list_if_multi>
      if multi
        out.puts "#{ subject.zooniverse_id },#{ season }, multi, #{ subject.likely_classification.keys.join(';') }"
      elsif blank
        out.puts "#{ subject.zooniverse_id },#{ season }, blank, "
      else
        out.puts "#{ subject.zooniverse_id },#{ season }, #{ subject.likely_classification.keys[0] },"
      end
    end
  end
end