import os
from flask import Flask, request, abort
from flask_restx import Api, Resource, reqparse
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
api = Api(app)

DB_NAME = "user_ildo"
app.config["MONGO_URI"] = f"mongodb+srv://microservices:b6mfydTzI8LtBom8@microservices-2024.jsawiqj.mongodb.net/{DB_NAME}"
mongo = PyMongo(app)

parser = reqparse.RequestParser()
parser.add_argument('name', required=True, help="Name cannot be blank!")
parser.add_argument('email', required=True, help="Email cannot be blank!")
parser.add_argument('password', required=True, help="Password cannot be blank!")
parser.add_argument('role', required=True, help="Role cannot be blank!")

def abort_if_user_doesnt_exist(user_id):
    user = mongo.db.user.find_one({"_id": ObjectId(user_id)})
    if not user:
        abort(404, description=f"User {user_id} doesn't exist")

@api.route('/users')
class UserList(Resource):
    def get(self):
        users = list(mongo.db.user.find({}, {"_id": 1, "name": 1, "email": 1, "role": 1}))
        for user in users:
            user["_id"] = str(user["_id"])
        return users

    def post(self):
        args = parser.parse_args()
        user = {
            "name": args['name'],
            "email": args['email'],
            "password": args['password'],
            "role": args['role']
        }
        result = mongo.db.user.insert_one(user)
        user["_id"] = str(result.inserted_id)
        return user, 201

@api.route('/users/<string:user_id>')
class User(Resource):
    def get(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        user = mongo.db.user.find_one({"_id": ObjectId(user_id)})
        user["_id"] = str(user["_id"])
        return user

    def put(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        args = parser.parse_args()
        updated_user = {
            "name": args['name'],
            "email": args['email'],
            "password": args['password'],
            "role": args['role']
        }
        mongo.db.user.update_one({"_id": ObjectId(user_id)}, {"$set": updated_user})
        updated_user["_id"] = user_id
        return updated_user, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
