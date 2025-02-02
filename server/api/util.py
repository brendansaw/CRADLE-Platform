from __future__ import annotations
import json
import pprint

"""
The ``api.util`` module contains utility functions to help extract useful information
from requests.
"""

import csv
from functools import reduce
from typing import Callable, Iterable, Type

import data.crud as crud
import data.marshal as marshal
import flask_jwt_extended as jwt
import utils
from data.crud import M
from flask import Request
from models import (
    Form,
    FormTemplate,
    FormClassification,
    Question,
    User,
)
from enums import QuestionTypeEnum, QRelationalEnum

from api.constants import (
    FORM_TEMPLATE_LANGUAGES_COL,
    FORM_TEMPLATE_LANGUAGES_ROW,
    FORM_TEMPLATE_NAME_COL,
    FORM_TEMPLATE_NAME_ROW,
    FORM_TEMPLATE_QUESTION_ID_COL,
    FORM_TEMPLATE_QUESTION_LINE_COUNT_COL,
    FORM_TEMPLATE_QUESTION_MAX_VALUE_COL,
    FORM_TEMPLATE_QUESTION_MIN_VALUE_COL,
    FORM_TEMPLATE_QUESTION_OPTIONS_COL,
    FORM_TEMPLATE_QUESTION_REQUIRED_COL,
    FORM_TEMPLATE_QUESTION_TEXT_COL,
    FORM_TEMPLATE_QUESTION_TYPE_COL,
    FORM_TEMPLATE_QUESTION_UNITS_COL,
    FORM_TEMPLATE_QUESTION_VISIBILITY_CONDITION_COL,
    FORM_TEMPLATE_ROW_LENGTH,
    FORM_TEMPLATE_VERSION_COL,
    FORM_TEMPLATE_VERSION_ROW,
)


def query_param_bool(request: Request, name: str) -> bool:
    """
    Returns true if the request URL contains a boolean query parameter with a given
    ``name`` who's value is "true".

    :param request: A request
    :param name: The name of the parameter to check for
    :return: True if the value for the parameter is "true", otherwise False.
    """
    return request.args.get(name, "false", type=str) == "true"


def query_param_limit(request: Request, name: str) -> int:
    """
    Returns Integer if the request URL contains a limit query parameter.

    :param request: A request
    :param name: The name of the parameter to check for
    :return: 10 if the value for the parameter is not specified, otherwise given value.
    """
    return request.args.get(name, 10, type=int)


def query_param_page(request: Request, name: str) -> int:
    """
    Returns Integer if the request URL contains a page query parameter.

    :param request: A request
    :param name: The name of the parameter to check for
    :return: 1 if the value for the parameter is not specified, otherwise given value.

    """
    return request.args.get(name, 1, type=int)


def query_param_sortBy(request: Request, name: str) -> str:
    """
    Returns String if the request URL contains a page sortBy parameter.

    :param request: A request
    :param name: The name of the parameter to check for
    :return: patientName if the value for the parameter is not specified, otherwise given column name.

    """
    return request.args.get(name, "patientName", type=str)


def query_param_sort_dir(request: Request, name: str) -> str:
    """
    Returns String if the request URL contains a page sortDir parameter.

    :param request: A request
    :param name: The name of the parameter to check for
    :return: asc if the value for the parameter is not specified, otherwise given column name.

    """
    return request.args.get(name, "asc", type=str)


def query_param_search(request: Request, name: str) -> str:
    """
    Returns String if the request URL contains a page sortDir parameter.

    :param request: A request
    :param name: The name of the parameter to check for
    :return: empty string if the value for the parameter is not specified, otherwise given column name.

    """
    return request.args.get(name, "", type=str)


def current_user() -> User:
    """
    Returns the the model for the user making the request.

    :return:
    """
    identity = jwt.get_jwt_identity()
    return crud.read(User, id=identity["userId"])


def isGoodPassword(password: str) -> bool:
    """
    Returns a Boolean indicating if the password inputted meets the desired characteristics or not

    :param password: The password string to evaluate
    """
    # To-Do: if anything requirments are necessary for a good password (having a number or special character
    # etc, these should be added here as well)

    passlength = False

    if len(password) >= 8:
        passlength = True

    return passlength


def filterPairsWithNone(payload: dict) -> dict:
    """
    Returns  dict with all the key-value pairs wherein the value is not None

    :param payload: The dictionary to evaluate
    """

    updated_data = {}
    for k, v in payload.items():
        if payload[k] is not None:
            updated_data[k] = v

    return updated_data


