import click
from click import BadParameter, Abort
from pydantic import BaseModel
from typing import Dict

from ..utils import *
from ...client.files_client import FilesClient
from ...client.service_registry import ServiceRegistry
from ...configuration import Configuration, ConfigurationManager
from ...json_path import JsonPath, BrokenPropertyPathError

_full_schema = Configuration.schema()
_adapter_to_property_paths: Dict[str, List[str]] = dict()
_logger = get_logger('config')


@click.group("config")
def config():
    pass


@config.command("schema")
def config_schema():
    click.echo(json.dumps(_full_schema, indent=2, sort_keys=True))


@config.command("available-properties")
@click.option("--type", "-t", required=False, default=None)
def config_list_available_properties(type: Optional[str] = None):
    __show_available_properties(type)


def __show_available_properties(adapter_type: Optional[str] = None):
    print()

    click.secho('                                          ', bold=True, bg='blue')
    click.secho('  All available configuration properties  ', bold=True, bg='blue')
    click.secho('                                          ', bold=True, bg='blue')

    click.echo('\nPlease check out https://docs.viral.ai/analytics for more information.')

    adapter_to_property_paths = __get_known_adapter_to_property_paths()

    for service_adapter_name, service_property_paths in adapter_to_property_paths.items():
        if adapter_type and adapter_type != service_adapter_name:
            continue
        click.secho(f'\n{service_adapter_name}\n', bold=True)
        for service_property_path in service_property_paths:
            if service_property_path == 'adapter_type':
                continue  # This is an internal property. Permanently skip.
            if service_property_path == 'default':
                continue  # This is temporarily skipped until the CLI support multiple endpoint.
            click.secho(f'  · {service_adapter_name}.{service_property_path}')

    print()


def __get_known_adapter_to_property_paths() -> Dict[str, List[str]]:
    if not _adapter_to_property_paths:
        __resolve_reference(_full_schema)
        service_property_paths = __list_all_json_path(_full_schema['properties']['endpoints']['items'])
        service_adapter_types = [
            CollectionsClient.get_adapter_type(),
            DataConnectClient.get_adapter_type(),
            FilesClient.get_adapter_type(),
            ServiceRegistry.get_adapter_type(),
            WesClient.get_adapter_type(),
        ]

        for service_adapter_name in service_adapter_types:
            _adapter_to_property_paths[service_adapter_name] = list()
            for service_property_path in service_property_paths:
                if service_property_path in ['id', 'adapter_type']:
                    continue  # This is an internal property. Permanently skip.
                if service_adapter_name == 'registry' and service_property_path.startswith('authentication.'):
                    continue  # A protected registry is not supported.
                _adapter_to_property_paths[service_adapter_name].append(service_property_path)

    return _adapter_to_property_paths


def __list_all_json_path(obj: Dict[str, Any], prefix_path: List[str] = None):
    properties = obj.get('properties') or dict()
    paths = []

    prefix_path = prefix_path or list()

    if obj['type'] == 'object':
        for property_name, obj_property in properties.items():
            if 'anyOf' in obj_property:
                for property_to_resolve in obj_property['anyOf']:
                    paths.extend(__list_all_json_path(__fetch_reference(property_to_resolve['$ref'], _full_schema),
                                                      prefix_path + [property_name]))
            elif obj_property['type'] == 'object':
                paths.extend(__list_all_json_path(obj_property, prefix_path + [property_name]))
            elif obj_property['type'] == 'array':
                paths.extend(__list_all_json_path(obj_property['items'], prefix_path + [property_name]))
                paths.extend(__list_all_json_path(obj_property['items'], prefix_path + [property_name + '[i]']))
            else:
                prefix_path_string = '.'.join(prefix_path)
                paths.append(f'{prefix_path_string}{"." if prefix_path_string else ""}{property_name}')

    return sorted(paths)


def __fetch_reference(reference_url: str, root: Dict[str, Any]):
    if reference_url.startswith('#/'):
        ref_path = reference_url[2:].split(r'/')
        local_reference = root
        try:
            while ref_path:
                property_name = ref_path.pop(0)
                local_reference = local_reference[property_name]
        except KeyError as e:
            raise RuntimeError(f'The reference {reference_url} for the configuration is undefined.')
        return __resolve_reference(local_reference, root)
    raise NotImplementedError('Resolving an external reference is not supported.')


def __resolve_reference(obj: Dict[str, Any], root: Optional[Dict[str, Any]] = None):
    root = root or obj
    properties = obj.get('properties') or dict()
    for property_name, obj_property in properties.items():
        if obj_property.get('$ref'):
            properties[property_name] = __fetch_reference(obj_property.get('$ref'), root)
        # Deal with array
        if obj_property.get('items') and obj_property.get('items').get('$ref'):
            obj_property['items'] = __fetch_reference(obj_property.get('items').get('$ref'), root)

    return obj


@config.command("set-default")
@click.argument("adapter-type", required=True, default=None)
@click.argument("endpoint-id", required=False, default=None)
def set_default(adapter_type: str, endpoint_id: str):
    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    configuration: Configuration = config_manager.load()
    endpoint = configuration.set_default(adapter_type=adapter_type, endpoint_id=endpoint_id)
    config_manager.save(configuration)


