
CRP:

Download the data with:

	python download.py ~/data
	
Extrac the data with:

	python extract.py ~/data
	
Denormalize the data with:

	python denormalize_pac2pac.py ~/data
	python denormalize_pac2candidate.py ~/data
	python denormalize_indiv.py ~/data
	
Load each denormalized file from ~/data/tmp with a command like:

	python manage.py loadcontributions ~/data/tmp/denorm_<xxx>.csv
	
	