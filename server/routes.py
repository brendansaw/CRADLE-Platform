"""
    @File: routes.py
    @Description: This file contains all the routes for the server
"""

import api as new_api
from api.resources.patients_android import *
from api.resources.version import *
from api.resources.assessments import Root as Assessments, SingleAssessment
from api.resources.stats import AllStats, FacilityReadings, UserReadings, ExportStats

from api.resources.patientAssociations import Root as PatientAssociations
from api.resources.facilities import Root as Facilities, SingleFacility
from api.resources.patients import (
    Root as Patients,
    SinglePatient,
    PatientInfo,
    PatientStats,
    PatientReadings,
    PatientMostRecentReading,
    PatientReferrals,
    PatientForms,
    PatientPregnancySummary,
    PatientMedicalHistory,
    PatientTimeline,
    ReadingAssessment,
    PatientAllRecords,
    PatientsAdmin,
)
from api.resources.readings import Root as Readings, SingleReading
from api.resources.referrals import (
    Root as Referrals,
    SingleReferral,
    AssessReferral,
    ReferralCancelStatus,
    ReferralNotAttend,
)
from api.resources.pregnancies import Root as Pregnancies, SinglePregnancy
from api.resources.medicalRecords import Root as MedicalRecords, SingleMedicalRecord
from api.resources.formTemplates import (
    Root as FormTemplate,
    FormTemplateResource,
    BlankFormTemplate,
    TemplateVersion,
    TemplateVersionCsv,
)
from api.resources.formClassifications import (
    Root as FormClassification,
    SingleFormClassification,
    FormClassificationSummary,
)
from api.resources.forms import Root as Forms, SingleForm
from api.resources.sms_relay import Root as SmsRelay
from api.resources.users import *
from api.resources.upload import Root as Upload


