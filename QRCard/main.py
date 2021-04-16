from QRCard.config import readTxt
from base64 import b64encode
import pymongo
import qrcode
import hashlib
import smtplib
import datetime
import random
import string
import os
import re

class Users():
    def __init__(self):
        self.variables = readTxt()
        self.connection = pymongo.MongoClient(self.variables['MONGO_CLIENT'])
        self.__mydb = self.connection["QRCardDb"]
        self.__users = self.__mydb['Users']
        self.__accounts = self.__mydb['Accounts']

    def auth(self, _id):
        self.__users.update_one(
            {"_id": _id}, {'$set': {"lastAuth": datetime.datetime.now()}})
        return self.getProfile("_id", _id)

    def login(self, email, password):
        query = {"email": email}
        user = self.__users.find_one(query)
        if user != None:
            password = Functions().encryptValue(password)
            if password == user["password"]:
                if user["username"] != None and user["_id"] != None:
                    user.pop('password')
                    user["qrcode"] = b64encode(user["qrcode"]).decode("ascii")
                    user["profile"] = b64encode(
                        user["profile"]).decode("ascii")
                    self.__users.update_one(
                        query, {'$set': {"lastAuth": datetime.datetime.now()}})
                    return {"message": "login-successfully", "user": user, "result": True, }
                else:
                    self.__users.delete_one(query)
                    return {"message": "deleted-user", "result": False, }
            else:
                return {"message": "email-or-password-not-correct", "result": False, }
        else:
            return {"message": "email-or-password-not-correct", "result": False, }

    def initRegister(self, email, password):
        while True:
            randomString = Functions().createId()
            _id = Functions().encryptValue(randomString)
            if self.__users.find_one({"_id": _id}) == None:
                break

        password = Functions().encryptValue(password)
        confirmCode = Functions().senderEmail(email)
        confirmCode = Functions().encryptValue(confirmCode)
        user = {
            "_id": _id,
            "email": email,
            "password": password,
            "confirmCode": confirmCode,
            "isVerify": False,
            "username": None,
            "fullname": None,
            "profile": None,
            "qrcode": None,
            "match": 0,
            "accounts": {},
            "cards": [],
            "lastAuth": datetime.datetime.now()
        }
        self.__users.insert_one(user)
        return {"message": "new-user-registered", "user": user, "result": True}

    def compRegister(self, _id, username, fullname, image):
        qrCode = Functions().createQR(username)
        query = {"_id": _id}

        image = open("QRCard/images/user.jpg", "rb") if image == None else image
        values = {
            "username": username,
            "fullname": fullname,
            "profile": image.read(),
            "qrcode": qrCode,
            "lastAuth": datetime.datetime.now()
        }

        self.__users.update_one(query, {'$set': values})
        data = self.getProfile("_id", _id)

        if data["result"]:
            user = data["user"]
            return {"message": "registration-completed", "user": user, "result": True}
        else:
            return {"message": data["message"], "result": False}

    def update(self, _id, email, username, fullname, image):
        data = self.getProfile("_id", _id)
        user = data["user"]
        if data["result"]:
            if email != user["email"]:
                checker = self.checkEmail(email)
                if checker["result"]:
                    user["email"] = email
                    self.sendVerfCode(_id, email)
                else:
                    return checker

            if username != user["username"]:
                checker = self.checkUsername(username)
                if checker["result"]:
                    user["username"] = username
                else:
                    return checker

            if fullname != user["fullname"] and fullname != None:
                user["fullaname"] = fullname
            elif fullname == None:
                return {"message": "fullname-cannot-be-empty", "result": False}

            qrcode = Functions().createQR(username)
            user["image"] = image.read()
            user["qrcode"] = qrcode

            self.__users.update_one({"_id": _id}, {'$set': user})
            user["profile"] = b64encode(user["profile"]).decode("ascii")
            user["qrcode"] = b64encode(user["qrcode"]).decode("ascii")

            return {"message": "update-completed", "user": user, "result": True}
        else:
            data

    def delete(self, _id):
        self.__users.delete_one({'_id':_id})
        return {"message": "User-successfully-deleted",  "result": True, } 
    
    def getProfile(self, typeOf, value):
        query = {typeOf: value}
        user = self.__users.find_one(query)

        if user == None:
            return {"message": "User-not-found", "user": None, "result": False, }

        user.pop('_id')
        user.pop('password')
        user["qrcode"] = b64encode(user["qrcode"]).decode("ascii")
        user["profile"] = b64encode(user["profile"]).decode("ascii")

        return {"message": "User-successfully-received", "user": user, "result": True, }

    def checkId(self, _id):
        query = {'_id': _id}
        if self.__users.find_one(query) != None:
            return True
        else:
            return False

    def checkEmail(self, email):
        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
        if re.search(regex, email):
            user = self.__users.find_one({"email": email})
            if user != None:
                return {"message": "email-already-in-use",  "result": False}
            else:
                return {"message": "available-email", "result": True}
        else:
            return {"message": "invalid-email", "result": False}

    def checkUsername(self, username):
        regex = '^(?=.{3,16}$)(?![.])(?!.*[.]{2})[a-zA-Z0-9._]+(?<![.])$'
        if re.search(regex, username):
            user = self.__users.find_one({"username": username})
            if user != None:
                return {"message": "username-already-in-use",  "result": False}
            else:
                return {"message": "available-username", "result": True}

        elif re.search("(?=.{3,20}$)", username) == None:
            return {"message": "username-is-out-of-range", "result": False}
        elif re.search('^(?![.])', username) == None:
            return {"message": "dot-cannot-be-at-the-start-of-username", "result": False}
        elif re.search('(?<![.])$', username) == None:
            return {"message": "dot-cannot-be-at-the-end-of-username", "result": False}
        elif re.search('^(?!.*[.]{2})[a-zA-Z0-9._]+$', username) == None:
            return {"message": "more-than-one-point-in-row-is-not-used", "result": False}
        else:
            return {"message": "invalid-username", "result": False}

    def addAccount(self, _id, platform, account):
        data = self.getProfile("_id", _id)
        if data["result"]:
            accounts = data['user']['accounts']
            if account != None or account != '':
                accounts[platform] = account
                self.__users.update_one(
                    {"_id": _id}, {'$set': {"accounts": accounts}})
                return {"message": "account added successfully", "accounts": accounts, "result": True}
            else:
                return {"message": "account missed", "accounts": accounts, "result": False}
        else:
            data

    def deleteAccount(self, _id, platform):
        data = self.getProfile("_id", _id)
        if data["result"]:
            accounts = data['user']['accounts']
            accounts.pop(platform)
            self.__users.update_one(
                {"_id": _id}, {'$set': {"accounts": accounts}})

            return {"message": "account deleted successfully", "accounts": accounts, "result": True}
        else:
            data

    def updateAccount(self, _id, platform, account):
        data = self.getProfile("_id", _id)
        if data["result"]:
            accounts = data['user']['accounts']
            if account != None or account != '':
                accounts[platform] = account
                self.__users.update_one(
                    {"_id": _id}, {'$set': {"accounts": accounts}})
                return {"message": "account updated successfully", "accounts": accounts, "result": True}
            else:
                return {"message": "account missed", "accounts": accounts, "result": False}
        else:
            data

    def getAccounts(self, _id):
        data = self.getProfile("_id", _id)
        if data["result"]:
            accounts = data['user']['accounts']
            return {"message": "accounts received successfully", "accounts": accounts, "result": True}
        else:
            data

    def search(self, value):
        query = {"username": {"$regex": "^{}".format(value)}}
        result = self.__users.find(query)
        users = []

        for user in result:
            user.pop('_id')
            user.pop('email')
            user.pop('accounts')
            user.pop('password')
            user.pop('qrcode')
            user["profile"] = b64encode(user["profile"]).decode("ascii")
            users.append(user)

        return {"message": "Users founded with value", "users": users, "result": True}

    def addUser(self, _id, user):
        data = self.getProfile("_id", _id)
        if data["result"]:
            cards = data["user"]["cards"]
            cards.append(user)

            self.__users.update_one({"username": user}, {'$inc': {'match': 1}})
            # burada karşı tarafa bildirim göndereceksin
            return {"message": "Users added to cards", "result": True}
        else:
            data

    def getUsers(self, _id):
        data = self.getProfile("_id", _id)
        if data["result"]:
            cardsName = data["user"]["cards"]
            cards = []
            for i in cardsName:
                card = self.getProfile("username", i)
                card.pop("confirmCode")
                card.pop("isVerify")
                card.pop("qrcode")
                card.pop("cards")
                cards.append(card)
            return {"message": "All cards received", "cards": cards, "result": True}
        else:
            data

    def sendVerfCode(self, _id, email):
        confirmCode = Functions().senderEmail(email)
        confirmCode = Functions().encryptValue(confirmCode)
        query = {"_id": _id}

        value = {
            "confirmCode": confirmCode,
            "isVerify": False
        }

        self.__users.update_one(query, {'$set': value})
        return {"message": "Verification Code Sended", "result": True}

    def approveEmail(self, _id, code):
        query = {"_id":_id}
        user = self.__users.find_one(query)
        if user != None:
            confirmCode = user["confirmCode"]
            code = Functions().encryptValue(code)
            if code == confirmCode:
                self.__users.update_one({"_id": _id}, {'$set': {"isVerify": True}})
                return {"message": "Verification Code is true", "result": True}
            else:
                return {"message": "Verification Code is wrong", "result": False}
        else:
            return {"message": "Verification Code is wrong", "result": False}