def getDictionaryOfUserInfo(id: int) -> dict:

    """
    Takes in an id and returns all of the information about a user from the users table
    and from the supervises table

    :param id: The user's id
    """

    user = crud.read(User, id=id)
    userDict = marshal.marshal(user)

    # The vhtlist has to be marshalled manually
    vhtList = []
    for user in user.vhtList:
        vhtList.append(user.id)
    userDict["supervises"] = vhtList

    userDict.pop("password")

    # Just for uniformity in the names of the keys
    userDict["userId"] = userDict["id"]
    userDict.pop("id")

    return userDict


def doesUserExist(id: int) -> bool:
    """
    Takes in id of the user and does a read to see if this user exists or not.
    :param id: The user's id

    """

    user = crud.read(User, id=id)
    if user is None:
        return False
    else:
        return True


def assign_form_or_template_ids(model: Type[M], req: dict) -> None:
    """
    Assign form id if not provided.
    Assign question id and formId or formTemplateId.
    Assign lang version qid.
    Therefore, we can create the form or template one time.
    """
    if req.get("classification") is not None:
        if req.get("classification").get("id") is None:
            req["classification"]["id"] = utils.get_uuid()
        if req.get("formClassificationId") is None:
            req["formClassificationId"] = req.get("classification").get("id")

    # assign form id if not provided.
    if req.get("id") is None:
        req["id"] = utils.get_uuid()

    id = req["id"]

    if model is FormClassification:
        return

    # assign question id and formId or formTemplateId.
    # assign lang version qid.
    for question in req.get("questions"):
        question["id"] = utils.get_uuid()

        if model is Form:
            question["formId"] = id
        elif model is FormTemplate:
            question["formTemplateId"] = id

        if question.get("questionLangVersions") is not None:
            for version in question.get("questionLangVersions"):
                version["qid"] = question["id"]


def get_query_params(request: Request) -> dict:
    """
    Extracts URL search params contained in the request.

    :param request: Flask request object

    :return: URL search params stored in a dictionary
    """
    params = {
        "search_text": request.args.get("search"),
        "order_by": request.args.get("sortBy"),
        "direction": request.args.get("sortDir"),
        "limit": request.args.get("limit"),
        "page": request.args.get("page"),
        "date_range": request.args.get("dateRange"),
        "readings": request.args.get("readings"),
        "referrals": request.args.get("referrals"),
        "assessments": request.args.get("assessments"),
        "forms": request.args.get("forms"),
        "lang": request.args.get("lang"),
        "is_assessed": request.args.get("isAssessed"),
        "is_pregnant": request.args.get("isPregnant"),
        "include_archived": request.args.get("includeArchived"),
        "vital_signs": list(filter(None, request.args.getlist("vitalSigns"))),
        "referrers": list(filter(None, request.args.getlist("referrer"))),
        "health_facilities": list(filter(None, request.args.getlist("healthFacility"))),
    }

    return {k: v for k, v in params.items() if v}


def parseCondition(parentQuestion: dict, conditionText: str) -> dict:
    """
    Returns a condition based on the parent question and the conditionText

    :param parentQuestion: The question the conditionText should be compared against
    :param conditionText: The text to be compared to the value of the parent question

    :return: Condition dictionary with the parent question ID and a valid answers object
    """
    mcOptionsToDict: Callable[[list[dict]], dict[str, int]] = lambda mcOptions: {
        option["opt"].casefold(): option["mcid"] for option in mcOptions
    }

    condition: dict[str, any] = {
        "qidx": parentQuestion["questionIndex"],
        "relation": QRelationalEnum.EQUAL_TO.value,
        "answers": {},
    }

    if parentQuestion["questionType"] == QuestionTypeEnum.CATEGORY:
        raise RuntimeError("Question visibility cannot depend on a category")

    if parentQuestion["questionType"] in [
        QuestionTypeEnum.MULTIPLE_CHOICE.value,
        QuestionTypeEnum.MULTIPLE_SELECT.value,
    ]:

        options = [option.strip().casefold() for option in conditionText.split(",")]

        previousQuestionOptions = mcOptionsToDict(
            parentQuestion["questionLangVersions"][0]["mcOptions"]
        )

        condition["answers"]["mcidArray"] = []
        for option in options:
            if option not in previousQuestionOptions.keys():
                raise RuntimeError("Invalid option for visibility.")

            condition["answers"]["mcidArray"].append(previousQuestionOptions[option])

    elif parentQuestion["questionType"] == QuestionTypeEnum.INTEGER.value:
        try:
            condition["answers"]["number"] = int(conditionText)
        except ValueError:
            raise RuntimeError("Invalid condition for parent question of type Integer")

    elif parentQuestion["questionType"] == QuestionTypeEnum.DECIMAL.value:
        try:
            condition["answers"]["number"] = float(conditionText)
        except ValueError:
            raise RuntimeError("Invalid condition for parent question of type Integer")

    else:
        condition["answers"]["text"] = int(conditionText)

    return condition


