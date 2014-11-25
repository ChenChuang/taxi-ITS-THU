# ---- install ubuntu 12.04 ----

# install ssh
sudo apt-get install openssh-client, openssh-server
/etc/init.d/ssh start

# install python
sudo apt-get install python-dev

# install scipy, numpy
sudo apt-get install scipy numpy

# install postgresql
sudo apt-get install libpq-dev

cd Downloads

wget http://initd.org/psycopg/tarballs/PSYCOPG-2-5/psycopg2-2.5.4.tar.gz
tar xfz psycopg2-2.5.4.tar.gz
cd psycopg2-2.5.4
python setup.py build
sudo python setup.py install
cd ..

# install setuptools
wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python

# install networkx
wget https://pypi.python.org/packages/source/n/networkx/networkx-1.9.1.tar.gz
tar xfz networkx-1.9.1.tar.gz
cd networkx-1.9.1
python setup.py build
sudo python setup.py install
cd ..

# install g++
sudo apt-get install g++

# install spatialindex
wget http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz
tar xfz spatialindex-src-1.8.5.tar.gz
cd spatialindex-src-1.8.5
./configure
make
sudo make install
sudo ldconfig
cd ..

# install rtree
wget https://pypi.python.org/packages/source/R/Rtree/Rtree-0.8.2.tar.gz
tar xfz Rtree-0.8.2.tar.gz
cd Rtree-0.8.2
sudo python setup.py install
cd ..

cd ..

# ---- END of install ubuntu 12.04 ----



# ---- install database ----

# install postgresql
# http://www.postgresql.org/download/linux/ubuntu/
sudo vim /etc/apt/sources.list.d/pgdg.list
add "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main"
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3 libpq-dev postgresql-server-dev-9.3
sudo apt-get install libxml2-dev libproj-dev libjson0-dev xsltproc docbook-xsl docbook-mathml libgdal1-dev
sudo su postgres
vim /etc/postgresql/9.3/main/pg_hba.conf
modify "local all postgres peer" to "local all postgres trust"
exit
psql -U postgres
# move psql database to home
sudo /etc/init.d/postgresql stop
cd ~/Workspace
mkdir psql_db
chown -R postgres:postgres psql_db
sudo su postgres
cp -aRv /var/lib/postgresql/9.3/main psql_db
cd /var/lib/postgresql/9.3/
mv main main_backup
exit
sudo vim /etc/postgresql/9.3/main/postgres.conf
modify "data_directory = '/var/lib/postgresql/9.3/main'" to "data_directory = '/home/chenchuang/Workspace/psql_db/main'"
sudo /etc/init.d/postgresql start
sudo su postgres
cd /var/lib/postgresql/9.3/
rm main_backup
exit
# Build GEOS 3.3.x
wget http://download.osgeo.org/geos/geos-3.3.9.tar.bz2
tar xfj geos-3.3.9.tar.bz2
cd geos-3.3.9
./configure
make
sudo make install
cd ..
# install GDAL
cd gdal-1.10.0
./configure
make
sudo make install
# Build PostGIS
# http://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS21Ubuntu1204src 
# more info: http://trac.osgeo.org/postgis/ and http://postgis.net/ 

wget http://download.osgeo.org/postgis/source/postgis-2.1.4.tar.gz
tar xfz postgis-2.1.4.tar.gz
cd postgis-2.1.4
./configure
make
sudo make install
sudo ldconfig
sudo make comments-install
sudo ln -sf /usr/share/postgresql-common/pg_wrapper /usr/local/bin/shp2pgsql
sudo ln -sf /usr/share/postgresql-common/pg_wrapper /usr/local/bin/pgsql2shp
sudo ln -sf /usr/share/postgresql-common/pg_wrapper /usr/local/bin/raster2pgsql

# ---- END of install postgis ----




# ---- download OpenStreetMap ----

download from http://download.geofabrik.de/asia/china.html
# export beijing .osm file from .osm.pbf file
echo 'beijing_v
1
    115.711    40.317
    117.054    40.317
    117.054    39.519
    115.711    39.519