class Functions():
    @classmethod
    def encryptValue(cls, value):
        encryptor = hashlib.sha256()
        encryptor.update(value.encode('utf-8'))
        return encryptor.hexdigest()

    @classmethod
    def createQR(cls, username):
        qr = qrcode.QRCode(version=4, box_size=15, border=3)
        qr.add_data('qrcard.app/'+username)
        qr.make(fit=True)
        qr = qr.make_image(fill='black', back_color="white")
        qr.save("QRCard/images/{}.jpg".format(username))
        qr = open("QRCard/images/{}.jpg".format(username), "rb").read()
        os.remove("QRCard/images/{}.jpg".format(username))

        return qr

    @classmethod
    def createId(cls, chars=string.ascii_uppercase + string.digits, N=10):
        return ''.join(random.choice(chars) for _ in range(N))

    @classmethod
    def senderEmail(cls, email):
        config = readTxt()
        receiverEmail = email
        randomCode = ''
        for i in range(6):
            randomCode += str(random.randint(0, 9))

        subject = 'QRCard Verification Code'
        body = 'Your Verification Code is ' + randomCode
        msg = f'Subject: {subject}\n\n{body}'

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(config['SENDER_EMAIL_ACCOUNT'],
                       config['SENDER_EMAIL_PASSWORD'])
            smtp.sendmail(
                config['SENDER_EMAIL_ACCOUNT'], receiverEmail, msg)

        return randomCode
