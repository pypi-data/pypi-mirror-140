import inspect
import hashlib

DEFAULT_CONTENT_TYPE = "application/json"


def get_schema_name(schema):
    if inspect.isclass(schema):
        return schema.__name__

    if hasattr(schema, "__apispec__") and schema.__apispec__.get("model"):
        return schema.__apispec__.get("model")

    if "exclude" in schema.__dict__:
        key = "{}".format(list(schema.__dict__.get("exclude"))).encode("utf-8")

        return "{}-{}".format(
            schema.__class__.__name__, hashlib.md5(key).hexdigest()[:5]
        )
    return schema.__class__.__name__


VALIDATOR_FOR_OPEN_API = {"querystring": "query", "headers": "header", "path": "path"}


class AutoDoc(object):
    def __init__(self, method, introspectable_view, cornice_service):
        self.method = method
        self.view = introspectable_view
        self.view_operations = {self.method.lower(): {}}
        self.cornice_service = cornice_service

    @property
    def content_type(self):
        content_type_info = self.cornice_service.get_contenttypes(self.method)
        try:
            return content_type_info[0] or DEFAULT_CONTENT_TYPE
        except IndexError:
            return DEFAULT_CONTENT_TYPE

    @property
    def request_schemas(self):
        return self.view.get("pcm_request", {})

    @property
    def tags(self):
        return self.view.get("pcm_tags", [])

    @property
    def summary(self):
        return self.view.get("pcm_summary", "")

    @property
    def description(self):
        return self.view.get("pcm_description", "")

    @property
    def security(self):
        return self.view.get("pcm_security", None)

    @property
    def response_schemas(self):
        return self.view.get("pcm_responses", [])

    def add_path_parameter(self, path_parameters):
        parameter_list = []
        for parameter_name in path_parameters:
            parameter_list += [
                {
                    "name": parameter_name,
                    "in": "path",
                    "required": True,
                    "schema": self.get_type_from_field("String"),
                    "description": "{} parameter".format(parameter_name),
                }
            ]
        self._add_parameter(parameter_list)

    def find_schema_for(self, location):
        return self.request_schemas.get(location)

    def _add_tags(self):
        if self.tags:
            self.view_operations[self.method.lower()].update({"tags": self.tags})

    def _add_responses(self, responses_dict):
        self.view_operations[self.method.lower()].update({"responses": responses_dict})

    def _generate_responses(self):
        if self.response_schemas:
            responses_dict = {}
            for status_code in self.response_schemas:
                schema = self.response_schemas[status_code]
                if isinstance(schema, str):  # is only text description
                    status_code_dict = {
                        status_code: {"description": schema, "content": {}}
                    }
                else:
                    schema_name = get_schema_name(schema)
                    if not inspect.isclass(schema) and schema.many:
                        schema_body = {
                            "type": "array",
                            "items": {
                                "$ref": "#/components/schemas/{}".format(schema_name)
                            },
                        }
                    else:
                        schema_body = {
                            "$ref": "#/components/schemas/{}".format(schema_name)
                        }

                    status_code_dict = {
                        status_code: {
                            "description": schema.__doc__ or "",
                            "content": {self.content_type: {"schema": schema_body}},
                        }
                    }
                responses_dict.update(status_code_dict)
            # Update current method dict in Operation
            self._add_responses(responses_dict)

    def _add_parameter(self, parameter_list):
        found_parameter_list = self.view_operations[self.method.lower()].get(
            "parameters", []
        )
        for parameter in parameter_list:
            found_parameter_list.append(parameter)
        self.view_operations[self.method.lower()].update(
            {"parameters": found_parameter_list}
        )

    def _generate_parameters(self):
        def _observed_name(key):
            field = schema._declared_fields[key]
            return getattr(field, "data_key", key) or key

        parameter_list = []
        for parameter_in in ["querystring", "headers"]:
            schema = self.find_schema_for(parameter_in)
            if schema:
                parameter_list += [
                    {
                        "name": _observed_name(key),
                        "in": VALIDATOR_FOR_OPEN_API.get(parameter_in, parameter_in),
                        "required": schema._declared_fields[key].required,
                        "schema": self.get_type_from_field(
                            schema._declared_fields[key]
                        ),
                        "description": schema.__doc__ or "",
                    }
                    for key in schema._declared_fields
                ]
        if parameter_list:
            self._add_parameter(parameter_list)

    def _generate_request_body(self):
        body_schema = self.find_schema_for("body")
        if body_schema:
            request_body_dict = {
                "content": {
                    self.content_type: {
                        "schema": {
                            "$ref": "#/components/schemas/{}".format(
                                get_schema_name(body_schema)
                            )
                        }
                    }
                }
            }
            self._add_request_body(request_body_dict)

    def _add_request_body(self, request_body_dict):
        self.view_operations[self.method.lower()].update(
            {"requestBody": request_body_dict}
        )

    def _add_summary(self):
        if self.summary:
            self.view_operations[self.method.lower()].update({"summary": self.summary})

    def _add_description(self):
        if self.description:
            self.view_operations[self.method.lower()].update(
                {"description": self.description}
            )

    def _add_security(self):
        if self.security:
            self.view_operations[self.method.lower()].update(
                {"security": [{self.security: []}]}
            )

    def to_dict(self):
        self._add_tags()
        self._add_summary()
        self._add_description()
        self._add_security()
        self._generate_request_body()
        self._generate_parameters()
        self._generate_responses()
        return self.view_operations

    @staticmethod
    def get_type_from_field(field):
        field_name = field.__class__.__name__
        return {
            "UUID": {"type": "string", "format": "uuid"},
            "Number": {"type": "number"},
            "Integer": {"type": "integer"},
            "Decimal": {"type": "number"},
            "Boolean": {"type": "boolean"},
            "Float": {"type": "number", "format": "float"},
            "DateTime": {"type": "string", "format": "date-time"},
            "LocalDateTime": {"type": "string", "format": "date-time"},
            "Time": {"type": "string", "format": "time"},
            "Date": {"type": "string", "format": "date"},
            "Email": {"type": "string", "format": "email"},
            "Bool": {"type": "boolean"},
            "Int": {"type": "integer"},
        }.get(field_name, {"type": "string"})