END
END' > beijing_v.txt
# http://wiki.openstreetmap.org/wiki/Osmosis
wget http://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz
tar xfz osmosis-latest.tgz
cd osmosis-latest/bin
./osmosis \
    --read-pbf file="china-latest.osm.pbf" \
    --bounding-polygon file="beijing_v.txt" \
    --write-xml file="beijing-2.osm"

# ---- END of download OpenStreetMap ----





# ---- extract map for taxi ----

#  http://osm2po.de/
# download osm2po
wget http://osm2po.de/download.php?lnk=osm2po-4.7.7.zip
unzip osm2po-4.7.7.zip
cd osm2po-4.7.7
# fix bugs in osm2po.config, change to these or see ~/Workspace/ITSproject/tools/osm2po/osm2po-4.7.7/osm2po.config
----------------------------------------------------
# Custom flags with ascending binary values 1, 2, 4, 8 ...
# You may define up to 32 Flags (Bits).

wtr.flagList = car, bike, foot, rail, ferry, roundabout

# final decision; only allow ways with these flags

wtr.finalMask = car

# very special hint for level_crossing modification

wtr.shuttleTrainMask = rail|car

# Main-Tag definitions. Params 1-4:
# 1) concurrent order
# 2) class (1-127)
# 3) default speed in kmh
# 4) allowed transportation type (optional) - since v4.5.30

tr.tag.highway.motorway =       1, 11, 120, car
wtr.tag.highway.motorway_link =  1, 12, 30,  car
wtr.tag.highway.trunk =          1, 13, 90,  car
wtr.tag.highway.trunk_link =     1, 14, 30,  car
wtr.tag.highway.primary =        1, 15, 70,  car
wtr.tag.highway.primary_link =   1, 16, 30,  car
wtr.tag.highway.secondary =      1, 21, 60,  car
wtr.tag.highway.secondary_link = 1, 22, 30,  car
wtr.tag.highway.tertiary =       1, 31, 40,  car|bike
wtr.tag.highway.tertiary_link =  1, 32, 30,  car|bike
wtr.tag.highway.living_street =  1, 61, 7,   car|bike|foot
wtr.tag.highway.pedestrian =     1, 62, 5,   bike|foot
wtr.tag.highway.residential =    1, 34, 50,  car|bike
wtr.tag.highway.unclassified =   1, 42, 30,  car|bike
# wtr.tag.highway.service =        1, 51, 5,   car|bike
wtr.tag.highway.track =          1, 71, 10,  car|bike|foot
wtr.tag.highway.bus_guideway =   1, 72, 50,  car
wtr.tag.highway.road =           1, 41, 30,  car|bike
wtr.tag.highway.path =           1, 72, 10,  bike|foot
wtr.tag.highway.cycleway =       1, 81, 15,  bike
wtr.tag.highway.footway =        1, 91, 5,   foot

wtr.tag.route.ferry =            2,  1, 10,  ferry
wtr.tag.route.shuttle_train =    2,  2, 50,  rail|car
wtr.tag.railway.rail =           3,  3, 50,  rail
wtr.tag.highway.motorway_junction = 1, 17, 30, car
wtr.tag.highway.mini_roundabout = 1, 23, 30, car|bike

# Other tags may overwrite the transportion type definition above.
# They allow or explicitly deny things, so the finalMask can
# catch or drop a set of tags at the end.
# Tags without explicit values like wtr.deny.motorcar act like
# an else-part and will be used if no other tag=value matches.
# Since Version 4.5.30 you may substitute keys. e.g.
# 'wtr.deny.motor[_vehicle|car]' will be replaced by
# 'wtr.deny.motor_vehicle' and 'wtr.deny.motorcar'.
# Nested expressions like ..[...[...]].. are not supported.

wtr.allow.motor[car|_vehicle].[yes|destination] = car
wtr.allow.[bicycle|cycleway] = bike
wtr.allow.junction.roundabout = car

