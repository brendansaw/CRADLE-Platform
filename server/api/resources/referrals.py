import time
from math import floor
from flasgger import swag_from
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort

import api.util as util
import data
import data.crud as crud
import data.marshal as marshal
from utils import get_current_time
import service.assoc as assoc
import service.view as view
from models import HealthFacility, Reading, Referral
from validation import referrals
import service.serialize as serialize


# /api/referrals
class Root(Resource):
    @staticmethod
    @jwt_required
    @swag_from(
        "../../specifications/referrals-get.yml", methods=["GET"], endpoint="referrals"
    )
    def get():
        user = get_jwt_identity()

        params = util.get_query_params(request)
        if params.get("health_facilities") and "default" in params["health_facilities"]:
            params["health_facilities"].append(user["healthFacilityName"])

        referrals = view.referral_list_view(user, **params)
        return serialize.serialize_referral_list(referrals)

    @staticmethod
    @jwt_required
    @swag_from(
        "../../specifications/referrals-post.yml",
        methods=["POST"],
        endpoint="referrals",
    )
    def post():
        json = request.get_json(force=True)
        error_message = referrals.validate(json)
        if error_message is not None:
            abort(400, message=error_message)

        healthFacility = crud.read(
            HealthFacility, healthFacilityName=json["referralHealthFacilityName"]
        )

        if not healthFacility:
            abort(400, message="Health facility does not exist")
        else:
            UTCTime = str(round(time.time() * 1000))
            crud.update(
                HealthFacility,
                {"newReferrals": UTCTime},
                True,
                healthFacilityName=json["referralHealthFacilityName"],
            )

        json["userId"] = get_jwt_identity()["userId"]
        json["dateReferred"] = floor(time.time())
        json["isAssessed"] = False
        json["dateAssessed"] = None
        json["isCancelled"] = False
        json["dateCancelled"] = None

        referral = marshal.unmarshal(Referral, json)
        crud.create(referral, refresh=True)
        # Creating a referral also associates the corresponding patient to the health
        # facility they were referred to.
        patient = referral.patient
        facility = referral.healthFacility
        if not assoc.has_association(patient, facility):
            assoc.associate(patient, facility=facility)

        return marshal.marshal(referral), 201


# /api/referrals/<int:referral_id>
class SingleReferral(Resource):
    @staticmethod
    @jwt_required
    @swag_from(
        "../../specifications/single-referral-get.yml",
        methods=["GET"],
        endpoint="single_referral",
    )
    def get(referral_id: int):
        referral = crud.read(Referral, id=referral_id)
        if not referral:
            abort(404, message=f"No referral with id {id}")

        return marshal.marshal(referral)

# /api/referralAssess/<int:referral_id>
class AssessReferral(Resource):
    @staticmethod
    @jwt_required
    @swag_from(
        "../../specifications/referrals-assess-update-post.yml",
        methods=["POST"],
        endpoint="referral_assess",
    )
    def post(referral_id: int):
        referral = crud.read(Referral, id=referral_id)
        if not referral:
            abort(404, message=f'No referral with id {referral_id}')
        
        if not referral.isAssessed:
            referral.isAssessed = True
            referral.dateAssessed = get_current_time()
            data.db_session.commit()
        
        new_referral = crud.read(Referral, id=referral_id)
        return marshal.marshal(new_referral), 201

# /api/referralCancelStatus/<int:referral_id>
class ReferralCancelStatus(Resource):
    @staticmethod
    @jwt_required
    @swag_from(
        "../../specifications/referrals-cancel-update-put.yml",
        methods=["PUT"],
        endpoint="referral_cancel_status",
    )
    def put(referral_id: int):
        request_body = request.get_json(force=True)

        error = referrals.validate_put_request(request_body)
        if error:
            abort(400, message=error)
        
        request_body["dateCancelled"] = get_current_time()

        if not request_body["isCancelled"]:
            request_body["cancelReason"] = None
            request_body["dateCancelled"] = None
        
        crud.update(Referral, request_body, id=referral_id)

        new_record = crud.read(Referral, id=referral_id)

        return marshal.marshal(new_record)

        
