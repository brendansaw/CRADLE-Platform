import enum

from jsonschema import validate
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError
from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import fields
import marshmallow
import json

from config import db, ma
from utils import get_current_time, get_uuid


# To add a table to db, make a new class
# create a migration: flask db migrate
# apply the migration: flask db upgrade

#
# ENUMS CLASSES
#


class RoleEnum(enum.Enum):
    VHT = "VHT"
    HCW = "HCW"
    ADMIN = "ADMIN"
    CHO = "CHO"


class SexEnum(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class GestationalAgeUnitEnum(enum.Enum):
    MONTHS = "MONTHS"
    WEEKS = "WEEKS"


class TrafficLightEnum(enum.Enum):
    NONE = "NONE"
    GREEN = "GREEN"
    YELLOW_UP = "YELLOW_UP"
    YELLOW_DOWN = "YELLOW_DOWN"
    RED_UP = "RED_UP"
    RED_DOWN = "RED_DOWN"


class FacilityTypeEnum(enum.Enum):
    HCF_2 = "HCF_2"
    HCF_3 = "HCF_3"
    HCF_4 = "HCF_4"
    HOSPITAL = "HOSPITAL"


class QuestionTypeEnum(enum.Enum):
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    STRING = "STRING"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    MULTIPLE_SELECT = "MULTIPLE_SELECT"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    CATEGORY = "CATEGORY"


class QRelationalEnum(enum.Enum):
    LARGER_THAN = "LARGER_THAN"
    SMALLER_THAN = "SMALLER_THAN"
    EQUAL_TO = "EQUAL_TO"
    CONTAINS = "CONTAINS"


#
# HELPER CLASSES
#


supervises = db.Table(
    "supervises",
    db.Column(
        "choId", db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), index=True
    ),
    db.Column("vhtId", db.Integer, db.ForeignKey("user.id", ondelete="CASCADE")),
    db.UniqueConstraint("choId", "vhtId", name="unique_supervise"),
)


#
# MODEL CLASSES
#


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(25))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String(50))

    # FOREIGN KEYS
    healthFacilityName = db.Column(
        db.String(50), db.ForeignKey("healthfacility.healthFacilityName"), nullable=True
    )

    # RELATIONSHIPS
    healthFacility = db.relationship(
        "HealthFacility", backref=db.backref("users", lazy=True)
    )

    referrals = db.relationship("Referral", backref=db.backref("users", lazy=True))
    vhtList = db.relationship(
        "User",
        secondary=supervises,
        primaryjoin=id == supervises.c.choId,
        secondaryjoin=id == supervises.c.vhtId,
    )

    @staticmethod
    def schema():
        return UserSchema

    def __repr__(self):
        return "<User {}>".format(self.username)


class Referral(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=get_uuid)
    dateReferred = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
    )
    comment = db.Column(db.Text)
    actionTaken = db.Column(db.Text)
    isAssessed = db.Column(db.Boolean, nullable=False, default=0)
    isCancelled = db.Column(db.Boolean, nullable=False, default=0)
    cancelReason = db.Column(db.Text)
    notAttended = db.Column(db.Boolean, nullable=False, default=0)
    notAttendReason = db.Column(db.Text)
    lastEdited = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )

    # FOREIGN KEYS
    userId = db.Column(db.Integer, db.ForeignKey("user.id"))
    patientId = db.Column(db.String(50), db.ForeignKey("patient.patientId"))
    referralHealthFacilityName = db.Column(
        db.String(50), db.ForeignKey("healthfacility.healthFacilityName")
    )

    # RELATIONSHIPS
    healthFacility = db.relationship(
        "HealthFacility", backref=db.backref("referrals", lazy=True)
    )
    patient = db.relationship(
        "Patient",
        backref=db.backref("referrals", cascade="all, delete-orphan", lazy=True),
    )

    @staticmethod
    def schema():
        return ReferralSchema


class HealthFacility(db.Model):
    __tablename__ = "healthfacility"
    # TODO: should probably have a unique id as primary key here, in addition to facility name
    healthFacilityName = db.Column(db.String(50), primary_key=True)
    facilityType = db.Column(db.Enum(FacilityTypeEnum))

    # Best practice would be to add column for area code + column for rest of number.
    # However, all of our facilities are in Uganda so area code does not change.
    # May want to change in the future if system if used in multiple countries
    healthFacilityPhoneNumber = db.Column(db.String(50))
    location = db.Column(db.String(50))
    about = db.Column(db.Text)
    newReferrals = db.Column(db.String(50))

    @staticmethod
    def schema():
        return HealthFacilitySchema


