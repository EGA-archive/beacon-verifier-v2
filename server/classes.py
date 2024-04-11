import os
from jsonschema import validate, RefResolver, Draft202012Validator
import json
from loguru import logger
'''
with open('beacon-verifier-v2/beacon-verifier-v2/server/ref_schemas/models/json/beacon-v2-default-model/individuals/defaultSchema.json', 'r') as f:
    individuals = json.load(f)

instance = {
        "id": "hola",
        "sex": {
            "label": 23
        }
    }
schema = individuals

# this is a directory name (root) where the 'grandpa' is located
schema_path = 'file:///{0}/'.format(
        os.path.dirname('beacon-verifier-v2/beacon-verifier-v2/server/ref_schemas/models/json/beacon-v2-default-model/individuals/defaultSchema.json').replace("\\", "/"))
resolver = RefResolver(schema_path, schema)
#validate(instance, schema, resolver=resolver)
'''
class JSONSchemaValidator:
    @classmethod
    def validate(cls, json_data: dict, schema: dict, resolver):
        validator = Draft202012Validator(schema, resolver=resolver)
        errors = validator.iter_errors(json_data)
        err_list = []
        for error in errors:
            logger.error(f"The JSON data is not valid: {error=}")
            err_list.append(error)
        return err_list
    
#JSONSchemaValidator.validate(instance, schema, resolver)
