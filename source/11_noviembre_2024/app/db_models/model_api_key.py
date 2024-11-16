from mongoengine import Document, StringField, ReferenceField

class APIKey(Document):
    user = ReferenceField('User', required=True)  
    api_key = StringField(required=True)
    broker = StringField(required=True)