class Patient(db.Model):
    patientId = db.Column(db.String(50), primary_key=True)
    patientName = db.Column(db.String(50))
    patientSex = db.Column(db.Enum(SexEnum), nullable=False)
    isPregnant = db.Column(db.Boolean)
    gestationalAgeUnit = db.Column(db.Enum(GestationalAgeUnitEnum), nullable=True)
    gestationalTimestamp = db.Column(db.BigInteger)
    medicalHistory = db.Column(db.Text)
    drugHistory = db.Column(db.Text)
    allergy = db.Column(db.Text)
    zone = db.Column(db.String(20))
    dob = db.Column(db.Date)
    isExactDob = db.Column(db.Boolean)
    villageNumber = db.Column(db.String(50))
    householdNumber = db.Column(db.String(50))
    created = db.Column(db.BigInteger, nullable=False, default=get_current_time)
    lastEdited = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    @staticmethod
    def schema():
        return PatientSchema


class Reading(db.Model):
    readingId = db.Column(db.String(50), primary_key=True)
    bpSystolic = db.Column(db.Integer)
    bpDiastolic = db.Column(db.Integer)
    heartRateBPM = db.Column(db.Integer)

    symptoms = db.Column(db.Text)
    trafficLightStatus = db.Column(db.Enum(TrafficLightEnum, nullable=False))
    dateTimeTaken = db.Column(db.BigInteger)
    dateRecheckVitalsNeeded = db.Column(db.BigInteger)
    retestOfPreviousReadingIds = db.Column(db.String(100))
    isFlaggedForFollowup = db.Column(db.Boolean)

    lastEdited = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )

    # FOREIGN KEYS
    userId = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    patientId = db.Column(
        db.String(50), db.ForeignKey("patient.patientId"), nullable=False
    )

    # RELATIONSHIPS
    patient = db.relationship(
        "Patient",
        backref=db.backref("readings", cascade="all, delete-orphan", lazy=True),
    )

    def get_traffic_light(self):
        red_systolic = 160
        red_diastolic = 110
        yellow_systolic = 140
        yellow_diastolic = 90
        shock_high = 1.7
        shock_medium = 0.9

        if (
            self.bpSystolic is None
            or self.bpDiastolic is None
            or self.heartRateBPM is None
        ):
            return TrafficLightEnum.NONE.value

        shock_index = self.heartRateBPM / self.bpSystolic

        is_bp_very_high = (self.bpSystolic >= red_systolic) or (
            self.bpDiastolic >= red_diastolic
        )
        is_bp_high = (self.bpSystolic >= yellow_systolic) or (
            self.bpDiastolic >= yellow_diastolic
        )
        is_severe_shock = shock_index >= shock_high
        is_shock = shock_index >= shock_medium

        if is_severe_shock:
            traffic_light = TrafficLightEnum.RED_DOWN.value
        elif is_bp_very_high:
            traffic_light = TrafficLightEnum.RED_UP.value
        elif is_shock:
            traffic_light = TrafficLightEnum.YELLOW_DOWN.value
        elif is_bp_high:
            traffic_light = TrafficLightEnum.YELLOW_UP.value
        else:
            traffic_light = TrafficLightEnum.GREEN.value

        return traffic_light

    @staticmethod
    def schema():
        return ReadingSchema


class FollowUp(db.Model):
    __tablename__ = "followup"
    id = db.Column(db.String(50), primary_key=True, default=get_uuid)

    followupInstructions = db.Column(db.Text)
    specialInvestigations = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    medicationPrescribed = db.Column(db.Text)
    dateAssessed = db.Column(db.BigInteger, nullable=False)
    followupNeeded = db.Column(db.Boolean)

    # FOREIGN KEYS
    healthcareWorkerId = db.Column(db.ForeignKey(User.id), nullable=False)
    patientId = db.Column(
        db.String(50), db.ForeignKey("patient.patientId"), nullable=False
    )

    # RELATIONSHIPS
    healthcareWorker = db.relationship(User, backref=db.backref("followups", lazy=True))
    patient = db.relationship(
        "Patient",
        backref=db.backref("followups", cascade="all, delete-orphan", lazy=True),
    )

    @staticmethod
    def schema():
        return FollowUpSchema


class Village(db.Model):
    villageNumber = db.Column(db.String(50), primary_key=True)
    zoneNumber = db.Column(db.String(50))


class UrineTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    urineTestLeuc = db.Column(db.String(5))
    urineTestNit = db.Column(db.String(5))
    urineTestGlu = db.Column(db.String(5))
    urineTestPro = db.Column(db.String(5))
    urineTestBlood = db.Column(db.String(5))

    # FOREIGN KEYS
    readingId = db.Column(db.ForeignKey("reading.readingId", ondelete="CASCADE"))

    # RELATIONSHIPS
    reading = db.relationship(
        Reading,
        backref=db.backref(
            "urineTests", lazy=True, uselist=False, cascade="all, delete-orphan"
        ),
    )

    @staticmethod
    def schema():
        return UrineTestSchema


