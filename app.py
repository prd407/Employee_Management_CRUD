from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
app = Flask(__name__)
app.debug = True
app.config["MONGO_URI"] = "mongodb+srv://pradeep:DPrGbZ0hDDPnH8SJ@cluster0.jb1rloa.mongodb.net/access_control?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user_id = mongo.db.users.insert_one(data).inserted_id
    user = mongo.db.users.find_one({'_id': user_id})
    return jsonify({'success': 'User added',
                    'user':{'id': str(user['_id']), 'name': user['name'], 'email': user['email']}})

# List all users in the system
@app.route('/users', methods=['GET'])
def get_users():
    name = request.args.get('name', None)
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))

    if name:
        users = mongo.db.users.find({'name': {'$regex': name, '$options': 'i'}}).skip(offset).limit(limit)
        total_count = mongo.db.users.count_documents({'name': {'$regex': name, '$options': 'i'}})
    else:
        users = mongo.db.users.find().skip(offset).limit(limit)
        total_count = mongo.db.users.count_documents({})

    users_list = []
    for user in users:
        users_list.append({'id': str(user['_id']), 'name': user['name'], 'email': user['email']})

    return jsonify({'total_count': total_count, 'users': users_list})

# Fetch a single user
@app.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user:
        return jsonify({'user':{'id': str(user['_id']), 'name': user['name'], 'email': user['email']}})
    else:
        return  jsonify({'error': "user not found"})

# Create a new organisation
@app.route('/organisations', methods=['POST'])
def create_organisation():
    data = request.json
    organisation_id = mongo.db.organisations.insert_one(data).inserted_id
    organisation = mongo.db.organisations.find_one({'_id': organisation_id})
    return jsonify({'success': 'Organisation added',
                    'organisation': {'id': str(organisation['_id']), 'name': organisation['name']}})

# List an organisation
@app.route('/organisations', methods=['GET'])
def get_organisations():
    name = request.args.get('name', None)
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))

    if name:
        organisations = mongo.db.organisations.find({'name': {'$regex': name, '$options': 'i'}}).skip(offset).limit(limit)
        total_count = mongo.db.organisations.count_documents({'name': {'$regex': name, '$options': 'i'}})
    else:
        organisations = mongo.db.organisations.find().skip(offset).limit(limit)
        total_count = mongo.db.organisations.count_documents({})

    organisations_list = []
    for organisation in organisations:
        organisations_list.append({'id': str(organisation['_id']), 'name': organisation['name']})

    return jsonify({'total_count': total_count, 'organisations': organisations_list})

# Create/update permissions for users on each organisation
@app.route('/permissions', methods=['POST'])
def create_or_update_permissions():
    # Get the request data
    data = request.json
    
    # Validate the request data
    if 'user_id' not in data or 'organisation_id' not in data or 'access_level' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Check if the user and organisation exist in the database
    if not mongo.db.users.find_one({'_id': ObjectId(data['user_id'])}) or not mongo.db.organisations.find_one({'_id': ObjectId(data['organisation_id'])}):
        return jsonify({'error': 'User or Organisation not found'}), 404
    
    # Create or update the permission record
    permission = {
        'user_id': ObjectId(data['user_id']),
        'organisation_id': ObjectId(data['organisation_id']),
        'access_level': data['access_level']
    }
    mongo.db.permissions.replace_one({'user_id': permission['user_id'], 'organisation_id': permission['organisation_id']}, permission, upsert=True)
    
    # Return the success response
    return jsonify({'success': 'Permission added',
                    'permission': {'user_id': str(permission['user_id']), 'organisation_id': str(permission['organisation_id']), 'access_level': permission['access_level']}
                    })

# API to remove permissions for a user on an organisation
@app.route('/permissions', methods=['DELETE'])
def remove_permissions():
    # Get the request data
    data = request.json
    
    # Validate the request data
    if 'user_id' not in data or 'organisation_id' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Check if the permission record exists in the database
    permission =  mongo.db.permissions.find_one({'user_id': ObjectId(data['user_id']), 'organisation_id': ObjectId(data['organisation_id'])})
    if not permission:
        return jsonify({'error': 'Permission record not found'}), 404
    
    # Delete the permission record
    mongo.db.permissions.delete_one({'_id': ObjectId(permission['_id'])})
    
    # Return the success response
    return jsonify({'success': 'Permission record deleted'})



if __name__ == '__main__':
    app.run(debug=True)
