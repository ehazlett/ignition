:: Ignition ::
--------------

Python web application stack creator (Python + uWSGI + Nginx)

Ignition is a stack creator for Python web applications.  It will create
the Python project (currently Django and Flask), a uWSGI start script, and 
a config file to launch Nginx as the frontend.  It will also create startup
and shutdown sample scripts for launching the stack.

Installation::

    $ pip install ignition

Or (manually): 

Clone/download::
    
    $ python setup.py install

Example
=======

To create a Django project called 'helloworld' listening on port 80, running under the user 'nginx', and located in /srv/projects::

    $ ignite.py -d /srv/projects -n helloworld -u nginx -p 80 -t django

To create a Flask project called 'helloworld' using shared hosting (virtual hosts) with the user 'nginx located in /srv/projects::

    $ ignite.py -d /srv/projects -n helloworld -u nginx --shared-hosting -t flask

Make sure to set permissions for the user it's running under, in this case 'nginx'::

    $ cd /srv/projects
    $ sudo chown nginx var/ log/

You can then 'cd' into /srv/projects/scripts and run::

    $ sudo ./helloworld_start.sh

Visit http://localhost in your web browser and you should see the standard 'It works!' Django page or 'Hello from Flask...' if you are using Flask.