class PatientAssociations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patientId = db.Column(
        db.ForeignKey(Patient.patientId, ondelete="CASCADE"),
        nullable=False,
    )
    healthFacilityName = db.Column(
        db.ForeignKey(HealthFacility.healthFacilityName, ondelete="CASCADE"),
        nullable=True,
    )
    userId = db.Column(db.ForeignKey(User.id, ondelete="CASCADE"), nullable=True)

    # RELATIONSHIPS
    patient = db.relationship(
        "Patient",
        backref=db.backref("associations", lazy=True, cascade="all, delete"),
    )
    healthFacility = db.relationship(
        "HealthFacility",
        backref=db.backref("associations", lazy=True, cascade="all, delete"),
    )
    user = db.relationship(
        "User",
        backref=db.backref("associations", lazy=True, cascade="all, delete"),
    )

    @staticmethod
    def schema():
        return PatientAssociationsSchema


class Pregnancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patientId = db.Column(
        db.ForeignKey(Patient.patientId, ondelete="CASCADE"),
        nullable=False,
    )
    startDate = db.Column(db.BigInteger, nullable=False)
    defaultTimeUnit = db.Column(db.Enum(GestationalAgeUnitEnum))
    endDate = db.Column(db.BigInteger, nullable=True, default=None)
    outcome = db.Column(db.Text)
    lastEdited = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )

    # RELATIONSHIPS
    patient = db.relationship(
        "Patient",
        backref=db.backref("pregnancies", cascade="all, delete-orphan", lazy=True),
    )

    @staticmethod
    def schema():
        return PregnancySchema


class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patientId = db.Column(
        db.ForeignKey(Patient.patientId, ondelete="CASCADE"),
        nullable=False,
    )
    information = db.Column(db.Text, nullable=False)
    isDrugRecord = db.Column(db.Boolean, nullable=False)
    dateCreated = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
    )
    lastEdited = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )

    # RELATIONSHIPS
    patient = db.relationship(
        "Patient",
        backref=db.backref("records", cascade="all, delete-orphan", lazy=True),
    )

    @staticmethod
    def schema():
        return MedicalRecordSchema


class FormTemplate(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=get_uuid)
    name = db.Column(db.Text, nullable=True)
    category = db.Column(db.Text, nullable=True)
    version = db.Column(db.Text, nullable=True)
    dateCreated = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
    )
    lastEdited = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )

    @staticmethod
    def schema():
        return FormTemplateSchema


class Form(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=get_uuid)
    lang = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False, default="")
    category = db.Column(db.Text, nullable=False, default="")
    patientId = db.Column(
        db.ForeignKey(Patient.patientId, ondelete="CASCADE"),
        nullable=False,
    )
    formTemplateId = db.Column(
        db.ForeignKey(FormTemplate.id, ondelete="SET NULL"),
        nullable=True,
    )
    dateCreated = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
    )
    lastEdited = db.Column(
        db.BigInteger,
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )
    lastEditedBy = db.Column(db.ForeignKey(User.id, ondelete="SET NULL"), nullable=True)

    # RELATIONSHIPS
    patient = db.relationship(
        "Patient",
        backref=db.backref("forms", cascade="all, delete", lazy=True),
    )

    @staticmethod
    def schema():
        return FormSchema


