from pymongo import MongoClient, ASCENDING

# Create a MongoDB client
client = MongoClient("mongodb+srv://pradeep:DPrGbZ0hDDPnH8SJ@cluster0.jb1rloa.mongodb.net/?retryWrites=true&w=majority")

# Create/access the 'users' collection in the 'access_control' database
db = client['access_control']
users_collection = db['users']

# Create an index on the 'name' field for efficient filtering
users_collection.create_index([('name', ASCENDING)])

# Create/access the 'organisations' collection in the 'access_control' database
organisations_collection = db['organisations']

# Create a unique index on the 'name' field to enforce uniqueness of organisation names
organisations_collection.create_index([('name', ASCENDING)], unique=True)

# Create/access the 'permissions' collection in the 'access_control' database
permissions_collection = db['permissions']

# Create a compound index on the 'user_id' and 'organisation_id' fields for efficient filtering
permissions_collection.create_index([('user_id', ASCENDING), ('organisation_id', ASCENDING)], unique=True)
