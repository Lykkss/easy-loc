from pymongo.collection import Collection
from db.mongodb.schemas import VehicleSchema

class VehicleDAO:
    def __init__(self, collection: Collection):
        self.collection = collection

    def create_vehicle(self, vehicle: VehicleSchema):
        self.collection.insert_one(vehicle.model_dump())

    def update_vehicle(self, uid: str, updates: dict):
        self.collection.update_one({"uid": uid}, {"$set": updates})

    def delete_vehicle(self, uid: str):
        self.collection.delete_one({"uid": uid})

    def find_by_licence_plate(self, plate: str):
        return self.collection.find_one({"licence_plate": plate})

    def count_by_km(self, threshold: int, more_than=True):
        op = "$gt" if more_than else "$lt"
        return self.collection.count_documents({"km": {op: threshold}})
