"""
Config module for Proxmox VE prometheus collector.
"""

from collections.abc import Mapping

def config_from_yaml(yaml):
    """
    Given a dictionary parsed from a yaml file return a config object.
    """

    if not isinstance(yaml, Mapping):
        return ConfigInvalid(
            "Not a dictionary. Check the syntax of the YAML config file."
        )

    modules = {
        key: config_module_from_yaml(value) for
        key, value in
        yaml.items()
    }
    invalid = [
        f"  - {key}: {module}" for
        key, module in
        modules.items() if
        not module.valid
    ]

    if invalid:
        return ConfigInvalid("\n".join(
            ["Invalid module config entries in config file"] + invalid
        ))

    if not modules:
        return ConfigInvalid("Empty dictionary. No modules specified.")

    return ConfigMapping(modules)


def config_from_env(env):
    """
    Given os.environ dictionary return a config object.
    """
    envmap = {
        'PVE_USER': 'user',
        'PVE_PASSWORD': 'password',
        'PVE_TOKEN_NAME': 'token_name',
        'PVE_TOKEN_VALUE': 'token_value',
    }

    confvals = {confkey: env[envkey] for envkey, confkey in envmap.items() if envkey in env}

    if 'PVE_VERIFY_SSL' in env:
        confvals['verify_ssl'] = env['PVE_VERIFY_SSL'].lower() not in ['false', '0']

    if not confvals:
        return ConfigInvalid(
            "Empty dictionary. No pve API parameters specified."
        )

    allow_list = None
    if 'PVE_ALLOW_LIST' in env:
        allow_list = [item for item in env['PVE_ALLOW_LIST'].split(',') if item.strip()]
        if not allow_list:
            return ConfigInvalid("PVE_ALLOW_LIST is set but contains no host names.")

    module = env.get('PVE_MODULE', 'default')
    modules = {}
    modules[module] = ConfigMapping(confvals, allow_list)

    return ConfigMapping(modules)


def config_module_from_yaml(yaml):
    """
    Given a dictionary parsed from a yaml file return a module config object.
    """
    if not isinstance(yaml, Mapping):
        return ConfigInvalid(
            "Not a dictionary. Check the syntax of the YAML config file."
        )

    params = dict(yaml)
    allow_list = params.pop('allow_list', None)
    if 'allow_list' in yaml and not (
            isinstance(allow_list, list) and allow_list and
            all(isinstance(item, str) and item.strip() for item in allow_list)):
        return ConfigInvalid("'allow_list' must be a non-empty list of host names.")

    if not params:
        return ConfigInvalid(
            "Empty dictionary. No pve API parameters specified."
        )

    return ConfigMapping(params, allow_list)


class ConfigMapping(Mapping):
    """
    Valid config object.
    """

    valid = True

    def __init__(self, mapping, allow_list=None):
        super().__init__()
        self._mapping = mapping
        self.allow_list = None if allow_list is None else frozenset(
            item.strip().lower() for item in allow_list
        )

    def allows(self, target):
        """
        Return True if credentials of this module may be sent to target.
        """
        return self.allow_list is None or target.strip().lower() in self.allow_list

    def __str__(self):
        num = len(self._mapping)
        keys = ", ".join(self._mapping.keys())
        return f"Valid config: with {num} keys: {keys}"

    def __getitem__(self, key):
        return self._mapping[key]

    def __iter__(self):
        return iter(self._mapping)

    def __len__(self):
        return len(self._mapping)


class ConfigInvalid:
    """
    Invalid config object.
    """

    # pylint: disable=too-few-public-methods

    valid = False

    def __init__(self, error="Unspecified reason."):
        self._error = error

    def __str__(self):
        return f"Invalid config: {self._error}"
