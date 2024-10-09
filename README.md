# Mamut&Lomihlav

Webová platforma na zabezpečenie chodu jednodňových súžaží organizovaných združením STROM.

## Requirements installation

 - Python (3 or later, version 3.10.0 recommended)
 - Django (version 4.2)
 - virtual enviroment

### Windows machine
Install Python from https://www.python.org/downloads/ and then in CMD type:

```cmd
python -m pip install virtualenv
```
### Linux machine
In Bash type:

```bash
sudo apt install pip
```
```bash
python3 -m pip install virtualenv
```

## Server setup for local network

You have to get through local setup only once (per a project).

### Windows machine

In CMD:

Create virtual enviroment
```cmd
py -m venv ENV_NAME
```
where `ENV_NAME` is your desired name for the newly created virtual environment, e. g. `venv`.
Perhaps, you will need to allow remote access in your firewall.

### Linux machine

In Terminal:

Create virtual enviroment
```cmd
virtualenv ENV_NAME
```
Install dependencies:
```cmd
pip install -r requirements.txt
```

and allow remote access for desired `PORT_NUMBER` (e. g. 8080):
```bash
iptables -I INPUT -p tcp -m tcp --dport PORT_NUMBER -j ACCEPT
```

## Base database creation

Make and then apply migrations. You can do it by typing:

```
manage.py makemigrations competition
```
```
manage.py migrate
```

to your CMD or Bash into `sutazeStrom` directory.


## Run server

### Windows machine

In CMD:

1. Go to `sutazeStrom` directory
2. Activate your virtual environment:
```cmd
ENV_NAME\Scripts\activate
```
3. Run server on your desired port:
```cmd
python manage.py runserver 0.0.0.0:PORT_NUMBER
```

### Linux machine

1. Login as root user

In Terminal:

2. Go to `sutazeStrom` directory
3. Activate your virtual environment:
```bash
source ENV_NAME/bin/activate
```
4. Run server on your desired port:
```bash
python manage.py runserver 0.0.0.0:PORT_NUMBER
```

## Application access

After all that you can access to admin site by typing `localhost:PORT_NUMBER/admin` and to app by typing `localhost:PORT_NUMBER/index` (`localhost` can be substituted by an IP address of server e.g. `192.168.1.47`).