class Question(db.Model):
    """
    Question: a child model related to a form template or a form

    isBlank: true means the question is related to form template, vice versa
    questionIndex: a custom-defined question number index e.g. 1,2,3...
    visibleCondition: any json format string indicating a visible condition,
    the content logic should be handled in frontend
    e.g.
    [{
        "qid": "asdsd-123",
        "relation": "EQUAL_TO",
        "answer": {
            "value": 1
        }
    }]

    mcOptions: a json format list string indicating a list of multiple choices
    (maximum 5 options)
    e.g.
    [
        "opt1",
        "opt2",
        ... (maximum 5 answers)
    ]

    answers: a json format string indicating the answers filled by user
    e.g.
    {
        "number": 123,
        "text": "111",
        "textArray": ["opt1", "opt2"],
        "comment": "example comment"
    }
    """

    id = db.Column(db.String(50), primary_key=True, default=get_uuid)
    isBlank = db.Column(db.Boolean, nullable=False, default=0)
    questionIndex = db.Column(db.Integer, nullable=False)
    questionId = db.Column(db.Text, nullable=True)
    questionText = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False, default="")
    questionType = db.Column(db.Enum(QuestionTypeEnum), nullable=False)
    hasCommentAttached = db.Column(db.Boolean, nullable=False, default=0)
    required = db.Column(db.Boolean, nullable=False, default=0)
    units = db.Column(db.Text, nullable=True)
    visibleCondition = db.Column(db.Text, nullable=False, default="[]")
    mcOptions = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False, default="[]")
    numMin = db.Column(db.Float, nullable=True)
    numMax = db.Column(db.Float, nullable=True)
    stringMaxLength = db.Column(db.Integer, nullable=True)
    answers = db.Column(db.Text, nullable=False, default="{}")

    # FORENIGN KEYS
    categoryId = db.Column(
        db.ForeignKey("question.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    formId = db.Column(
        db.ForeignKey(Form.id, ondelete="CASCADE"),
        nullable=True,
    )
    formTemplateId = db.Column(
        db.ForeignKey(FormTemplate.id, ondelete="CASCADE"),
        nullable=True,
    )

    # RELATIONSHIPS
    categoryQuestion = db.relationship(
        "Question",
        backref=db.backref("questions", remote_side="Question.id", lazy=True),
    )
    form = db.relationship(
        "Form",
        backref=db.backref("questions", cascade="all, delete", lazy=True),
    )
    formTemplate = db.relationship(
        "FormTemplate",
        backref=db.backref("questions", cascade="all, delete", lazy=True),
    )

    @staticmethod
    def schema():
        return QuestionSchema


class QuestionLangVersion(db.Model):
    """
    This model is used to store different language versions of a single question.
    """

    id = db.Column(db.Integer, primary_key=True)
    lang = db.Column(db.Text, nullable=False)
    questionText = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False)
    mcOptions = db.Column(db.Text(collation="utf8mb4_general_ci"), nullable=False, default="[]")

    # FORENIGN KEYS
    qid = db.Column(
        db.ForeignKey(Question.id, ondelete="CASCADE"),
        nullable=False,
    )

    # RELATIONSHIPS
    question = db.relationship(
        "Question",
        backref=db.backref("lang_versions", cascade="all, delete", lazy=True),
    )

    @staticmethod
    def schema():
        return QuestionLangVersionSchema


#
# SCHEMAS
#


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = User
        load_instance = True
        include_relationships = True


class PatientSchema(ma.SQLAlchemyAutoSchema):
    patientSex = EnumField(SexEnum, by_value=True)

    class Meta:
        include_fk = True
        model = Patient
        load_instance = True
        include_relationships = True


class ReadingSchema(ma.SQLAlchemyAutoSchema):
    trafficLightStatus = EnumField(TrafficLightEnum, by_value=True)

    class Meta:
        include_fk = True
        model = Reading
        load_instance = True
        include_relationships = True


class HealthFacilitySchema(ma.SQLAlchemyAutoSchema):
    facilityType = EnumField(FacilityTypeEnum, by_value=True)

    class Meta:
        include_fk = True
        model = HealthFacility
        load_instance = True
        include_relationships = True


class FollowUpSchema(ma.SQLAlchemyAutoSchema):
    healthcareWorker = fields.Nested(UserSchema)

    class Meta:
        include_fk = True
        model = FollowUp
        load_instance = True
        include_relationships = True


class ReferralSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = Referral
        load_instance = True
        include_relationships = True


class UrineTestSchema(ma.SQLAlchemyAutoSchema):
    # urineTests = fields.Nested(ReadingSchema)
    class Meta:
        include_fk = True
        model = UrineTest
        load_instance = True
        include_relationships = True


class PatientAssociationsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = PatientAssociations
        load_instance = True
        include_relationships = True


user_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "firstName": {"type": "string"},
        "role": {"type": "string"},
        "healthFacilityName": {"type": "string"},
        "password": {"type": "string", "minLength": 5},
    },
    "required": ["email", "password"],
    "additionalProperties": False,
}


class VillageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = Village
        load_instance = True
        include_relationships = True


def validate_timestamp(ts):
    if ts > get_current_time():
        raise marshmallow.ValidationError("Date must not be in the future.")


class PregnancySchema(ma.SQLAlchemyAutoSchema):
    startDate = marshmallow.fields.Integer(validate=validate_timestamp)
    endDate = marshmallow.fields.Integer(validate=validate_timestamp)

    class Meta:
        include_fk = True
        model = Pregnancy
        load_instance = True
        include_relationships = True


class MedicalRecordSchema(ma.SQLAlchemyAutoSchema):
    dateCreated = marshmallow.fields.Integer(validate=validate_timestamp)

    class Meta:
        include_fk = True
        model = MedicalRecord
        load_instance = True
        include_relationships = True


class FormTemplateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = FormTemplate
        load_instance = True
        include_relationships = True


class FormSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = Form
        load_instance = True
        include_relationships = True


class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = Question
        load_instance = True
        include_relationships = True


class QuestionLangVersionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = QuestionLangVersion
        load_instance = True
        include_relationships = True


def validate_user(data):
    try:
        validate(data, user_schema)
    except ValidationError as e:
        return {"ok": False, "message": e}
    except SchemaError as e:
        return {"ok": False, "message": e}
    return {"ok": True, "data": data}
