import re
import importlib

from apispec import APISpec
from apispec.exceptions import DuplicateComponentNameError

from .generator import get_schema_name, AutoDoc

from .marshmallow import MarshmallowPlugin

from .predicates import register as predicates_register


def includeme(config):
    config.include("pyramid_apispec.views")

    def spec_view(request):
        version = request.matchdict.get("version")
        if not version:
            return {}
        try:
            _path = f"{config.root_package.__name__}.api.{version}.apispecview"
            m = importlib.import_module(_path)
        except ImportError:
            request.response.status = 404
            return {}
        return m.api_spec(request)

    config.add_route("openapi_spec", "/{version}/openapi.json")
    config.add_view(spec_view, route_name="openapi_spec", renderer="json")

    config.pyramid_apispec_add_explorer(
        spec_route_name="openapi_spec",
        explorer_route_path="/{version}/api-explorer",
    )
    predicates_register(config)


class InstropectedView:
    def __init__(self, view):
        self.view = view
        self.introspectable = view["introspectable"]

    def __getattr__(self, attr):
        return self.introspectable.get(attr)


def get_uri_placeholders(uri_pattern):
    """pattern: {any}"""
    return re.findall("{(.*?)}", uri_pattern)


def get_spec(request, title, version, description=None, security_scheme=None):
    spec = APISpec(
        title=title,
        version=version,
        openapi_version="3.0.2",
        plugins=[MarshmallowPlugin()],
    )

    introspector = request.registry.introspector

    for view in introspector.get_category("views"):
        intro = InstropectedView(view)
        show_apispec = intro.pcm_show or ""

        if not all(
            (show_apispec == request.matchdict.get("version"), intro.request_methods)
        ):
            continue

        # Check option before skip
        if intro.request_methods.lower() in ["head", "option"]:
            continue

        route = introspector.get("routes", intro.route_name)
        original_pattern = route["pattern"]
        cornice_service = request.registry.cornice_services.get(original_pattern)

        autodoc = AutoDoc(
            method=intro.request_methods,
            introspectable_view=intro.introspectable,
            cornice_service=cornice_service,
        )

        if intro.pcm_request:
            for _, v in intro.pcm_request.items():
                try:
                    spec.components.schema(get_schema_name(v), schema=v)
                except DuplicateComponentNameError:
                    pass

        if intro.pcm_responses:
            for _, v in intro.pcm_responses.items():
                try:
                    spec.components.schema(get_schema_name(v), schema=v)
                except DuplicateComponentNameError:
                    pass

        path_parameters = get_uri_placeholders(original_pattern)
        if path_parameters:
            autodoc.add_path_parameter(path_parameters)

        _op = autodoc.to_dict()

        spec.path(path="/" + original_pattern, operations=_op)

    if security_scheme:
        for k, v in security_scheme.items():
            spec.components.security_scheme(k, v)

    openapi_spec = spec.to_dict()

    if description:
        openapi_spec["info"].update({"description": description})

    scheme = request.scheme  # Or force to https
    main_server_url = "{}://{}".format(scheme, request.host)
    openapi_spec.update({"servers": [{"url": main_server_url}]})

    return openapi_spec
