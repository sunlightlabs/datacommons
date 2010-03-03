* install pip, virtualenv
  - pip is a tarball you can download online
  - then for virtualenv:
    $ sudo easy_install virtualenv

* install dependencies in requirements.txt files for dc_web and
  dc_matchbox
  $ pip install -E datacommons/ <package name>

* install and configure virtualenvwrapper:
  $ [sudo] pip install virtualenvwrapper
  $ echo 'export WORKON_HOME="path/to/virtualenvs"' >> ~/.bashrc
  $ echo "source /usr/local/bin/virtualenvwrapper_bashrc" >> ~/.bashrc

* create a new virtual env for datacommons. this will also activate
  it:
  $ mkvirtualenv datacommons

* if you need activate the datacommons virtualenv later, use:
  $ workon datacommons
   
* add dc_data, dc_matcchbox, dc_web to the virtual env python path
  $ add2virtualenv [dir]

* create local_settings.py files for both dc_web and dc_matchbox apps
  (get a copy from someone else). 

* manage.py runserver 


