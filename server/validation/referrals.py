from typing import Optional
from validation.validate import required_keys_present, values_correct_type


def validate(request_body: dict) -> Optional[str]:
    """
    Returns an error message if the /api/referrals post request
    is not valid. Else, returns None.

    :param request_body: The request body as a dict object
                        {
                            "comment": "here is a comment",
                            "readingId": "e90c0529-74ad-41b4-876e-d8e5ac60e786",
                            "referralHealthFacilityName": "H0000",
                        }
    :return: An error message if request body in invalid in some way. None otherwise.
    """
    error_message = None

    error_message = required_keys_present(
        request_body,
        [
            "referralHealthFacilityName",
        ],
    )

    if error_message is not None:
        return error_message

    all_fields = [
        "comment",
        "patientId",
        "referralHealthFacilityName",
    ]

    for key in request_body:
        if key not in all_fields:
            return "The key '" + key + "' is not a valid field or is set server-side"

    return error_message


def validate_cancel_put_request(request_body: dict) -> Optional[str]:
    """
    Returns an error message if the /api/referrals/cancel-status-switch/<int:referral_id> PUT
    request is not valid. Else, returns None.

    :param request_body: The request body as a dict object

    :return: An error message if request body is invalid in some way. None otherwise.
    """
    record_keys = [
        "isCancelled",
        "cancelReason",
        "base"
    ]

    for key in request_body:
        if key not in record_keys:
            return f"{key} is not a valid key in referral request."
        else:
            record_keys.remove(key)

    if len(record_keys) and record_keys != ["base"]:
        return f"There are missing fields for the request body."

    error = values_correct_type(request_body, ["isCancelled"], bool)
    if error:
        return error

    error = values_correct_type(request_body, ["cancelReason"], str)
    if error:
        return error
    
    # check base field if this field is contained
    if not len(record_keys):
        error = values_correct_type(request_body, ["base"], int)
        if error:
            return error



def validate_not_attend_put_request(request_body: dict) -> Optional[str]:
    """
    Returns an error message if the /api/referrals/not-attend/<int:referral_id> PUT
    request is not valid. Else, returns None.

    :param request_body: The request body as a dict object

    :return: An error message if request body is invalid in some way. None otherwise.
    """
    record_keys = [
        "notAttendReason",
    ]

    for key in request_body:
        if key not in record_keys:
            return f"{key} is not a valid key in referral request."
        else:
            record_keys.remove(key)

    if len(record_keys) > 0:
        return f"There are missing fields for the request body."

    error = values_correct_type(request_body, ["notAttendReason"], str)
    if error:
        return error
