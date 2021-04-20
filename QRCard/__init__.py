from flask import Flask, request, jsonify
import QRCard.main as main

app = Flask(__name__)
server_att = main.Users()
variables = server_att.variables

@app.route('/')
def index():
    return jsonify(Home='Welcome')


@app.route('/<string:username>')
def user(username):
    user = server_att.getProfile("username", username)
    return user


@app.route('/api/v1/auth/json', methods=['GET'])
def auth():
    _id = request.args.get('id', None)

    if server_att.checkId(_id) == True:
        return server_att.auth(_id)
    else:
        return {"message": "User id is incorrect", "user": {}, "result": False}


@app.route('/api/v1/login/json', methods=['GET'])
def login():
    email = request.args.get('email', None)
    password = request.args.get('password', None)

    if email != None and password != None:
        return server_att.login(email, password)
    else:
        return {"message": "email-and-password-cannot-be-empty", "result": False}


@app.route('/api/v1/register/initial/json', methods=['POST'])
def initRegister():
    email = request.args.get('email', None)
    password = request.args.get('password', None)
    checkEmail = server_att.checkEmail(email)

    if checkEmail["result"] and len(password) >= 8:
        return server_att.initRegister(email, password)
    elif len(password) < 8:
        return {"message": "weak-password", "user": {}, "result": False}
    else:
        return checkEmail


@app.route('/api/v1/register/sendVerfCode/json', methods=['GET'])
def sendVerfCode():
    _id = request.args.get('id', None)
    email = request.args.get('email', None)

    if server_att.checkId(_id) == True:
        return server_att.sendVerfCode(_id, email)
    else:
        return {"message": "User id is incorrect", "user": {}, "result": False}

@app.route('/api/v1/register/isVerified/json', method=['GET'])
def isVerified():
    _id = request.args.get('id', None)

    if server_att.checkId(_id) == True:
        return server_att.isVerified(_id)
    else:
        return {"message": "User id is incorrect", "user": {}, "result": False}

@app.route('/api/v1/register/approveEmail/json', methods=['POST'])
def approveEmail():
    _id = request.args.get('id', None)
    email= request.args.get('email', None)
    code = request.args.get('confirmCode', None)

    if server_att.checkId(_id) == True:
        return server_att.approveEmail(_id, email, code)
    else:
        return {"message": "User id is incorrect", "user": {}, "result": False}


@app.route('/api/v1/register/complete/json', methods=['POST'])
def compRegister():
    _id = request.args.get('id', None)
    username = request.args.get('username', None)
    fullname = request.args.get('fullname', None)
    image = request.files.get('image', None)

    if server_att.checkId(_id) == False:
        return {"message": "User id is incorrect", "user": {}, "result": False}
    elif username == None:
        return {"message": "Username cannot be empty", "user": {}, "result": False}
    elif fullname == None:
        return {"message": "Fullname cannot be empty", "user": {}, "result": False}

    checkUsername = server_att.checkUsername(username)
    if checkUsername["result"]:
        return server_att.compRegister(_id, username, fullname, image)
    else:
        return checkUsername


@app.route('/api/v1/update/json', methods=['POST'])
def update():
    _id = request.args.get('id', None)
    email = request.args.get('email', None)
    username = request.args.get('username', None)
    fullname = request.args.get('fullname', None)
    image = request.files.get('image', None)

    if server_att.checkId(_id) == True:
        return server_att.update(_id, email, username, fullname, image)
    else:
        return {"message": "User id is incorrector", "user": {}, "result": False}

@app.route('/api/v1/delete/json',methods=['DELETE'])
def delete():
    _id = request.args.get('id', None)

    if server_att.checkId(_id) == True:
        return server_att.delete(_id)
    else:
        return {"message": "User id is incorrector", "user": {}, "result": False}


@app.route('/api/v1/accounts/add/json', methods=['POST'])
def addAccount():
    _id = request.args.get('id', None)
    platform = request.args.get('platform', None)
    account = request.args.get('account', None)
    if server_att.checkId(_id) == True:
        return server_att.addAccount(_id, platform, account)
    else:
        return {"message": "User id is incorrect", "user": {}, "result": False}


@app.route('/api/v1/accounts/delete/json', methods=['DELETE'])
def deleteAccount():
    _id = request.args.get('id', None)
    platform = request.args.get('platform', None)

    if server_att.checkId(_id) == True:
        return server_att.deleteAccount(_id, platform)
    else:
        return {"message": "User id is incorrect", "user": {}, "result": False}


@app.route('/api/v1/accounts/update/json', methods=['POST'])
def updateAccount():
    _id = request.args.get('id', None)
    platform = request.args.get('platform', None)
    account = request.args.get('account', None)
    if server_att.checkId(_id) == True:
        return server_att.updateAccount(_id, platform, account)
    else:
        return {"message": "User id is incorrect", "user": {}, "result": False}


@app.route('/api/v1/accounts/get/json', methods=['GET'])
def getAccounts():
    _id = request.args.get('id', None)

    if server_att.checkId(_id) == True:
        return server_att.getAccounts(_id)
    else:
        return {"message": "User id is incorrect", "user": {}, "result": False}


# @app.route('/api/v1/search/json', methods=['GET'])
# def search():
#     _id = request.args.get('id', None)
#     value = request.args.get('value', None)

#     if server_att.checkId(_id) == True:
#         return server_att.search(value)
#     else:
#         return {"message": "User id is incorrect", "users": {}, "result": False}


@app.route('/api/v1/cards/json', methods=['GET', 'POST'])
def cards():
    if request.method == 'GET':
        _id = request.args.get('id', None)

        if server_att.checkId(_id) == True:
            return server_att.getUsers(_id)
        else:
            return {"message": "User id is incorrect", "result": False}
    elif request.method == 'POST':
        _id = request.args.get('id', None)
        user = request.args.get('user', None)

        if server_att.checkId(_id) == True:
            return server_att.addUser(_id, user)
        else:
            return {"message": "User id is incorrect", "result": False}


if __name__ == "__main__":

    app.run(host=variables['SERVER_CLIENT_HOST'],
            port=variables['SERVER_CLIENT_PORT'])
