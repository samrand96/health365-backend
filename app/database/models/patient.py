from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Patient(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    age = fields.IntField()
    gender = fields.CharField(max_length=50)
    address = fields.CharField(max_length=100)
    email = fields.CharField(max_length=50, unique=True)
    phone_number = fields.CharField(max_length=13, unique=True)
    status = fields.CharField(max_length=50)

    doctor = fields.ForeignKeyField('models.User', related_name='patients')


Patient_Pydantic = pydantic_model_creator(Patient, name='Patient')
PatientIn_Pydantic = pydantic_model_creator(Patient, name='PatientIn', exclude_readonly=True)
