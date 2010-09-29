NIMSP:

Database setup:

    PostgreSQL server with the following databases:
        - datacommons
        - salts
        - util
        - nimsp

    MySQL server with the following database:
        - nimsp


Note: The following instructions are old and assume that you are starting from scratch, loading all the data
releases incrementally. You should be able to skip down to the "Load the updates with" part for whatever
date/release you are working on.

Also a possibility is doing the process for the full dataset, available as Sunlight.RELEASEDATE.tar.gz.

Data downloads:

    If starting from scratch, download all files from http://my.followthemoney.org/sunlight/.
    Place them in the following directories:
        - 2009-04-06
        - 2009-05-22
        - 2009-09-01
    (These normally go in ~/data/download/nimsp/, but they can be put anywhere.)

    To get updates for a single release, use the dcdata/scripts/nimsp/get_nimsp_update.sh script to automate
    the download. Just pass in the release date.

    ./get-nimsp-update 2010-09-22

    It will download the files into ~/data/download/nimsp/my.followthemoney.org/sunlight/2010-09-22

Load the raw data into MySQL:

    If starting from scratch:

        The initial CREATE TABLE statements are in the first release, in NIMSP_Data.sql.

            mysql -p nimsp < ~/data/download/nimsp/my.followthemoney.org/sunlight/2009-04-06/NIMSP_Data.sql

        Load the initial data with:

            load-nimsp -s ~/data/download/nimsp/2009-04-06/

        Load all subsequent releases like so:

            load-nimsp-update -s ~/data/download/nimsp/my.followthemoney.org/sunlight/2009-05-22
            load-nimsp-update -s ~/data/download/nimsp/my.followthemoney.org/sunlight/2009-09-01
            load-nimsp-update -s ~/data/download/nimsp/my.followthemoney.org/sunlight/2009-12-01

    If loading a single release, just load it as follows:

        Make any schema modifications by running the Update-YYYY-MM-DD.sql file:

            mysql -p nimsp < ~/data/download/nimsp/my.followthemoney.org/sunlight/2010-09-22/Update-2010-09-22.sql

        Load the new data:

            load-nimsp-update -s ~/data/download/nimsp/my.followthemoney.org/sunlight/2010-09-22

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

Extract the data from the MySQL server:

    python dump_to_csv.py -o /tmp/nimsp_partial_denormalization.csv

    Then copy the output to the denormalized directory:

    cp /tmp/nimsp_partial_denormalization.csv ~/data/denormalized

    (This manual copying is necessary because the MySQL server process doesn't have permission
    to write to the datacommons' directories.)

Finish the data denormalization:

    python process_csv.py -d ~/data

Split the allocated contributions file into smaller chunks:

    split -l 3000000 nimsp_allocated_contributions.csv nimsp_split.

    This is only necessary because the loadcontributions command will run out of memeory when run with
    the full data set.

Load each denormalized file from ~/data/denormalized with a command like:

    python manage.py loadcontributions ~/data/tmp/nimsp_<xxx>.csv

