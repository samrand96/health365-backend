from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Patient(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    age = fields.IntField()
    gender = fields.CharField(max_length=50)
    address = fields.CharField(max_length=100)
    created_by = fields.ForeignKeyField('models.User', related_name='created_patients')


Patient_Pydantic = pydantic_model_creator(Patient, name='Patient')
PatientIn_Pydantic = pydantic_model_creator(Patient, name='PatientIn', exclude_readonly=True)


class MedicalRecord(Model):
    id = fields.IntField(pk=True)
    patient = fields.ForeignKeyField('models.Patient', related_name='medical_records')
    doctor = fields.ForeignKeyField('models.User', related_name='medical_records')
    description = fields.CharField(max_length=255)
    diagnosis = fields.CharField(max_length=255)
    prescription = fields.CharField(max_length=255)
    status = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)


MedicalRecord_Pydantic = pydantic_model_creator(MedicalRecord, name='MedicalRecord')
MedicalRecordIn_Pydantic = pydantic_model_creator(MedicalRecord, name='MedicalRecordIn', exclude_readonly=True)

class PatientDoctor(Model):
    id = fields.IntField(pk=True)
    patient = fields.ForeignKeyField('models.Patient', related_name='patient_doctors')
    doctor = fields.ForeignKeyField('models.User', related_name='patient_doctors')

PatientDoctor_Pydantic = pydantic_model_creator(PatientDoctor, name='PatientDoctor')
PatientDoctorIn_Pydantic = pydantic_model_creator(PatientDoctor, name='PatientDoctorIn', exclude_readonly=True)

