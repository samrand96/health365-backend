from fastapi import APIRouter, HTTPException
from app.database.models import user
from app.database.models.patient import PatientDoctor, Patient, Patient_Pydantic
from app.database.models.user import UserRole, User_Pydantic

router = APIRouter()


@router.get("/doctors", response_model=list[User_Pydantic])
async def get_doctors():
    try:
        doctors = await user.filter(role=UserRole.DOCTOR)
        return doctors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/doctors/{doctor_id}", response_model=User_Pydantic)
async def get_doctor(doctor_id: int):
    try:
        doctor = await user.get(id=doctor_id, role="Doctor")
        return doctor
    except Exception as e:
        raise HTTPException(status_code=404, detail="Doctor not found")


@router.get("/doctors/{doctor_id}/assigned-patients", response_model=list[Patient_Pydantic])
async def get_assigned_patients(doctor_id: int):
    try:
        assigned_patients = await PatientDoctor.filter(doctor_id=doctor_id)
        patient_ids = [assigned_patient.patient_id for assigned_patient in assigned_patients]
        patients = await Patient.filter(id__in=patient_ids)
        return patients
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))