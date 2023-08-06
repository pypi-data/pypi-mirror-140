import uuid

from bson import ObjectId

from mobio.libs.dynamic_field.models.mongo.db_manager import DBManager


class BaseModel(object):
    CREATED_TIME = "created_time"
    UPDATED_TIME = "updated_time"

    db_name = 'test'
    url_connection = None
    collection = None

    db = None

    def __init__(self, url_connection):
        self.url_connection = url_connection
        self.client_mongo = DBManager.get_instance(self.url_connection).db
        self.db_name = self.client_mongo.get_database().name

    def get_db(self, read_preference=None):
        if not self.client_mongo:
            self.client_mongo = DBManager.get_instance(self.url_connection).db
        return self.client_mongo.get_database(self.db_name).get_collection(self.collection,
                                                                           read_preference=read_preference)

    @staticmethod
    def normalize_uuid(some_uuid):
        if isinstance(some_uuid, str):
            return uuid.UUID(some_uuid)
        return some_uuid

    @staticmethod
    def normalize_object_id(some_object_id):
        if isinstance(some_object_id, str):
            return ObjectId(some_object_id)
        return some_object_id
