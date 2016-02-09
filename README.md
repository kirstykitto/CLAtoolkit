CLAtoolkit
========

The Connected Learning Analytics toolkit (new django architecture, superseeding https://github.com/kirstykitto/CLAtoolkit-oldPrototypes)

## Todo
- Create/Assign all participants to groups (Working - Manually)
- CoI Interface: Messages to be classified by everyone - order messages received to be different order for every group

## Table of Contents
- [Development Installation](https://github.com/kirstykitto/CLAtoolkit#development-installation)
- [Server Installation](https://github.com/kirstykitto/CLAtoolkit#server-installation)
- [Importing a seeded database](https://github.com/kirstykitto/CLAtoolkit#importing-a-seeded-database)
- [Helpful Commands](https://github.com/kirstykitto/CLAtoolkit#helpful-commands)

Development Installation
---------

**If you're running OSX or Windows installing Docker, Docker Compose, and Machine via [Docker Toolbox](https://www.docker.com/docker-toolbox) is the easiest method.**

Install Docker following the instructions [here](https://docs.docker.com/engine/installation/).

Along with Docker we will be using:
- Docker Compose for orchestrating a multi-container application into a single app, and
- Docker Machine for creating Docker hosts both locally and in the cloud.

Follow the directions [here](https://docs.docker.com/compose/install/) and [here](https://docs.docker.com/machine/#installation) to install Docker Compose and Machine, respectively.

Test if docker-machine and docker-compose are installed:

```bash
λ docker-machine --version
docker-machine version 0.5.3, build 4d39a66
λ docker-compose --version
docker-compose version 1.5.2, build e5cf49d
```

Clone the project from the repository using git and enter the directory:

```bash
λ git clone https://github.com/kirstykitto/CLAtoolkit.git
λ cd CLAtoolkit
```

Create a virtual machine for our project to live in:

```bash
λ docker-machine create -d virtualbox dev;
```

Select the dev VM as the machine we want to run commands against:

**Linux/OSX**:
```bash
λ eval "$(docker-machine env dev)"
```

**Windows**:

If you're using cmd.exe replace 'powershell' with 'cmd'

```bash
λ docker-machine.exe env --shell powershell dev
$Env:DOCKER_TLS_VERIFY = "1"
$Env:DOCKER_HOST = "tcp://192.168.99.100:2376"
$Env:DOCKER_CERT_PATH = "C:\Users\n-\.docker\machine\machines\dev"
$Env:DOCKER_MACHINE_NAME = "dev"
# Run this command to configure your shell:
# E:\Program Files\Docker Toolbox\docker-machine.exe env --shell powershell dev | Invoke-Expression
```

Run the outputted command to configure your shell:

```bash
λ docker-machine env --shell powershell dev | Invoke-Expression
```
---

To get the containers started build the images and start the services:

```bash
λ docker-compose build
λ docker-compose up -d
```

This will take quite some time to complete the first time you run it. Subsequent builds will be far quicker as the results are cached from the first build.

Run Django database migrations:

```bash
λ docker-compose run -d clatoolkit_project python manage.py migrate
```

Grab the IP associated with the Docker Machine we created:
```bash
λ docker-machine ip dev
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
λ docker-compose --version
docker-compose version 1.5.2, build e5cf49d
```

Clone the project from the repository using git and enter the directory:

```bash
λ git clone https://github.com/kirstykitto/CLAtoolkit.git
λ cd CLAtoolkit
```

To get the containers started build the images and start the services:

```bash
λ docker-compose build
λ docker-compose -f production.yml up -d
```

This will take quite some time to complete the first time you run it. Subsequent builds will be far quicker as the results are cached from the first build.

Run Django database migrations:

```bash
λ docker-compose run -d clatoolkit_project python manage.py migrate
```

The server should now be running on port 80

Importing a seeded database
--------

List the running images:

```bash
λ docker-compose ps
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
λ docker cp cladevdbase.bak clatoolkit_postgres_1:/cladevdbase.bak
```

Enter a bash prompt in the postgres container:

```bash
λ docker exec -it clatoolkit_postgres_1 bash
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
λ ./script_name.sh
```

To see which environment variables are available to the clatoolkit_project service, run:

```bash
λ docker-compose run clatoolkit_project env
```

To view the logs:

```bash
λ docker-compose logs
```
