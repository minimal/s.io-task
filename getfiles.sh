#! /bin/bash
wget -qO- http://s3.amazonaws.com/alexa-static/top-1m.csv.zip | funzip -p  | head -100000 | awk -F "," '{ print "http://" $2 }' > top100k
wget -qO bugs.json http://www.ghostery.com/update/all?format=json
