* install pip and virtualenv
  - sudo apt-get install python-pip
  - sudo apt-get install python-setuptools (if you don't already have easy_install)
  - sudo easy_install virtualenv

* install and configure virtualenvwrapper:
  $ sudo pip install virtualenvwrapper
  $ echo 'export WORKON_HOME="path/to/virtualenvs"' >> ~/.bashrc
  $ echo "source /usr/local/bin/virtualenvwrapper_bashrc" >> ~/.bashrc

* create a new virtual env for datacommons. this will also activate it:
  $ mkvirtualenv datacommons
  note that the 'datacommons' dir can already exist or not. this command will create bin/ include/ and lib/ directories inside the datacommons directory.  

* if you need activate the datacommons virtualenv later, use:
  $ workon datacommons

* install dependencies in requirements.txt files for dc_web and
  dc_matchbox
  $ pip install -E datacommons/ <package name>
   
* add dc_data, dc_matcchbox, dc_web to the virtual env python path
  $ add2virtualenv [dir]

* create local_settings.py files for both dc_web and dc_matchbox apps
  (get a copy from someone else). 

* manage.py runserver 


