# Setting up the CLA Toolkit with Apache
How to setup the CLA Toolkit on Ubuntu 14.04 using the Apache server.  

**The CLA toolkit needs to be installed in advance. The instruction can be found [here](https://github.com/kojiagile/CLAtoolkit/blob/koji/README.md#local-installation-using-virtualenv)**  

**Install Apache and dependancies**
```bash
$ sudo apt-get update
$ sudo apt-get install apache2 libapache2-mod-wsgi python-psycopg2
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
