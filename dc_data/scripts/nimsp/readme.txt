

NIMSP:

Database setup:

	PostreSQL server with the following databases:
		- datacommons
		- salts
		- util
		- nimsp

	MySQL server with the following database:
		- nimsp


Data downloads:

	Download all files from http://my.followthemoney.org/sunlight/. Place them in the following directories:
		- 2009-04-06
		- 2009-05-22
		- 2009-09-01
	(I'm assuming that these go in ~/data/download/nimsp/, but they can be put anywhere.)
		
Load the raw data into MySQL:

	Create the tables with:
	
		mysql nimsp < ~/data/download/nimsp/2009-04-06/NIMSP_Data.sql
		
	Load the initial data with:
	
		load-nimsp -s ~/data/download/nimsp/2009-04-06/
		
	Load the updates with:
	
		load-nimsp-update -s ~/data/download/nimsp/2009-05-22
		load-nimsp-update -s ~/data/download/nimsp/2009-09-01
		
Run the salting scripts:

	Run
	
		createlang plpgsql util

	Then from schema/postgresql/util run:
	
		psql util < <file>
		
	for each file in table, indexes, and functions, in that order.
	
	Then run
	
		bin/load-names
		bin/make-locations
		
	From schema/postgresql/salts run:
		
		psql salts < <file>
		
	for the files in tables tables and indexes.
	
	Then run
	
		bin/make-salts -n 7500
		
	where 7500 was determined by Garrett to be an appropriate number of salted records to add.
		
Finally, denormalize the data with:

	python denormalize_nimsp.py -d ~/data
		
		
