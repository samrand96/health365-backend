from typing import List
from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import Q
from app.database.models.patient import Patient_Pydantic, Patient, MedicalRecord, MedicalRecord_Pydantic, \
    MedicalRecordIn_Pydantic, PatientIn_Pydantic, PatientDoctor, PatientDoctor_Pydantic
from app.helpers.security import has_permission
from app.database.models.user import UserRole, User, User_Pydantic

router = APIRouter()


@router.get("/patients", response_model=list[Patient_Pydantic])
async def get_patients():
    try:
        patients = await Patient.all()
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/patients", response_model=Patient_Pydantic)
async def create_patient(patient: PatientIn_Pydantic):
    try:
        new_patient = await Patient.create(**patient.dict(exclude_unset=True))
        return new_patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients/{patient_id}", response_model=Patient_Pydantic)
async def get_patient(patient_id: int):
    try:
        patient = await Patient.get(id=patient_id)
        return patient
    except Exception as e:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.put("/patients/{patient_id}", response_model=Patient_Pydantic)
async def update_patient(patient_id: int, patient: PatientIn_Pydantic):
    try:
        existing_patient = await Patient.get(id=patient_id)
        await existing_patient.update_from_dict(patient.dict(exclude_unset=True))
        return await Patient_Pydantic.from_tortoise_orm(existing_patient)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: int):
    try:
        patient = await Patient.get(id=patient_id)
        await patient.delete()
        return {"message": "Patient deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.post("/patients/{patient_id}/assign-doctor/{doctor_id}", response_model=PatientDoctor_Pydantic)
async def assign_doctor_to_patient(patient_id: int, doctor_id: int):
    try:
        patient = await Patient.get(id=patient_id)
        existing_assignment = await PatientDoctor.filter(patient=patient, doctor_id=doctor_id)
        if existing_assignment:
            raise HTTPException(status_code=400, detail="Doctor is already assigned to this patient")
        assignment = await PatientDoctor.create(patient=patient, doctor_id=doctor_id)
        return assignment
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/patients/{patient_id}/assigned-doctors", response_model=list[User_Pydantic])
async def get_assigned_doctors(patient_id: int):
    try:
        assigned_doctors = await PatientDoctor.filter(patient_id=patient_id)
        doctor_ids = [assigned_doctor.doctor_id for assigned_doctor in assigned_doctors]
        doctors = await User.filter(id__in=doctor_ids)
        return doctors
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/patients/{patient_id}/unassign-doctor/{doctor_id}")
async def unassign_doctor_from_patient(patient_id: int, doctor_id: int):
    try:
        assignment = await PatientDoctor.get(patient_id=patient_id, doctor_id=doctor_id)
        await assignment.delete()
        return {"message": "Doctor unassigned successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/patients/{patient_id}/medical-information", response_model=list[MedicalRecord_Pydantic])
async def get_patient_medical_information(patient_id: int):
    try:
        patient = await Patient.get(id=patient_id)
        medical_records = await MedicalRecord.filter(patient=patient)
        return medical_records
    except Exception as e:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.post("/patients/{patient_id}/medical-information", response_model=MedicalRecord_Pydantic)
async def create_medical_record(patient_id: int, medical_record: MedicalRecordIn_Pydantic):
    try:
        patient = await Patient.get(id=patient_id)
        doctor_id = medical_record.dict().get("doctor")
        doctor = await User.get(id=doctor_id)
        new_medical_record = await MedicalRecord.create(patient=patient, doctor=doctor,
                                                        **medical_record.dict(exclude_unset=True))
        return new_medical_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/patients/{patient_id}/medical-information/{record_id}", response_model=MedicalRecord_Pydantic)
async def update_medical_record(patient_id: int, record_id: int, medical_record: MedicalRecordIn_Pydantic):
    try:
        patient = await Patient.get(id=patient_id)
        record = await MedicalRecord.get(id=record_id, patient=patient)
        await record.update_from_dict(medical_record.dict(exclude_unset=True))
        return await MedicalRecord_Pydantic.from_tortoise_orm(record)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Patient or medical record not found")


@router.delete("/patients/{patient_id}/medical-information/{record_id}")
async def delete_medical_record(patient_id: int, record_id: int):
    try:
        patient = await Patient.get(id=patient_id)
        record = await MedicalRecord.get(id=record_id, patient=patient)
        await record.delete()
        return {"message": "Medical record deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Patient or medical record not found")
