"""
Config module for Proxmox VE prometheus collector.
"""

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping


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
        "  - {0}: {1}".format(key, module) for
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

def value_from_file_or_env(env, name):
    """
    Given os.environ dictionary, and the name of a key
    returns the value inside the name with the _FILE suffix (if it exists),
    otherwise returns the value of the named env key.
    If the key does not exists, returns None.
    """
    envfile_key = f"{name}_FILE"
    if envfile_key in env:
        with open(env[envfile_key], 'r') as envfile:
            # read will return the string followed by a newline, which we don't want
            # so we split and take the first line without the \n
            return envfile.read().splitlines()[0]
    else:
        return env.get(name)

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

    confvals = {}
    for envkey, confkey in envmap.items():
        value = value_from_file_or_env(env, envkey)
        if value is not None:
            confvals[confkey] = value

    if 'PVE_VERIFY_SSL' in env:
        confvals['verify_ssl'] = env['PVE_VERIFY_SSL'].lower() not in ['false', '0']

    if not confvals:
        return ConfigInvalid(
            "Empty dictionary. No pve API parameters specified."
        )

    module = env.get('PVE_MODULE', 'default')
    modules = {}
    modules[module] = ConfigMapping(confvals)

    return ConfigMapping(modules)


def config_module_from_yaml(yaml):
    """
    Given a dictionary parsed from a yaml file return a module config object.
    """
    if not isinstance(yaml, Mapping):
        return ConfigInvalid(
            "Not a dictionary. Check the syntax of the YAML config file."
        )

    if not yaml:
        return ConfigInvalid(
            "Empty dictionary. No pve API parameters specified."
        )

    return ConfigMapping(yaml)


class ConfigMapping(Mapping):
    """
    Valid config object.
    """

    valid = True

    def __init__(self, mapping):
        super().__init__()
        self._mapping = mapping

    def __str__(self):
        num = len(self._mapping)
        keys = ", ".join(self._mapping.keys())
        return "Valid config: with {0} keys: {1}".format(num, keys)

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
        return "Invalid config: {0}".format(self._error)
