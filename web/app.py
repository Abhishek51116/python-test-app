from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]

class Register(Resource):
    def post(self):
        #Get posted data by the users
        postedData = request.get_json()

        #Get the Data
        username = postedData["username"]
        password = postedData["password"] #not good to store as raw data

        #hash(password + salt) = gibrish
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #store username and passwornd in Database
        users.insert({
        "Username": username,
        "Password": hashed_pw,
        "Sentence": "",
        "Tokens":6
        })

        retJson = {
        "status":200,
        "msg":"You successfully signed up for the API"
        }
        return jsonify(retJson)

def verifyPw(username, password):
    hashed_pw = users.find({
        "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
    "Username":username
    })[0]["Tokens"]
    return tokens

class Store(Resource):
    def post(self):
        #get the posted Data
        postedData = request.get_json()

        #read  the Data
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        #verify the uername and password match
        correct_pw = verifyPw(username,password)

        if not correct_pw:
            retJson ={
            "status":302
            }
            return jsonify(retJson)

        #Verify thast user has enough tokens
        num_tokens = countTokens(username)
        if num_tokens<=0:
            retJson = {
            "status":301,
            "msg":"Not Enough tokens"
            }
            return jsonify(retJson)

        #Store the sentence and take a token and return success
        users.update({
        "Username":username
        },{
           "$set":{
               "Sentence":sentence,
               "Tokens":num_tokens-1
               }
        })

        retJson = {
          "status":200,
          "msg":"Saved successfully"
        }

        return jsonify(retJson)

class Get(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        #verify the uername and password match
        correct_pw = verifyPw(username,password)

        if not correct_pw:
            retJson ={
            "status":302
            }
            return jsonify(retJson)


        #Verify thast user has enough tokens
        num_tokens = countTokens(username)
        if num_tokens<=0:
            retJson = {
            "status":301,
            "msg":"Not Enough tokens"
            }
            return jsonify(retJson)

        #make the user pay
        users.update({
        "Username":username
        },{
           "$set":{
               "Tokens":num_tokens-1
               }
        })

        sentence = users.find({
        "Username": username
        })[0]["Sentence"]

        retJson = {
        "status":200,
        "sentence":sentence
        }

        return jsonify(retJson)

api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(Get, '/get')

if __name__=="__main__":
    app.run(host='0.0.0.0')
