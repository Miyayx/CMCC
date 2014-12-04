#mongoexport --db mobile --collection doc_parse --out /home/alex/projects/mobile/src/Classify/mobile.json
scp 30:/home/alex/projects/mobile/src/Classify/mobile.json /mnt/wind/EclipseWorkspace/Classify/
sudo service mongod start
mongoimport --db mobile --collection test --file /mnt/wind/EclipseWorkspace/Classify/mobile.json


