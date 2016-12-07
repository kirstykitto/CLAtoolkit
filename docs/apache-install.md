# Setting up the CLA Toolkit with Apache
How to setup the CLA Toolkit on Ubuntu 14.04 using the Apache server.  

**Install dependancies:**
```bash
$ sudo apt-get update
$ sudo apt-get install git python-pip python-dev apache2 libapache2-mod-wsgi postgresql postgresql-contrib python-psycopg2 libxml2-dev libxslt-dev libpq-dev
```

**Clone the CLAtoolkit repo locally:**
```bash
$ git clone https://github.com/kirstykitto/CLAtoolkit.git
$ cd CLAtoolkit
```

**Setup virtualenv:**
```bash
$ sudo pip install virtualenv
$ sudo pip install virtualenvwrapper
$ mkvirtualenv clatoolkit
```

**Install Python dependancies:**
```bash
$ pip install -r requirements.txt
```

**Setup Postgres:**
```bash
$ sudo -u postgres createuser -P clatoolkit -s
$ sudo createdb -U clatoolkit --locale=en_US.utf-8 -E utf-8 -O clatoolkit cladjangodb -T template0 -h 127.0.0.1 --username=clatoolkit
```
When prompted for a password, use the password for the Postgres user you just created

**Configure clatoolkit environment with your database credentials:**
```bash
$ cp .env.example .env
$ nano .env
```
Make sure to change the `DEBUG` flag to 0 if this instance is being used in production

**Initialise the Database:**
```bash
$ python clatoolkit_project/manage.py migrate
```

**Create a superuser:**
```bash
$ python manage.py createsuperuser
```

**Edit the Apache configuration:**
```bash
$ sudo nano /etc/apache2/sites-available/000-default.conf
```

An example working configuration file is shown below:
```apache
<VirtualHost *:80>
    #ServerName example.com
    ServerAdmin webmaster@localhost

    Alias /static /home/ubuntu/CLAtoolkit/clatoolkit_project/static
    <Directory /home/ubuntu/CLAtoolkit/clatoolkit_project/static>
        Require all granted
    </Directory>

    <Directory /home/ubuntu/CLAtoolkit/clatoolkit_project/clatoolkit_project>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    WSGIDaemonProcess cla python-path=/home/ubuntu/CLAtoolkit/clatoolkit_project:/home/ubuntu/.virtualenvs/clatoolkit/lib/python2.7/site-packages
    WSGIProcessGroup cla
    WSGIApplicationGroup %{GLOBAL}
    WSGIScriptAlias / /home/ubuntu/CLAtoolkit/clatoolkit_project/clatoolkit_project/wsgi.py

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>
```

**Enable the site:**
```bash
$ a2ensite 000-default.conf
```

**Restart Apache:**
```
$ sudo service apache2 restart
```

You should now have a working instance of the CLA Toolkit running on your Ubuntu server
