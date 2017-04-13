CLAtoolkit
========

The Connected Learning Analytics toolkit (new django architecture, superseeding https://github.com/kirstykitto/CLAtoolkit-oldPrototypes)

## Table of Contents
- [Local Installation using VirtualEnv](https://github.com/kirstykitto/CLAtoolkit#local-installation-using-virtualenv)
- [Creating a Development VM Development with-Docker](https://github.com/kirstykitto/CLAtoolkit#Creating-a-Development-VM-Development-with Docker)
- [Creating a Server VM with Docker](https://github.com/kirstykitto/CLAtoolkit#server-installation)
- [Importing a seeded database](https://github.com/kirstykitto/CLAtoolkit#importing-a-seeded-database)
- [Helpful Docker Commands](https://github.com/kirstykitto/CLAtoolkit#helpful-commands)

Local Installation using VirtualEnv
---------

**CLAToolkit is built with Django. The installation is pretty standard but requires PostgreSQL, Numpy and a range of Machine Learning Libraries such as Scikit Learn and Gensim**  
**CLAToolkit also requires Learning Record Store (LRS) to store/retrieve JSON data. You can see the instruction for installing LRS [here](https://github.com/zwaters/ADL_LRS)**  

If you do not have VirtualEnv installed:
```bash
$ pip install virtualenv
$ pip install virtualenvwrapper
$ mkdir ~/.virtualenvs
```

Add the following lines in .bashrc (or .bash_profile)
```bash
$ export WORKON_HOME=~/.virtualenvs
$ source /usr/local/bin/virtualenvwrapper.sh
```

Apply the two lines
```bash
$ source .bashrc
```

**Create a virtual environment for CLAToolkit:**


```bash
$ mkvirtualenv clatoolkit
$ workon clatoolkit
```


**Get code from GitHub:**

```bash
$ git clone https://github.com/kirstykitto/CLAtoolkit.git
$ cd clatoolkit/clatoolkit_project/clatoolkit_project
```

**Install Python and Django Requirements**

***Run these commands below before running requirements.txt.***  
Install prerequisite libraries that are required to install libraries in requirements.txt
```bash
$ sudo apt-get install python-dev libpq-dev libxml2-dev libxslt-dev libigraph0-dev
```

**Install PostgreSQL**  
Install postgreSQL9.4 on Ubuntu 14.04  
PostgreSQL 9.3 is installed as default database on Ubuntu 14.04. However, the CLA toolkit uses PostgreSQL 9.4 or above.
```bash
$ sudo add-apt-repository "deb https://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main"
$ wget --quiet -O - https://postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
$ sudo apt-get update
$ sudo apt-get install postgresql-9.4 postgresql-contrib
```

On a Mac install postgres.app using these instructions: http://postgresapp.com/ 
and add to path using:
```bash
export PATH="/Applications/Postgres.app/Contents/Versions/9.4/bin:$PATH"
```

**Install requirements**  
A requirements.txt file is provided in the code repository. This will take a while especially the installation of numpy. If numpy fails you may have to find a platform specific deployment method eg using apt-get on ubuntu ($ sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose).

```bash
$ sudo pip install -r requirements.txt
```

**Create PostgreSQL database instance**  
You can either create a new postgres database for your CLAToolkit Instance or use database with preloaded Social Media content. A preloaded database is available upon request which comes with a set of migrations.

Create a superuser (if necessary)
```bash
$ sudo su - postgres
$ createuser -P -s -e username
```

Follow http://killtheyak.com/use-postgresql-with-django-flask/ to create a user and database for django
```bash
$ sudo -u username createdb --locale=en_US.utf-8 -E utf-8 -O username cladjangodb -T template0
```

Load an existing database by first creating a new database and then importing data from backup database
```bash
$ sudo -u username createdb --locale=en_US.utf-8 -E utf-8 -O username newdatabasename -T template0
$ psql newdatabasename < backedupdbname.bak
```

**Configure CLAToolkit environment file (.env) with your database credentials and social media secret ID and password**
```bash
$ cp .env.example .env
$ nano .env
```
Then, edit ```.env``` and add secret key and DB details  


**Migration**  
If a new database was created, you will need to setup the database tables and create a superuser.
```bash
$ python manage.py migrate
$ python manage.py createsuperuser
```

If you see an error saying that dotenv has no attribute 'read_dotenv' when you run migrate command, other types of dotenv are likely to conflict with django-dotenv. If so, uninstall them and (re)install django-dotenv if necessary.  
Example error message:
```bash
Traceback (most recent call last):
  File "manage.py", line 8, in <module>
    dotenv.read_dotenv(os.path.join(BASE_DIR, ".env"))
AttributeError: 'module' object has no attribute 'read_dotenv'
```
```bash
$ sudo pip uninstall dotenv
$ sudo pip uninstall python-dotenv
$ sudo pip install django-dotenv==1.4.1
```
  

**Insert the default data into database**  
Default LRS data needs to be stored in the database in advance. Run the insert SQL below.
```bash
insert into xapi_clientapp values (1, 'CLAToolkit LRS', 'Connected Learning Analytics Toolkit', '<LRS access token key>', '<LRS access token secret>', 'http', 'lrs.beyondlms.org', 43, '/xapi/OAuth/initiate','/xapi/OAuth/token', '/xapi/OAuth/authorize', '/xapi/statements', '/regclatoolkitu/');
```
  

**Install Bower Component**  
To install bower, follow the instruction on [https://bower.io/](https://bower.io/)  
  
```bash
$ cd clatoolkit_project/static
$ sudo bower install --allow-root
```

Now you can run the django webserver:
```bash
$ python manage.py runserver
```

If a new database was created go to http://localhost:8000/admin and login with superuser account.  
Edit the user's profile (admin home - Users - click the user).  

Go to http://localhost:8000/ and login to the CLA toolkit. Create a unit via unit offering page (Click the username on the right top corner - Click Create Offering). Once a unit is created, it will be listed in user's dashboard.

When a unit is created, there will be a link to the user registration page (e.g. https://localhost/clatoolkit/unitofferings/1/register/). To add other toolkit users to the unit, give them the link and let them login or create a new user.  


Installation on Ubuntu using Apache
-
Step by step instructions for installation on Ubuntu using Apache server can be found [here](docs/apache-install.md)

Creating a Development VM Development with Docker
---------

**If you're running OSX or Windows installing Docker, Docker Compose, and Machine via [Docker Toolbox](https://www.docker.com/docker-toolbox) is the easiest method.**

Install Docker following the instructions [here](https://docs.docker.com/engine/installation/).

Along with Docker we will be using:
- Docker Compose for orchestrating a multi-container application into a single app, and
- Docker Machine for creating Docker hosts both locally and in the cloud.

On Mac OS X, Docker Machine and Compose are installed with Docker Toolbox. Follow these directions [here](https://docs.docker.com/compose/install/) and [here](https://docs.docker.com/machine/#installation) to install Docker Compose and Machine, respectively on other platforms. Docker Compose does not seem to be available for Windows even though some intructions are below.

Test if docker-machine and docker-compose are installed:

```bash
$ docker-machine --version
docker-machine version 0.5.3, build 4d39a66
$ docker-compose --version
docker-compose version 1.5.2, build e5cf49d
```

Clone the project from the repository using git and enter the directory:

```bash
$ git clone https://github.com/kirstykitto/CLAtoolkit.git
$ cd CLAtoolkit
```

Create a virtual machine for our project to live in:

```bash
$ docker-machine create -d virtualbox dev;
```

Select the dev VM as the machine we want to run commands against:

**Linux/OSX**:
```bash
$ eval "$(docker-machine env dev)"
```

**Windows**:

If you're using cmd.exe replace 'powershell' with 'cmd'

```bash
$ docker-machine.exe env --shell powershell dev
$Env:DOCKER_TLS_VERIFY = "1"
$Env:DOCKER_HOST = "tcp://192.168.99.100:2376"
$Env:DOCKER_CERT_PATH = "C:\Users\n-\.docker\machine\machines\dev"
$Env:DOCKER_MACHINE_NAME = "dev"
# Run this command to configure your shell:
# E:\Program Files\Docker Toolbox\docker-machine.exe env --shell powershell dev | Invoke-Expression
```

Run the outputted command to configure your shell:

```bash
$ docker-machine env --shell powershell dev | Invoke-Expression
```
---

To get the containers started build the images and start the services:

```bash
$ docker-compose build
$ docker-compose up -d
```

This will take quite some time to complete the first time you run it. Subsequent builds will be far quicker as the results are cached from the first build.

Run Django database migrations:

```bash
$ docker-compose run -d clatoolkit_project python manage.py migrate
```

Grab the IP associated with the Docker Machine we created:
```bash
$ docker-machine ip dev
192.168.99.100
```

Navigate to the IP in your browser, which in my case is 192.168.99.100 and you should be greeted with the login page to the toolkit.


Server Installation
---------

Along with Docker we will be using:
- Docker Compose for orchestrating a multi-container application into a single app

Follow the directions [here](https://docs.docker.com/machine/#installation) to install Docker Compose.

Test if docker-compose is installed:

```bash
$ docker-compose --version
docker-compose version 1.5.2, build e5cf49d
```

Clone the project from the repository using git and enter the directory:

```bash
$ git clone https://github.com/kirstykitto/CLAtoolkit.git
$ cd CLAtoolkit
```

To get the containers started build the images and start the services:

```bash
$ docker-compose build
$ docker-compose -f production.yml up -d
```

This will take quite some time to complete the first time you run it. Subsequent builds will be far quicker as the results are cached from the first build.

Run Django database migrations:

```bash
$ docker-compose run -d clatoolkit_project python manage.py migrate
```

The server should now be running on port 80

Importing a seeded database
--------

List the running images:

```bash
$ docker-compose ps
               Name                              Command               State           Ports
-----------------------------------------------------------------------------------------------------
clatoolkit_clatoolkit_project_1       /usr/local/bin/gunicorn cl ...   Up      8000/tcp
clatoolkit_clatoolkit_project_run_1   python manage.py migrate         Up      8000/tcp
clatoolkit_data_1                     /docker-entrypoint.sh true       Up      5432/tcp
clatoolkit_nginx_1                    /usr/sbin/nginx                  Up      0.0.0.0:80->80/tcp
clatoolkit_postgres_1                 /docker-entrypoint.sh postgres   Up      0.0.0.0:5432->5432/tcp
```

Copy the seeded database into the postgres container:

```bash
$ docker cp cladevdbase.bak clatoolkit_postgres_1:/cladevdbase.bak
```

Enter a bash prompt in the postgres container:

```bash
$ docker exec -it clatoolkit_postgres_1 bash
```

Create the default admin account:

```bash
root@96245826afca:/# createuser -U postgres --interactive
Enter name of role to add: aneesha
Shall the new role be a superuser? (y/n) y
```

Restore the seeded database to the default postgres database (or whichever is being currently used):

```bash
psql -U postgres postgres < cladevdbase.bak
```

Helpful Commands
--------

Use restart-containers.sh to have the server reflect changes made in the code (this should eventually be done using docker volumes instead):

```bash
$ ./script_name.sh
```

To see which environment variables are available to the clatoolkit_project service, run:

```bash
$ docker-compose run clatoolkit_project env
```

To view the logs:

```bash
$ docker-compose logs
```
