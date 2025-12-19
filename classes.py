import os
from jsonschema import validate, RefResolver, Draft202012Validator
import json
from loguru import logger

class JSONSchemaValidator:
    @classmethod
    def validate(cls, json_data: dict, schema: dict, resolver):
        validator = Draft202012Validator(schema, resolver=resolver)
        errors = validator.iter_errors(json_data)

        err_list = []
        for error in errors:
            logger.error("The JSON data is not valid", exc_info=error)
            err_list.append(cls._serialize_error(error))

        return err_list

    @staticmethod
    def _serialize_error(error):
        return {
            "message": error.message,
            "validator": error.validator,
            "validator_value": error.validator_value,
            "schema_path": list(error.schema_path),
            "instance_path": list(error.path),
            "schema": error.schema,
            "instance": error.instance,
        }
    
#JSONSchemaValidator.validate(instance, schema, resolver)
