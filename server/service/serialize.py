"""
The ``service.util`` contains utility functions to help simplify useful information into a dict
instead of using marshal on the whole Object.
"""
from typing import Any, List, Optional, Tuple, Union

import data.marshal as marshal
from models import (
    FollowUp,
    MedicalRecord,
    Patient,
    Pregnancy,
    Reading,
    Referral,
    UrineTest,
)


def serialize_patient_list(patients: List[Any]) -> dict:
    return [
        {
            "patientId": p.patientId,
            "patientName": p.patientName,
            "villageNumber": p.villageNumber,
            "trafficLightStatus": p.trafficLightStatus.value
            if p.trafficLightStatus
            else "",
            "dateTimeTaken": p.dateTimeTaken if p.dateTimeTaken else "",
        }
        for p in patients
    ]


def serialize_referral(r: Any) -> dict:
    return {
        "referralId": r.id,
        "patientId": r.patientId,
        "patientName": r.patientName,
        "villageNumber": r.villageNumber,
        "trafficLightStatus": r.trafficLightStatus.value,
        "dateReferred": r.dateReferred,
        "isAssessed": r.isAssessed,
    }


def serialize_pregnancy(p: Pregnancy) -> dict:
    return {
        "pregnancyId": p.id,
        "startDate": p.startDate,
        "endDate": p.endDate,
        "outcome": p.outcome,
        "lastEdited": p.lastEdited,
    }


def serialize_medical_record(r: MedicalRecord) -> dict:
    return {
        "medicalRecordId": r.id,
        "information": r.information,
        "dateCreated": r.dateCreated,
        "lastEdited": r.lastEdited,
    }


def serialize_patient_timeline(r: Any) -> dict:
    return {
        "title": r.title,
        "information": r.information,
        "date": r.date,
    }


def serialize_patient(patient: Any, readings: Optional[List[Reading]] = None) -> dict:
    p = {
        "patientId": patient.patientId,
        "patientName": patient.patientName,
        "patientSex": patient.patientSex.value,
        "dob": str(patient.dob),
        "isExactDob": patient.isExactDob,
        "zone": patient.zone,
        "householdNumber": patient.householdNumber,
        "villageNumber": patient.villageNumber,
        "allergy": patient.allergy,
        "isPregnant": True if patient.pregnancyStartDate else False,
        "pregnancyId": patient.pregnancyId,
        "pregnancyStartDate": patient.pregnancyStartDate,
        "gestationalAgeUnit": patient.gestationalAgeUnit.value
        if patient.gestationalAgeUnit
        else None,
        "medicalHistoryId": patient.medicalHistoryId,
        "medicalHistory": patient.medicalHistory,
        "drugHistoryId": patient.drugHistoryId,
        "drugHistory": patient.drugHistory,
        "lastEdited": patient.lastEdited,
        "base": patient.lastEdited,
        "readings": [serialize_reading(r) for r in readings] if readings else [],
    }
    return {k: v for k, v in p.items() if v or v == False}


def serialize_reading(tup: Tuple[Reading, Referral, FollowUp, UrineTest]) -> dict:
    reading = marshal.marshal(tup[0], True)
    if tup[1]:
        reading["referral"] = marshal.marshal(tup[1])
    if tup[2]:
        reading["followup"] = marshal.marshal(tup[2])
    if tup[3]:
        reading["urineTests"] = marshal.marshal(tup[3])
    return reading


def deserialize_patient(
    data: dict, shallow: bool = True, partial: bool = False
) -> Union[dict, Patient]:
    d = {
        "patientId": data["patientId"],
        "patientName": data["patientName"],
        "patientSex": data["patientSex"],
        "dob": data["dob"],
        "isExactDob": data["isExactDob"],
        "zone": data.get("zone"),
        "villageNumber": data.get("villageNumber"),
        "householdNumber": data.get("householdNumber"),
        "allergy": data.get("allergy"),
    }
    if partial:
        return d

    patient = Patient.schema()().load(d)
    if shallow:
        return patient

    medical_records = list()
    if data.get("medicalHistory"):
        medical_records.append(deserialize_medical_record(data, False))
    if data.get("drugHistory"):
        medical_records.append(deserialize_medical_record(data, True))

    pregnancies = list()
    if data.get("pregnancyStartDate"):
        pregnancies.append(deserialize_pregnancy(data))

    if medical_records:
        patient.records = medical_records
    if pregnancies:
        patient.pregnancies = pregnancies

    return patient


def deserialize_pregnancy(data: dict, partial: bool = False) -> Union[dict, Pregnancy]:
    if partial:
        d = {
            "endDate": data["pregnancyEndDate"],
            "outcome": data.get("pregnancyOutcome"),
        }
        return {k: v for k, v in d.items() if v}

    d = {
        "patientId": data["patientId"],
        "startDate": data["pregnancyStartDate"],
        "defaultTimeUnit": data["gestationalAgeUnit"],
    }
    return Pregnancy.schema()().load(d)


def deserialize_medical_record(data: dict, is_drug_record: bool) -> MedicalRecord:
    d = {
        "patientId": data["patientId"],
        "information": data.pop("drugHistory")
        if is_drug_record
        else data.pop("medicalHistory"),
        "isDrugRecord": is_drug_record,
    }
    if data.get("medicalLastEdited") or data.get("drugLastEdited"):
        d["dateCreated"] = (
            data.pop("drugLastEdited")
            if is_drug_record
            else data.pop("medicalLastEdited")
        )
    return MedicalRecord.schema()().load(d)