def getFormTemplateDictFromCSV(csvData: str):
    """
    Returns a dictionary of form templates from a CSV file.
    """

    # Helper functions
    def isRowEmpty(row: Iterable) -> bool:

        return all(map(lambda val: val == "", row))

    def isQuestionRequired(required: str) -> bool:
        return len(required) > 0 and required.upper()[0] == "Y"

    def toNumberOrNone(strVal: str) -> int | float | None:
        if strVal == "":
            return None

        return float(strVal) if "." in strVal else int(strVal)

    def toMcOptions(strVal: str) -> list[dict[str, int | str]]:
        return [
            {"mcid": index, "opt": opt.strip()}
            for index, opt in enumerate(strVal.split(","))
            if len(opt.strip()) > 0
        ]

    def getQuestionLanguageVersionFromRow(row: list) -> dict:
        return {
            "questionText": row[FORM_TEMPLATE_QUESTION_TEXT_COL],
            "mcOptions": toMcOptions(row[FORM_TEMPLATE_QUESTION_OPTIONS_COL]),
            "lang": row[FORM_TEMPLATE_LANGUAGES_COL].strip(),
        }

    def findCategoryIndex(
        categoryList: list[dict[str, any]], categoryText: str
    ) -> int | None:

        for category in categoryList:
            for languageVersion in category["questionLangVersions"]:
                if languageVersion["questionText"] == categoryText:
                    return category["questionIndex"]

        return None

    result: dict = dict()

    csv_reader = csv.reader(csvData.splitlines())
    rows = []

    for index, row in enumerate(csv_reader):
        if len(row) != FORM_TEMPLATE_ROW_LENGTH:
            raise RuntimeError(
                "All Rows must have {} columns. Row {} has {} columns.".format(
                    FORM_TEMPLATE_ROW_LENGTH, index, len(row)
                )
            )

        rows.append(row)

    languages = [
        language.strip()
        for language in rows[FORM_TEMPLATE_LANGUAGES_ROW][
            FORM_TEMPLATE_LANGUAGES_COL
        ].split(",")
    ]

    result["classification"] = {
        "name": rows[FORM_TEMPLATE_NAME_ROW][FORM_TEMPLATE_NAME_COL]
    }
    result["version"] = rows[FORM_TEMPLATE_VERSION_ROW][FORM_TEMPLATE_VERSION_COL]
    result["questions"] = []

    categoryIndex = None
    categoryList: list[dict[str, any]] = []

    questionRows = iter(rows[4:])
    questionIndex = 0

    for row in questionRows:
        if isRowEmpty(row):
            categoryIndex = None
            continue

        type = str(row[FORM_TEMPLATE_QUESTION_TYPE_COL]).upper()

        if type not in QuestionTypeEnum.listNames():
            raise RuntimeError("Invalid Question Type Encountered")

        visibilityConditionsText = str.strip(
            row[FORM_TEMPLATE_QUESTION_VISIBILITY_CONDITION_COL]
        )

        visibilityConditions: list = []

        if len(visibilityConditionsText) > 0:

            if questionIndex == 0:
                raise RuntimeError(
                    "First questions cannot have a visibility condition."
                )

            previousQuestion = result["questions"][questionIndex - 1]

            visibilityConditions.append(
                parseCondition(previousQuestion, visibilityConditionsText)
            )

        question = {
            "questionId": row[FORM_TEMPLATE_QUESTION_ID_COL],
            "questionIndex": questionIndex,
            "questionType": QuestionTypeEnum[type].value,
            "questionLangVersions": [],
            "required": isQuestionRequired(row[FORM_TEMPLATE_QUESTION_REQUIRED_COL]),
            "numMax": toNumberOrNone(row[FORM_TEMPLATE_QUESTION_MAX_VALUE_COL]),
            "numMin": toNumberOrNone(row[FORM_TEMPLATE_QUESTION_MIN_VALUE_COL]),
            "stringMaxLength": toNumberOrNone(
                row[FORM_TEMPLATE_QUESTION_LINE_COUNT_COL]
            ),
            "units": row[FORM_TEMPLATE_QUESTION_UNITS_COL],
            "visibleCondition": visibilityConditions,
            "categoryIndex": categoryIndex,
        }

        questionLangVersion = getQuestionLanguageVersionFromRow(row)

        if type == "CATEGORY":
            existingCategoryIndex = findCategoryIndex(
                categoryList=categoryList,
                categoryText=questionLangVersion["questionText"],
            )

            if existingCategoryIndex is not None:
                categoryIndex = existingCategoryIndex
                continue

        questionLangVersions = dict(
            [(questionLangVersion["lang"], questionLangVersion)]
        )

        for _ in range(len(languages) - 1):

            row = next(questionRows, None)

            if row is None or isRowEmpty(row):
                raise RuntimeError(
                    "All Questions must be provided in all the languages supported by the form",
                )

            questionLangVersion = getQuestionLanguageVersionFromRow(row)
            language: str = questionLangVersion["lang"]

            if language not in languages:
                raise RuntimeError(
                    "Language {} for question #{} not listed in Form Languages [{}].".format(
                        language, questionIndex + 1, str.join(", ", languages)
                    ),
                )

            if language in questionLangVersions.keys():
                raise RuntimeError(
                    "Language {} defined multiple times for question #{}".format(
                        language, questionIndex + 1
                    ),
                )

            questionLangVersions[language] = getQuestionLanguageVersionFromRow(row)

        question["questionLangVersions"] = list(questionLangVersions.values())

        if type == "CATEGORY":
            categoryList.append(question)
            categoryIndex = questionIndex

        result["questions"].append(question)
        questionIndex += 1

    return result


