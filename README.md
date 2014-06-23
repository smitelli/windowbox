To run the app:
---------------

System packages:

* python-pip
* python-dev
* libmysqlclient-dev
* libjpeg-dev
* zlib1g-dev
* libimage-exiftool-perl

Python packages (NOTE: Make a virtualenv first, unless you don't care):

* `pip install -r reqs.txt`

Copy the built CSS and JS files into `./windowbox/static/{css,js}`.

The WSGI module is `windowbox.application`, and the callable is `app`.

The production config file can be specified with the `WINDOWBOX_CONFIG_FILE`
environment variable. If this is unset, development defaults will be used.

`fetch.py` is the cron script that fetches new posts from an IMAP server.

Additionally, to develop or build the app:
------------------------------------------

System Packages:

* npm
* ruby

npm Modules:

* `sudo npm install -g grunt-cli`
* `npm install`

Ruby Gems:

* `gem install sass`

Python Packages:

* `pip install flake8`

**To run the dev app:** `python run_dev.py`

**To watch for CSS/JS changes and continually rebuild:** `grunt`

**To build the CSS and JS:** `grunt dev`

**To lint the Python and JS code:** `grunt lint`
