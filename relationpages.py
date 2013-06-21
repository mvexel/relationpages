#!/usr/bin/python

import csv
import re 
from collections import defaultdict
from os import path
import string 
from datetime import datetime
import states

basepath = "/home/ubuntu/www/relationpages"
statsfile = "/mnt/mr_data/usrouterelations.csv"
keys = ['id','version','user_id', 'tstamp','changeset_id','name','ref','network']
interstates = []
usroutes = []
stateroutes = defaultdict(list)
substateroutes = defaultdict(list)
weirdroutes = []
valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

def load_routes(statsfile):
    try:
        with open(statsfile, 'rb') as statscsv:
            reader = csv.DictReader(statscsv, keys, delimiter=',')
            for row in reader:
                network = row['network'].split(':')
                if not network[0] == 'US':
                    continue # this is not a valid US numbered route
                if network[1] == 'I': # it is an interstate
                    interstates.append(row)
                elif network[1] == 'US': # it is a US route
                    usroutes.append(row)
                elif re.match('^[A-Z]{2}$', network[1]): # it is a state or substate route
                    if len(network) == 2: # it is a state route
                        stateroutes[network[1]].append(row)
                    else:
                        substateroutes[network[1]].append(row)
                else:
                    weirdroutes.append(row)
    except IOError:
        print "something not right with %s, check into that will you?" % (statsfile,)

def generate_relationrow(relation):
    code = '<tr>'
    # name ref id check manage josm history view gpx
    code += '''<td>%s</td>
        <td>%s</td>
        <td><a target="_new" href='http://www.openstreetmap.org/browse/relation/%s'>%s</a></td>
        <td><a target="_new" href='http://ra.osmsurround.org/analyze.jsp?relationId=%s'>check</a></td>
        <td><a target="_new" href='http://osm.cdauth.eu/route-manager/relation.jsp?id=%s'>manage</a></td>
        <td><a target="_new" href='http://localhost:8111/import?url=http://api.openstreetmap.org/api/0.6/relation/%s/full'>josm</a></td>
        <td><a target="_new" href='http://osm.virtuelle-loipe.de/history/?type=relation&ref=%s'>history</a></td>
        <td><a target="_new" href='http://openstreetmap.org/?relation=%s'>view</a></td>
        <td><a target="_new" href='http://osmrm.openstreetmap.de/gpx.jsp?relation=%s'>gpx</a></td>
        ''' % ( relation['name'], 
                relation['ref'],
                relation['id'], 
                relation['id'], 
                relation['id'],
                relation['id'],
                relation['id'],
                relation['id'],
                relation['id'],
                relation['id'],
            )
    code += '</tr>'
    return code

def generate_header(title, caption):
    return '''<!DOCTYPE html><html lang="en"><head>
    <meta charset="utf-8">
    <title>relations viewer - %s</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" type="text/css" href="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css">
    <script type="text/javascript" charset="utf8" src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js"></script>
    <script type="text/javascript" charset="utf8" src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js"></script>    
    <script id="js">$(document).ready(function() {
        var dt = $('#relationsTable').dataTable({
            "aaSorting": [[ 1, "asc" ]],
            //"bJQueryUI": true,
            "bPaginate": false,
            "sPaginationType": "full_numbers",
            "iDisplayLength": 50,
            "aoColumnDefs": [
                {"bSearchable": false, "aTargets": [2,3,4,5,6,7,8]},
                {"bSortable": false, "aTargets": [3,4,5,6,7,8]}
            ],
            "oSearch": {"bSmart": false}
        });
        dt.fnFilter("^" + filter_value + "$");
        var settings = dt.fnSettings();
        settings.aoPreSearchCols[1].bRegex = false;
    })</script>
    </head><body><h1>%s</h1><p><em>%s</em></p><div id='title'><img src="images/relationinfo_150.png"><div id='ttext'>OSM US<br />relation pages</div></div>''' % (title, title, caption,)

def generate_footer():
    return '<br /><hr><small>generated at %s - gets refreshed every 4 hours based on latest OSM data - <a href="https://github.com/mvexel/relationpages">this on github</a> - thanks jquery and <a href="http://www.datatables.net/index">datatables</a></small></body></html>' % (str(datetime.now()),)

def generate_page(relations, title, caption):
    filename = path.join(basepath, ''.join(c for c in title if c in valid_chars).lower() + '.html')
    html = generate_header(title, caption)
    html += generate_relationtable(relations)
    html += generate_footer()
    with open(filename, 'w') as htmlout:
        htmlout.write(html)
    print '%s written to %s.' % (title, filename)

def generate_relationtable(relations):
    code = '<table id="relationsTable"><thead><tr>'
    for key in ('Name','Ref','ID','check','manage','josm','history','view','gpx'):
        code += '<th>%s</th>' % (key,)
    code += '</tr></thead><tbody>'
    for relation in relations:
        code += generate_relationrow(relation)
    code += '</tbody></table>'
    return code

if __name__ == "__main__":
    load_routes(statsfile)
    print "%i interstates, %i US routes, %i state routes consumed" % (len(interstates), len(usroutes), len(stateroutes))
    print "%i weird" % (len(weirdroutes))
    print stateroutes.keys()
    print "substateroutes:"
    for key in sorted(substateroutes.keys()):
        print "%s : %i" % (key, len(substateroutes[key]))
    generate_page(interstates, "Interstates", "The U.S. Interstate route relations")
    generate_page(usroutes, "U.S. Routes", "The U.S. Route relations")
    for abbrev, relations in stateroutes.iteritems():
        print 'processing %s' % (abbrev,)
        statename = abbrev
        if abbrev in states.states:
            statename = states.states[abbrev]
        generate_page(relations, 
                "%s State Routes" % (statename), 
                "%s State Route relations" % (statename)
        )