def init(api):
    api.add_resource(AllStats, "/api/stats/all")  # [GET]

    api.add_resource(
        FacilityReadings, "/api/stats/facility/<string:facility_id>"
    )  # [GET]
    api.add_resource(ExportStats, "/api/stats/export/<int:user_id>")  # [GET]

    api.add_resource(UserReadings, "/api/stats/user/<int:user_id>")

    api.add_resource(UserRegisterApi, "/api/user/register")  # [POST]
    api.add_resource(UserAuthApi, "/api/user/auth")  # [POST]
    api.add_resource(UserAuthTokenRefreshApi, "/api/user/auth/refresh_token")  # [POST]
    api.add_resource(UserTokenApi, "/api/user/current")  # [GET]
    api.add_resource(UserAll, "/api/user/all")  # [GET]

    api.add_resource(UserApi, "/api/user/<int:id>")  # [GET, PUT, DELETE]

    api.add_resource(UserAllVHT, "/api/user/vhts")  # [GET]

    api.add_resource(
        AndroidPatientGlobalSearch, "/api/patients/global/<string:search>"
    )  # [GET]
    api.add_resource(
        AndroidPatients, "/api/mobile/patients", endpoint="android_patient"
    )  # [GET]
    api.add_resource(
        AndroidReadings, "/api/mobile/readings", endpoint="android_readings"
    )  # [GET]
    api.add_resource(
        AndroidReferrals, "/api/mobile/referrals", endpoint="android_referrals"
    )  # [GET]
    api.add_resource(
        AndroidAssessments, "/api/mobile/assessments", endpoint="android_assessments"
    )  # [GET]
    api.add_resource(
        AndroidForms,
        "/api/mobile/forms/<string:patient_id>/<string:form_template_id>",
        endpoint="android_forms",
    )  # [GET]

    #### New Endpoints ####
    api.add_resource(
        Assessments, "/api/assessments", endpoint="assessment"
    )  # [POST, GET]

    api.add_resource(
        SingleAssessment,
        "/api/assessments/<string:assessment_id>",
        endpoint="single_assessment",
    )  # [GET]

    api.add_resource(
        PatientAssociations, "/api/patientAssociations", endpoint="patientAssociations"
    )  # [POST]

    api.add_resource(
        Facilities, "/api/facilities", endpoint="facilities"
    )  # [GET, POST]
    api.add_resource(
        SingleFacility,
        "/api/facilities/<string:facility_name>",
        endpoint="single_facility",
    )  # [GET]

    api.add_resource(Patients, "/api/patients", endpoint="patients")  # [GET, POST]
    api.add_resource(
        SinglePatient, "/api/patients/<string:patient_id>", endpoint="single_patient"
    )  # [GET]
    api.add_resource(
        PatientInfo, "/api/patients/<string:patient_id>/info", endpoint="patient_info"
    )  # [GET, PUT]
    api.add_resource(
        PatientStats,
        "/api/patients/<string:patient_id>/stats",
        endpoint="patient_stats",
    )  # [GET]
    api.add_resource(
        PatientReadings,
        "/api/patients/<string:patient_id>/readings",
        endpoint="patient_readings",
    )  # [GET]
    api.add_resource(
        PatientMostRecentReading,
        "/api/patients/<string:patient_id>/most_recent_reading",
        endpoint="patient_most_recent_reading",
    )  # [GET]
    api.add_resource(
        PatientReferrals,
        "/api/patients/<string:patient_id>/referrals",
        endpoint="patient_referrals",
    )  # [GET]
    api.add_resource(
        PatientForms,
        "/api/patients/<string:patient_id>/forms",
        endpoint="patient_forms",
    )  # [GET]
    api.add_resource(
        PatientPregnancySummary,
        "/api/patients/<string:patient_id>/pregnancy_summary",
        endpoint="patient_pregnancy_summary",
    )  # [GET]
    api.add_resource(
        PatientMedicalHistory,
        "/api/patients/<string:patient_id>/medical_history",
        endpoint="patient_medical_history",
    )  # [GET]
    api.add_resource(
        PatientTimeline,
        "/api/patients/<string:patient_id>/timeline",
        endpoint="patient_timeline",
    )  # [GET]
    api.add_resource(
        ReadingAssessment,
        "/api/patients/reading-assessment",
        endpoint="reading_assessment",
    )  # [POST]
    api.add_resource(
        PatientAllRecords,
        "/api/patients/<string:patient_id>/get_all_records",
        endpoint="patient_get_all_records",
    )  # [GET]
    api.add_resource(
        PatientsAdmin, "/api/patients/admin", endpoint="patients_admin"
    )  # [GET]

    api.add_resource(Readings, "/api/readings", endpoint="readings")  # [POST]
    api.add_resource(
        SingleReading, "/api/readings/<string:reading_id>", endpoint="single_reading"
    )  # [GET]

    api.add_resource(Referrals, "/api/referrals", endpoint="referrals")  # [GET, POST]
    api.add_resource(
        SingleReferral, "/api/referrals/<int:referral_id>", endpoint="single_referral"
    )  # [GET]
    api.add_resource(
        AssessReferral,
        "/api/referrals/assess/<string:referral_id>",
        endpoint="referral_assess",
    )  # [PUT]
    api.add_resource(
        ReferralCancelStatus,
        "/api/referrals/cancel-status-switch/<string:referral_id>",
        endpoint="referral_cancel_status",
    )  # [PUT]
    api.add_resource(
        ReferralNotAttend,
        "/api/referrals/not-attend/<string:referral_id>",
        endpoint="referral_not_attend",
    )  # [PUT]

    api.add_resource(
        Pregnancies,
        "/api/patients/<string:patient_id>/pregnancies",
        endpoint="pregnancies",
    )  # [GET, POST]
    api.add_resource(
        SinglePregnancy,
        "/api/pregnancies/<string:pregnancy_id>",
        endpoint="single_pregnancy",
    )  # [GET, PUT, DELETE]

    api.add_resource(
        MedicalRecords,
        "/api/patients/<string:patient_id>/medical_records",
        endpoint="medical_records",
    )  # [GET, POST]
    api.add_resource(
        SingleMedicalRecord,
        "/api/medical_records/<string:record_id>",
        endpoint="single_medical_record",
    )  # [GET, PUT, DELETE]

    api.add_resource(
        FormTemplate, "/api/forms/templates", endpoint="form_templates"
    )  # [GET, POST]
    api.add_resource(
        FormTemplateResource,
        "/api/forms/templates/<string:form_template_id>",
        endpoint="single_form_template",
    )  # [GET, PUT]
    api.add_resource(
        TemplateVersion,
        "/api/forms/templates/<string:form_template_id>/versions",
        endpoint="single_form_template_version",
    )  # [GET]
    api.add_resource(
        TemplateVersionCsv,
        "/api/forms/templates/<string:form_template_id>/versions/<string:version>/csv",
        endpoint="single_form_template_csv",
    )  # [GET, PUT]
    api.add_resource(
        BlankFormTemplate,
        "/api/forms/templates/blank/<string:form_template_id>",
        endpoint="blank_form_template",
    )  # [GET]

    api.add_resource(
        FormClassification,
        "/api/forms/classifications",
        endpoint="form_classifications",
    )  # [GET, POST]
    api.add_resource(
        SingleFormClassification,
        "/api/forms/classifications/<string:form_classification_id>",
        endpoint="single_form_classification",
    )  # [GET, PUT]
    api.add_resource(
        FormClassificationSummary,
        "/api/forms/classifications/summary",
        endpoint="form_classification_summary",
    )  # [GET]

    api.add_resource(Forms, "/api/forms/responses", endpoint="forms")  # [POST]
    api.add_resource(
        SingleForm, "/api/forms/responses/<string:form_id>", endpoint="single_form"
    )  # [GET, PUT]

    api.add_resource(AdminPasswordChange, "/api/user/<int:id>/change_pass")  # [POST]
    api.add_resource(UserPasswordChange, "/api/user/current/change_pass")  # [POST]

    api.add_resource(Version, "/api/version")  # [GET]

    api.add_resource(
        Upload, "/api/upload/admin", endpoint="upload_admin"
    )  # [GET, POST]

    api.add_resource(SmsRelay, "/api/sms_relay", endpoint="sms_relay")  # [GET, PUT]

    new_api.init_routes(api)
