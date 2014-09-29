# Bulk Data

Much of the data behind Influence Explorer and its APIs is available in
bulk. Listed below are the various datasets, with links to downloads and
schema documentation.

## License

Data returned by this service is subject to the use restrictions set by
the [Federal Election Commission](http://www.fec.gov). By accessing this
data, you understand that you are using the data subject to all
applicable local, state and federal law, including FEC restrictions.

All data licensed under a
[Creative Commons BY-NC-SA license](http://creativecommons.org/licenses/by-nc-sa/3.0/us/).
By downloading data and accessing the API you are agreeing to the terms
of the license.

Federal campaign contribution and lobbying records must be attributed to
[OpenSecrets.org](http://www.opensecrets.org).

State campaign contribution records must be attributed to
[FollowTheMoney.org](www.followthemoney.org).

## Available Datasets

### Campaign Contributions

[Full state and federal data set](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.all.csv.zip) 3.27 GB

#### Federal

Federal records provided by [OpenSecrets.org](http://www.opensecrets.org).  
Please see [OpenSecrets' data README](http://assets.sunlightfoundation.com.s3.amazonaws.com/brisket/1.0/data/CRP_README.txt)
prior to use.

[All federal campaign contribution records](http://datacommons.s3.amazonaws.com/subsets/td-20120907/contributions.fec.csv.zip) 1.57 GB
|
[Schema documentation](contribution.html)

##### By Contribution Year

- [1989-1990](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.1990.csv.zip) 32 MB
- [1991-1992](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.1992.csv.zip) 45 MB
- [1993-1994](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.1994.csv.zip) 50 MB
- [1995-1996](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.1996.csv.zip) 70 MB
- [1997-1998](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.1998.csv.zip) 58 MB
- [1999-2000](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.2000.csv.zip) 91 MB
- [2001-2002](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.2002.csv.zip) 80 MB
- [2003-2004](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.2004.csv.zip) 157 MB
- [2005-2006](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.2006.csv.zip) 121 MB
- [2007-2008](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.2008.csv.zip) 269 MB
- [2009-2010](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.2010.csv.zip) 165 MB
- [2011-2012](http://datacommons.s3.amazonaws.com/subsets/td-20140324/contributions.fec.2012.csv.zip) 299 MB
- [2013-2014](http://datacommons.s3.amazonaws.com/subsets/td-20140927/contributions.fec.2014.csv.zip) 131 MB

#### State

State records provided by [FollowTheMoney.org](http://www.followthemoney.org).

[All state campaign contribution records](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.csv.zip) 1.7 GB
|
[Schema documentation](contribution.html)

##### By Contribution Year

- [1989-1990](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.1990.csv.zip) 5 MB
- [1991-1992](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.1992.csv.zip) 6 MB
- [1993-1994](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.1994.csv.zip) 12 MB
- [1995-1996](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.1996.csv.zip) 42 MB
- [1997-1998](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.1998.csv.zip) 148 MB
- [1999-2000](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.2000.csv.zip) 131 MB
- [2001-2002](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.2002.csv.zip) 205 MB
- [2003-2004](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.2004.csv.zip) 190 MB
- [2005-2006](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.2006.csv.zip) 248 MB
- [2007-2008](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.2008.csv.zip) 203 MB
- [2009-2010](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.2010.csv.zip) 257 MB
- [2011-2012](http://datacommons.s3.amazonaws.com/subsets/td-20121109/contributions.nimsp.2012.csv.zip) 303 MB
- [2013-2014](http://datacommons.s3.amazonaws.com/subsets/td-20130726/contributions.nimsp.2014.csv.zip) 26 KB

### Federal Lobbying

Federal lobbying data provided by [OpenSecrets.org](http://opensecrets.org).

[Full data set](http://datacommons.s3.amazonaws.com/subsets/td-20121001/lobbying.zip) 228 MB
|
[Schema documentation](lobbying.html)

### Earmarks

Earmarks data provided by [Taxpayers for Common Sense](http://taxpayers.net).

[Full data set](http://datacommons.s3.amazonaws.com/subsets/td-20111006/earmarks.zip) 2.7 MB
|
[Schema documentation](earmark.html)

### Federal Grants & Contracts

Federal grant and contract data can be downloaded from
[USASpending.gov](http://www.usaspending.gov/data).

[Schema documentation](grant.html)

### EPA ECHO

EPA data from [EPA ECHO](http://www.epa-echo.gov/echo/idea_download.html).

[All EPA ECHO records](http://datacommons.s3.amazonaws.com/subsets/td-20111006/epa.zip) 6 MB
|
[Schema documentation](epa_echo.html)

_Note: the download contains two files, one with the action records and the
other with case ID's and defendant names (defennm) as they are found in the
EPA data, alongside the verified, corresponding organization name and parent
organization name in [Influence Explorer.](http://influenceexplorer.com)_

### Federal Advisory Committee Act (FACA)

Federal Advisory Committee Act (FACA) data provided by
[U.S. General Services Administration](http://www.gsa.gov/portal/category/21242).

[All FACA records](http://datacommons.s3.amazonaws.com/subsets/td-20120327/faca_records.csv.zip) 16.5 MB

### Federal Regulations

Federal regulatory comments extracted from
[Regulations.gov](http://regulations.gov).

This dataset consists of all of the text extracted from federal rulemaking
dockets on Regulations.gov. It encompasses approximately 13,000 regulatory
dockets comprised of over 3,000,000 documents. The entire dataset is
approximately 14 gigabytes. For each docket, there is one zip file containing
a directory for each document, which, in turn, contains a text file for each
attachment. Both dockets and documents also include additional, JSON-encoded
metadata (date, title, etc.). The docket zip files are organized into
directories by agency.

We offer several mechanisms for downloading this dataset, depending on whether
you're interested in a single docket, an agency's worth of dockets, or the
entire dataset. To find a particular docket you will need the docket ID from
Regulations.gov.

#### Web access

We have made the dataset available for browsing via the web below. Individual
dockets can be downloaded from this site.

[Browse the dataset online](http://torrents.sunlightfoundation.com/browse/regulations-2011-09-27/)

#### BitTorrent

We are also seeding a torrent of all of the regulatory data. This is the
recommended mechanism for downloading the entire dataset. You can use this
torrent to either download data for all agencies, or, if your BitTorrent
client supports it, a subset of either agencies or dockets. For more
information on how to use BitTorrent, see [this LifeHacker
post.](http://lifehacker.com/285489/a-beginners-guide-to-bittorrent)

[Download the dataset via BitTorrent](http://torrents.sunlightfoundation.com/torrents/regulations-2011-09-27.torrent)

#### Rsync

The dataset is also available via Rsync, either in full or part. The link
below is the Rsync URL for the entire dataset. To download only an agency's
worth of data via Rsync, use the [browser interface](http://torrents.sunlightf
oundation.com/browse/regulations-2011-09-27/), locate the agency you wish to
download, then copy the rsync URL from the rightmost column. _Note: our rsync
capacity is limited as rsync is a memory-intensive process. BitTorrent is the
preferred means of downloading full agencies or the entire dataset, so please
only use the Rsync service if you can't use the torrent._

[Download via Rsync](rsync://torrents.sunlightfoundation.com/pub/regulations-2011-09-27)
