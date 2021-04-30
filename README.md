# QRCard

This repo contains Business card web and mobile application server where users can keep and share all their social media accounts with Python Flask using QR Code and NFC technologies.

## Installation

**Be sure to use the same version of the code as the version of the docs you're reading.**
You probably want the latest tagged version, but the default Git version is the master branch.

```shell
# clone the repository
$ git clone https://github.com/furkankyildirim/QRCard
$ cd QRCard
# checkout the correct version
$ git tag
```

Create a virtualenv and activate it:
```shell
$ python3 -m venv venv --without-pip
$ source venv/bin/activate
```

Or on Windows cmd:
```shell
$ py -3 -m venv venv
$ venv\Scripts\activate.bat
```
Install pip3 requirements
```shell
$ pip3 install -r requirements.txt
```

## Run
```shell
$ export FLASK_APP=QRCard 
# to run in developer mode
$ export FLASK_ENV=development
$ flask run
```
Or on Windows cmd:
```shell
$ set FLASK_APP=QRCard
# to run in developer mode
$ set FLASK_ENV=development
$ flask run
```
Open http://127.0.0.1:5000 in a browser.

## Edit Config File

Edit the [config.txt](https://github.com/furkankyildirim/QRCard/tree/master/config.txt) file so that the program can run on your own server.
```text
SERVER_CLIENT_HOST : Your_server_host
SERVER_CLIENT_PORT : Your_server_port
MONGO_CLIENT : mongodb_url
SENDER_EMAIL_ACCOUNT : Sender_email_account
SENDER_EMAIL_PASSWORD : Sender_email_password
```