def getCsvFromFormTemplate(form_template: FormTemplate):
    """
    Returns a CSV string from a FormTemplate object.
    """

    # Helper functions
    def get_question_lang_list(question: Question):
        lang_list = []
        for lang in question.lang_versions:
            lang_list.append(lang.lang)
        return lang_list

    def list_to_csv(rows: list):
        csv_str = ""

        def format_cell(cell: str):
            return '"{}"'.format(cell if cell is not None else "")

        for row in rows:
            row = [format_cell(cell) for cell in row]

            csv_str += ",".join(row)
            csv_str += "\n"

        return csv_str

    def mcoptions_to_str(mcoptions: str):
        mcoptions = json.loads(mcoptions)
        options = [option["opt"] for option in mcoptions]

        return ",".join(options) if mcoptions is not None else ""

    def get_visible_condition_options(
        visible_condition: str, questions: list[Question]
    ):
        visible_conditions = json.loads(visible_condition)

        if visible_conditions is None or len(visible_conditions) == 0:
            return ""

        visible_condition = visible_conditions[0]
        parent_question_id = visible_condition["qidx"]
        parent_question = questions[parent_question_id]

        if parent_question is None:
            return ""

        mc_options = json.loads(parent_question.lang_versions[0].mcOptions)

        optionIndices = visible_condition["answers"]["mcidArray"]

        options = [mc_options[i]["opt"] for i in optionIndices]

        return ",".join(options) if visible_condition is not None else ""

    questions: list[Question] = form_template.questions

    questions = sorted(questions, key=lambda q: q.questionIndex)

    rows = [
        [
            "Name",
            form_template.classification.name,
            "Languages",
            ",".join(get_question_lang_list(questions[0])),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "Version",
            form_template.version,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Integer/Decimal only",
            "",
            "String Only",
            "MC Only",
        ],
        [
            "Question ID",
            "Question Text",
            "Type",
            "Language",
            "Required",
            "Units",
            "Visible If",
            "Min",
            "Max",
            "# Lines",
            "Options",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
    ]

    for question in questions:
        row = [
            question.questionId,
            question.lang_versions[0].questionText,
            question.questionType.value,
            question.lang_versions[0].lang,
            "Y" if question.required else "N",
            question.units,
            get_visible_condition_options(
                question.visibleCondition, questions=questions
            ),
            question.numMin,
            question.numMax,
            question.stringMaxLength,
            mcoptions_to_str(question.lang_versions[0].mcOptions),
        ]
        rows.append(row)

        for lang in question.lang_versions[1:]:
            row = [
                "",
                lang.questionText,
                "",
                lang.lang,
                "",
                "",
                "",
                "",
                "",
                "",
                mcoptions_to_str(lang.mcOptions),
            ]
            rows.append(row)

    return list_to_csv(rows)
