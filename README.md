relationpages
=============

generates pages with relation info / links for U.S.  numbered route relations.

##demo

[here](http://maproulette.org/relationpages/interstates.html)

##set it up

###have this

You need two servers: 

1. a postgresql database server containing an osmosis snapshot schema database with replication.
2. a web server running python 2.7 and apache (it just needs to serve static pages, so you could use any lightweight server, but the example config file is for apache.)

these can very well be on the same machine. i am going to assume ubuntu linux for the os.

###do this 

* edit the sql script `sql/relationsquery.sql` so that the output file `usrouterelations.csv` is stored in a place where whoever you will be running the python script as can get to it.
* set up a cron job to run the query in `sql/relationsquery.sql` every few hours or so.
* (if your database is on a separate server, set up another cron job to copy the resulting csv file to the server that will host the pages.)
* create a directory to hold the static pages. let's assume this directory is `/home/osm/www` (adapt below as needed if you pick something different)
* copy or symlink the directories living in `sitestuff` (that would be `css` and `images`) to `/home/osm/www`.
* edit the apache config file `relationpages.conf` to point to `/home/osm/www`.
* edit the `basedir` variable in `relationpages.py` so it says `/home/osm/www`.
* edit the `statsfile` variable in `relationpages.py` so it points to where your output csv from the sql query is saved.
* symlink the apache config file in `/etc/apache2/conf.d` and restart apache with `service apache2 restart`
* test the page generation script by running the sql once (`psql -U dbuser -d dbname -f sql/relationsquery.sql`) and then the generation script (`python relationpages.py`)
* go to `http://yourserver/relationpages` and you should see a long list of relation pages.

this is [wtfpl](http://www.wtfpl.net), [datatables](http://www.datatables.net/) is dual licensed under the GPL v2 license or a BSD (3-point) license.
