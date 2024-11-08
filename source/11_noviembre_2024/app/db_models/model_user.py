from mongoengine import Document, StringField, ListField, ReferenceField, EmailField, DoesNotExist, ValidationError

# Modelo de Usuario
class User(Document):
    username = StringField(required=True, max_length=50, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, min_length=8)
    api_keys = ListField(ReferenceField('APIKey'))  # Añade esta línea

# CRUD Functions
def create_user(username, email, password):
    try:
        if User.objects(username=username).first() or User.objects(email=email).first():
            return False
        new_user = User(username=username, email=email, password=password)
        new_user.save()
        return True
    except ValidationError:
        return False

def get_user_by_username(username):
    try:
        return User.objects.get(username=username)
    except DoesNotExist:
        return None

def update_user(username, new_email=None, new_password=None):
    try:
        user = User.objects.get(username=username)
        if new_email:
            if User.objects(email=new_email).first():
                return False
            user.update(set__email=new_email)
        if new_password:
            user.update(set__password=new_password)
        return True
    except DoesNotExist:
        return False

def delete_user(username):
    try:
        user = User.objects.get(username=username)
        user.delete()
        return True
    except DoesNotExist:
        return False
