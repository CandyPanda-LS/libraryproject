import motor.motor_asyncio

MONGO_DETAILS = "mongodb+srv://root:root@cluster0.uav972i.mongodb.net/?retryWrites=true&w=majority"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.booklibrary
user_collection = database.get_collection("user")
book_collection = database.get_collection("book")