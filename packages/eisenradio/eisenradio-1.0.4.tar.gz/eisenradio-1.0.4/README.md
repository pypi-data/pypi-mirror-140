Eisenradio - a Web radio expandable collection
---
 * Organize your web radios; delete and update, backup and restore
 * Style your app with pictures, import a poem, song text, or a funny comment to have a good time
 * Create a shuffled playlist of your local audio files in seconds
 * More action; a ping variable shows the response time and a spectrum analyser the frequency range 
 * Travel through the app at breakneck speed, thanks to the smart design of the controls 
 * Android: download to mobile (link below .-apk), rename *WHL to *ZIP, extract with Android _file_ manager
 * https://pypi.org/project/eisenradio-apk/

Eisenradio - the boring details 
---
 * REST API app on blueprints and application factory of the flask framework on a SQLite database
 * Eisenradio runs in a terminal (on PC)
 * Kill the browser window, streams for listen and rec will be up; kill the terminal - all stops
 * Eisenradio uses its own internal API and adjusts the buffer size for a given bit rate
 * Backup and restore are easy work with the help of an exported *ini file (on PC)
 * Eisenradio uses Pythons sys.path; it will find its modules on the dark side of the moon 
 * Runs on one processor only, due to the use of Python Multithreading
 * Android Package uses Python Kivy for multi-touch to start and promote itself to "foreground service" (not get killed)
 * Backend (server) opens the connection, buffers the incoming stream and presents it to the browsers internal net
 * Frontend (browser) controls the backend, plays local audio and has a spectrum analyser at your disposal

 
		""" sketch """

	     |B |               |S | Flask web server, Header[Werkzeug/2.0.2 Python/3.10.1]
	     |r |listen         |e |-------> starRadio
	     |o |------->   <-- |r |
	     |w |GhettoRecorder |v |-------> planetRadio
	     |s |--->    <----- |e |
	     |e |               |r |-------> satteliteRadio
	     |r |               |  |
         net: localhost     net: internet
         CORS: accept       CORS: deny
         audioNode: 1,-1    audioNode: 0, 0
         JavaScript,CSS     Python,SQL

    Cross-Origin Resource Sharing mechanism (CORS) 
    i.a. prevents Browser from analysing audio from internet
    

pip install
-
	""" xxs Linux xxs """
    $ pip3 install eisenradio
    $ python3 -m eisenradio.wsgi  # watch flask

    """ xxm Windows xxm """
    > pip install eisenradio
    > python -m eisenradio.wsgi

    """ xxl big company xxl """
    $$$ pip3 install eisenradio
    $$$ python3 -m eisenradio.app  # serve flask
    """ for the sake of completeness, a python
        production server 'waitress' is started """

Pytest
---
> ~ ... /test/functional$ python3 -m pytest -s    # -s print to console

find the modified test db in ./app_writable/db

Uninstall
---
Python user:

* find module location
* uninstall and then remove remnants

>$ pip3 show eisenradio

>$ pip3 uninstall eisenradio

Location: ... /python310/site-packages
