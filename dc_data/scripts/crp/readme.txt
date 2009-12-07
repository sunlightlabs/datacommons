
CRP:

Download the data with:

	python download.py ~/data
	
Extrac the data with:

	python extract.py ~/data
	
Denormalize the data with:

	python denormalize_pac2pac.py ~/data
	python denormalize_pac2candidate.py ~/data
	python denormalize_indiv.py ~/data
	
Split the 'indiv' file into smaller chunks:

	split -l 3000000 denormalize_indiv.py denormalize_indiv_split.
	
	This is only necessary because the loadcontributions command will run out of memeory when run with
	the full data set.	
	
Load each denormalized file from ~/data/denormalized with a command like:

	python manage.py loadcontributions ~/data/denormalized/denorm_<xxx>.csv
	
	
	