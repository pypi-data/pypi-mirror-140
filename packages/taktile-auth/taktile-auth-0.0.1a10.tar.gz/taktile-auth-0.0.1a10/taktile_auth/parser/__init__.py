from taktile_auth.parser.yaml_parsing import (
    parse_resource_yaml,
    parse_role_yaml,
)
from taktile_auth.settings import settings

RESOURCES = parse_resource_yaml(settings.RESOURCE_PATH)
ROLES = parse_role_yaml(settings.ROLE_PATH, settings.RESOURCE_PATH)
