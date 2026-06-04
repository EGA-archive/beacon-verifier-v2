def return_unhandled_error(path, value, definition, error):
    schema_to_return={
                        "errorMessage": str(error),
                        "schema": {
                            "path": path,
                            "definition": definition
                            },
                        "received": {
                            "path": path,
                            "value": value,
                        }
                    }
    return schema_to_return

def error_message_to_return(log, inc, gran):
    error_message={
                "granularity": gran,
                "include": inc,
                "errorMessage": log["message"],
                "schema": {
                    "path": log["schema_path"],
                    "definition": log["schema"],
                },
                "received": {
                    "path": log["instance_path"],
                    "value": log["instance"],
                }
            }
    return error_message

def error_message_with_dataset_to_return(log, datasetId, inc, gran):
    error_message={
                    "granularity": gran,
                    "include": inc,
                    "datasetId": datasetId,
                    "errorMessage": log["message"],
                    "schema": {
                        "path": log["schema_path"],
                        "definition": log["schema"],
                    },
                    "received": {
                        "path": log["instance_path"],
                        "value": log["instance"],
                    }
                }
    return error_message