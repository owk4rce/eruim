from mongoengine import Document, StringField
from mongoengine.errors import ValidationError

class TestModel(Document):
    name = StringField(
        required=True,
        error_messages={
            'required': 'My custom required message'
        }
    )


# Попробуем создать документ без name
test = TestModel()
try:
    test.save()
except ValidationError as e:
    print(e.to_dict())  # Увидим наше кастомное сообщение