# wtr.deny.tracktype.grade[4|5] = car|bike
# wtr.deny.access.no = car|bike|foot|rail|ferry
# wtr.deny.vehicle.no = car|bike
# wtr.deny.motor[_vehicle|car] = car
# wtr.deny.[bicycle|cycleway].no = bike
# wtr.deny.foot.no = foot
---------------------------------------------------

# transform OpenStreetMap data file to SQL file
java -Xmx512m -jar osm2po-core-4.7.7-signed.jar prefix=hh tileSize=x beijing-2.osm
# login as postgres user (default user created by postgres installation)
su postgres
# login postgres
psql -U postgres
# need a new database to store map
create database beijing_mm_po;
\c beijing_mm_po;
create extension postgis;
# exit postgres
\q
exit
cd hh
su postgres
# run SQL to put map into map database
psql -U postgres -d beijing_mm_po -q -f hh_2po_4pgr.sql
# connect to map database
psql -U postgres -d beijing_mm_po
# change default table name
alter table hh_2po_4pgr rename to ways;

# ---- END of extract map ----






# ---- build pgrouting2.0 web application ----

# install pgrouting
# http://docs.pgrouting.org/2.0/en/doc/index.html
git clone https://github.com/pgRouting/pgrouting.git
mkdir build
cd build
cmake  ..
make
sudo make install
# build web app
# http://docs.pgrouting.org/2.0/en/doc/src/tutorial/tutorial.html
createdb beijing_routing
psql beijing_routing -c "create extension postgis"
psql beijing_routing -c "create extension pgrouting"
# import OpenStreetMap data to pgrouting database
# http://pgrouting.org/docs/tools/osm2pgrouting.html
git clone https://github.com/pgRouting/osm2pgrouting.git
cd osm2pgrouting
make
./osm2pgrouting -file your-OSM-XML-File.osm \
                -conf mapconfig.xml \
              -dbname beijing_routing \
                -user postgres \
               -clean
# create topology table
# http://docs.pgrouting.org/2.0/en/doc/src/tutorial/tutorial.html
psql -U postgres -d beijing_routing
select pgr_createTopology('ways', 0.000001);
# create web app
# http://docs.pgrouting.org/2.0/en/doc/src/tutorial/tutorial.html
# workshop of pgrouting2.0 is TBD
# workshop of pgrouting1.x can be found at http://workshop.pgrouting.org/chapters/installation.html (maybe 2.0 is cool with this...) 
# or see my job at ~/Workspace/ITSproject/pgrouting-web using php web-server
sudo ln -s ~/Workspace/ITSproject/pgrouting-web /var/www/pgrouting-web
sudo apt-get install php5
sudo apt-get install php5-pgsql
sudo /etc/init.d/postgresql restart
sudo /etc/init.d/apache2 restart

# ---- END of install pgrouting ----




# ---- install lib ----

# Python 2.7.3
MySQLdb, getpass, 
psycopg2, networkx, rtree
numpy, scipy
pprocess

# Javascript
jquery-1.8.0
OpenLayers-2.13-dev.js
jquery.ratyi-2.5.2.js
jquery.json-2.4.js

# R 3.0.1
download R source package
./configure
make
./bin/R
# R packages
DBI, RMySQL, PostgreSQL
ggplot2, grid, Hmisc, xts

# ---- END of install lib ----




# install tracks table

# install paths table




# ---- install go ----

wget http://golangtc.com/static/go/go1.3.3.linux-386.tar.gz
sudo tar -C /usr/local -xzf go1.3.3.linux-386.tar.gz
add "export PATH=$PATH:/usr/local/go/bin" to /etc/profile

# add syntax highlight in vim
cp -R /usr/local/go/misc/vim/syntax ~/.vim/syntax
cp -R /usr/local/go/misc/vim/autoload ~/.vim/autoload
cp -R /usr/local/go/misc/vim/ftdetect ~/.vim/ftdetect
add "set rtp+=/usr/local/go/misc/vim
filetype plugin on" to ~/.vimrc

# install postgresql package
mkdir ~/.go
export GOPATH=$HOME/.go
go get github.com/lib/pq


# ---- END of install go ----
