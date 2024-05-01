from typing import List
from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import Q
from app.database.models.patient import Patient_Pydantic, Patient
from app.helpers.security import has_permission
from app.database.models.user import UserRole

router = APIRouter()


@router.get("/patients", dependencies=[Depends(has_permission([UserRole.DOCTOR]))],
            response_model=List[Patient_Pydantic])
async def get_patients(user=Depends(has_permission(["doctor","labroto"]))):
    return await Patient_Pydantic.from_queryset(Patient.all())


@router.get("/patients/{patient_id}", dependencies=[Depends(has_permission([UserRole.DOCTOR]))],
            response_model=Patient_Pydantic)
async def get_patients(patient_id: int, user=Depends(has_permission([UserRole.DOCTOR]))):
    try:
        if user['is_admin']:
            return await Patient_Pydantic.from_queryset_single(Patient.get(id=patient_id))
        else:
            return await Patient_Pydantic.from_queryset_single(
                Patient.filter(Q(doctor_id=user['id']) & Q(id=patient_id)).first())
    except Exception as e:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.post("/patients", dependencies=[Depends(has_permission([UserRole.DOCTOR]))], response_model=Patient_Pydantic)
async def create_patient(patient: Patient_Pydantic, user=Depends(has_permission(["doctor"]))):
    if user['is_admin']:
        patient_obj = await Patient.create(**patient.dict(exclude_unset=True))
    else:
        patient_obj = await Patient.create(**patient.dict(exclude_unset=True), doctor_id=user['id'])
    return await Patient_Pydantic.from_tortoise_orm(patient_obj)


@router.delete("/patients/{patient_id}", dependencies=[Depends(has_permission([UserRole.DOCTOR]))])
async def delete_patient(patient_id: int, user=Depends(has_permission(["admin", "doctor"]))):
    if user['is_admin']:
        patient = await Patient.get(id=patient_id)
    else:
        patient = await Patient.get(Q(doctor_id=user['id']) & Q(id=patient_id))
    if patient:
        await patient.delete()
        return {"message": "Patient deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.put("/patients/{patient_id}", dependencies=[Depends(has_permission([UserRole.DOCTOR]))],
            response_model=Patient_Pydantic)
async def update_patient(patient_id: int, patient: Patient_Pydantic, user=Depends(has_permission(["admin", "doctor"]))):
    if user['is_admin']:
        patient_obj = await Patient.get(id=patient_id)
    else:
        patient_obj = await Patient.get(Q(doctor_id=user['id']) & Q(id=patient_id))
    if patient_obj:
        await patient_obj.update_from_dict(patient.dict(exclude_unset=True))
        await patient_obj.save()
        return await Patient_Pydantic.from_tortoise_orm(patient_obj)
    else:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.post("/patients/{patient_id}/assign-doctor/{doctor_id}",
             dependencies=[Depends(has_permission([UserRole.DOCTOR]))], response_model=Patient_Pydantic)
async def assign_doctor(patient_id: int, doctor_id: int, user=Depends(has_permission(["admin", "doctor"]))):
    try:
        if user['is_admin']:
            patient_obj = await Patient.get(id=patient_id)
        else:
            patient_obj = await Patient.get(Q(doctor_id=user['id']) & Q(id=patient_id))
        if patient_obj:
            patient_obj.doctor_id = doctor_id
            await patient_obj.save()
            return await Patient_Pydantic.from_tortoise_orm(patient_obj)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Either doctor or patient not found or your don't have permission "
                                                    "to operate the following action")


@router.post("/patients/{patient_id}/share-info/{doctor_id}",
             dependencies=[Depends(has_permission(["admin", "doctor"]))], response_model=Patient_Pydantic)
async def share_info(patient_id: int, doctor_id: int, user=Depends(has_permission(["admin", "doctor"]))):
    try:
        if user['is_admin']:
            patient_obj = await Patient.get(id=patient_id)
        else:
            patient_obj = await Patient.get(Q(doctor_id=user['id']) & Q(id=patient_id))
        if patient_obj:
            patient_obj.doctor_id = doctor_id
            await patient_obj.save()
            return await Patient_Pydantic.from_tortoise_orm(patient_obj)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Either doctor or patient not found or your don't have permission "
                                                    "to operate the following action")


@router.get("/patients/medical-record/{patient_id}", dependencies=[Depends(has_permission(["admin", "doctor"]))])
async def get_medical_record(patient_id: int, user=Depends(has_permission(["admin", "doctor"]))):
    try:
        if user['is_admin']:
            patient_obj = await Patient.get(id=patient_id)
        else:
            patient_obj = await Patient.get(Q(doctor_id=user['id']) & Q(id=patient_id))
        if patient_obj:
            return patient_obj.medical_record
    except Exception as e:
        raise HTTPException(status_code=404, detail="Either doctor or patient not found or your don't have permission "
                                                    "to operate the following action")