@config.command("remove-endpoint")
@click.argument("adapter-type", required=True, default=None)
@click.argument("endpoint-id", required=True, default=None)
def remove_endpoint(adapter_type: str, endpoint_id: str):
    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    configuration: Configuration = config_manager.load()
    configuration.remove_endpoint(adapter_type=adapter_type, endpoint_id=endpoint_id)
    config_manager.save(configuration)


@config.command("add-endpoint")
@click.argument("endpoint-id", required=True)
@click.argument("adapter-type", required=True, default=None)
@click.argument("url", required=False, default=None)
def add_endpoint(endpoint_id: str, adapter_type: str, url: str):
    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    configuration: Configuration = config_manager.load()
    configuration.add_endpoint(adapter_type=adapter_type, endpoint_id=endpoint_id, url=url)
    config_manager.save(configuration)


@config.command("list")
@click.pass_context
def config_list(ctx: click.Context):
    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    click.secho(config_manager.load_raw() or '{}', dim=True)


@config.command("get")
@click.argument("key")
@click.option("--endpoint-id", "-i", required=False, type=str, default=None)
# @catch_errors(error_types=(ConfigException,))
def config_get(key: str, endpoint_id: str):
    adapter_type, path = __parse_configuration_key(key)

    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    configuration: Configuration = config_manager.load()

    try:
        endpoint = configuration.get_endpoint_or_default(adapter_type, endpoint_id=endpoint_id)
        result = JsonPath.get(endpoint, path)
    except BrokenPropertyPathError as __:
        _logger.error(f'A/{adapter_type}: The path "{path}" does not exist in {endpoint}.')
        raise Abort(f'The configuration {key} does not exist.')
    except MissingEndpointError:
        result = None

    if result is None:
        click.secho('null', dim=True)
    elif isinstance(result, bool):
        click.secho(str(result).lower(), dim=True)
    elif isinstance(result, BaseModel):
        click.secho(result.json(indent=2), dim=True)
    else:
        click.secho(result, dim=True)


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--endpoint-id", "-i", required=False, type=str, default=None)
# @catch_errors(error_types=(RuntimeError,))
def config_set(key: str, value: str, endpoint_id: str):
    adapter_type, path = __parse_configuration_key(key)
    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    configuration = config_manager.load()

    endpoint = configuration.get_endpoint_or_default(adapter_type,
                                                     endpoint_id=endpoint_id,
                                                     create_default_if_missing=True)

    try:
        JsonPath.set(endpoint, path, value)
    except BrokenPropertyPathError as __:
        # Attempt to repair the broken path.
        __repair_path(endpoint, '.'.join(path.split('.')[:-1]))

        # Then, try again.
        JsonPath.set(endpoint, path, value)

    config_manager.save(configuration)


def __repair_path(obj, path):
    selectors = path.split(r'.')
    visited = []

    _logger.debug(f'__repair_path: type(obj) = {type(obj).__name__}')
    _logger.debug(f'__repair_path: obj = {obj}')
    _logger.debug(f'__repair_path: path = {path}')

    for selector in selectors:
        visited.append(selector)
        route = '.'.join(visited)

        _logger.debug(f'__repair_path: route = {route}')

        try:
            JsonPath.get(obj, route, raise_error_on_null=True)
            break
        except BrokenPropertyPathError as e:
            visited_nodes = e.visited_path.split(r'.')
            last_visited_node = visited_nodes[-1]

            node = e.parent or obj

            _logger.debug(f'__repair_path: ***** Broken Path Detected *****')
            _logger.debug(f'__repair_path: type(e.parent) = {type(e.parent).__name__}')
            _logger.debug(f'__repair_path: e.parent = {e.parent}')

            annotation = node.__annotations__[last_visited_node]

            if str(annotation).startswith('typing.Dist['):
                setattr(node, last_visited_node, dict())
            elif str(annotation).startswith('typing.List['):
                setattr(node, last_visited_node, list())
            elif str(annotation).startswith('typing.Union[') or str(annotation).startswith("typing.Optional["):
                # Dealing with Union/Optional
                cls = annotation.__args__[0]
                required_properties = cls.schema().get('required') or []
                if issubclass(cls, BaseModel):
                    placeholders = {
                        p: __get_place_holder(cls.__annotations__[p])
                        for p in required_properties
                    }
                    setattr(node, last_visited_node, cls(**placeholders))
                else:
                    setattr(node, last_visited_node, cls())
            else:
                cls = annotation
                setattr(node, last_visited_node, cls())

            _logger.debug(f'__repair_path: node = {getattr(node, last_visited_node)}')


def __get_place_holder(cls):
    if cls == str:
        return ''
    elif cls == int or cls == float:
        return 0
    elif cls == bool:
        return False
    else:
        raise NotImplementedError(cls)


def __parse_configuration_key(key: str):
    nodes = key.split(r'.')

    adapter_type = nodes[0]
    path = '.'.join(nodes[1:])

    adapter_to_property_paths = __get_known_adapter_to_property_paths()

    if adapter_type not in adapter_to_property_paths:
        __show_available_properties()
        raise BadParameter(f'Unknown configuration key: A/{adapter_type}')

    if path and path not in adapter_to_property_paths[adapter_type]:
        __show_available_properties(adapter_type)
        raise BadParameter(f'Unknown configuration key: A/{adapter_type}: P/{path}: Available Paths: {adapter_to_property_paths[adapter_type]})"')

    return adapter_type, path
