
# note: these instructions are slightly out of date due to the new command system.
# in general, run as 'python manage.py <command-name> ...' instead of running the script directly.

CRP:

Download the data with:

	python download.py ~/data
	
Extrac the data with:

	python extract.py ~/data
	
Denormalize the data with:

	python denormalize_pac2pac.py -d ~/data
	python denormalize_pac2candidate.py -d ~/data
	python denormalize_indiv.py -d ~/data
		
Load each denormalized file from ~/data/denormalized with a command like:

	python manage.py loadcontributions ~/data/denormalized/denorm_<xxx>.csv
	
	
	