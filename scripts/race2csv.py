#!/usr/bin/env python

from subprocess import Popen, PIPE
import json
import shlex
from itertools import *
from operator import *
import csv
import sys
import yaml

spec = open('csv_spec.yml')
csv_columns = yaml.load(spec.read())['race']
spec.close()

filename = (len(sys.argv) == 2 and sys.argv[1]) or "BYAW0P3YPS31LXW035Y7"
curl = """/usr/bin/curl 'https://hwo2014-racedata-prod.s3.amazonaws.com/test-races/%s.json' -H 'Pragma: no-cache' -H 'Origin: https://helloworldopen.com' -H 'Accept-Encoding: gzip,deflate,sdch' -H 'Accept-Language: en-US,en;q=0.8,pl;q=0.6' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.27 Safari/537.36' -H 'Accept: */*' -H 'Cache-Control: no-cache' -H 'Referer: https://helloworldopen.com/race-visualizer/recording=https://hwo2014-racedata-prod.s3.amazonaws.com/test-races/BYAW0P3YPS31LXW035Y7.json&version=1' -H 'Connection: keep-alive' -H 'DNT: 1' --compressed"""%filename
p = Popen(shlex.split(curl), stdin=None, stdout=PIPE, stderr=None)
data = p.stdout.read()
data = json.loads(data)
#TODO: handle crash/respawn
pos_vel = filter(lambda x: x.has_key('gameTick') and x['msgType'] in (u'carVelocities', u'fullCarPositions'), data)

def make_row(g):
  row = {}
  row['map_id'] = filename
  for v in g:
    if v['msgType'] == 'carVelocities':
      row['velocity_x'] = v['data'][0]['x']
      row['velocity_y'] = v['data'][0]['y']
    elif v['msgType'] == 'fullCarPositions':
      row['tick'] = v['gameTick']
      v = v['data'][0]
      row['car'] = "%s_%s"%(v['id']['name'], v['id']['color'])
      row['coord_x'] = v['coordinates']['x']
      row['coord_y'] = v['coordinates']['y']
      row['angle'] = v['angle']
      row['angle_offset'] = v['angleOffset']
      piece = v['piecePosition']
      row['piece_id'] = piece['pieceIndex']
      row['piece_pos'] = piece['inPieceDistance']
      row['lane_start'] = piece['lane']['startLaneIndex']
      row['lane_end'] = piece['lane']['endLaneIndex']
      row['lap'] = piece['lap']

  return row

rows = [make_row(x) for _, x in groupby(pos_vel, itemgetter('gameTick'))] #TODO: handle multiple cars
with open("%s_race.csv"%filename, 'wb') as csvfile:
  writer = csv.DictWriter(csvfile, csv_columns)
  writer.writeheader()
  writer.writerows(rows)


