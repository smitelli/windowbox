Windowbox
=========

Don't call it a moblog / I've posted for years.

by [Scott Smitelli](mailto:scott@smitelli.com)

Running in Development
----------------------

Windowbox is developed and tested in a [Vagrant](https://www.vagrantup.com/) environment. Assuming you have all the prerequisites (Vagrant and VirtualBox) installed, setup should be as simple as:

    cd /path/to/repo
    vagrant up
    vagrant ssh

Once inside the VM, everything should be installed and ready for use. The quickest way to get something running is:

    flask create
    flask insert 10
    flask run

Assuming everything worked correctly, the app will be accessible on the host at [http://localhost:5000](http://localhost:5000/).

Using the Development VM
------------------------

All commands should be run with the current working directory set to `/vagrant` -- any deviation from this may result in the `flask` script failing to locate the project directory.

The following shell commands are commonly used:

- `flask create`: Create the development database and all tables within it. This command **must** be run before starting the app or any of its scrupts for the first time.
- `flask drop`: Drop the app tables from the database and delete the Attachment/Derivative files from the storage path.
- `flask insert [count]`: Generate _count_ Posts, each with an Attachment, and add it to the app. If `count` is omitted, it defaults to `1`.
- `flask lint`: Run the flake8 style checker against the Python codebase.
- `flask run`: Run the app. It will listen on port 5000, accessible on the host at [http://localhost:5000](http://localhost:5000/). The app will auto-reload if changes to the source code are detected. To stop it, hit Ctrl+C.
- `flask shell`: Start an interactive REPL shell with an appropriate environment for app development. Noteworthy globals include `app` and `g`, which can be used immediately without importing anything.
- `flask test`: Run the unit test suite and display the code coverage report. Any options supported by pytest (like `-v` or `-k some_module`) can be provided and will be passed to the underlying test runner.

Local storage is in `/var/opt/windowbox`. This is where the dev/test SQLite database files, the virtualenv, and the Attachment/Derivative storage data are all located.

TODOs
-----

- prod docs, `WINDOWBOX_CONFIG=configs/dev.py windowbox-bark/fetch`
- `flask assets clean; flask assets build`
- make sure process runs with a umask that makes FS files look good
- setup.py: url, project_urls, add non-*.py files to manifest
- spellcheck/cap/indent style
- cache headers: etag, last-modified, cache-control?, expires?
- document REST API schema and unit test its shape
- split up overloaded tests
- sender.email_address needs to be utf8mb4_unicode_520_ci on mysql; how to do that?
