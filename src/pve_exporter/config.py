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

    Each of the credential variables may instead be given as <VAR>_FILE
    (e.g., PVE_PASSWORD_FILE) pointing to a file holding the value, as used
    with docker secrets or systemd credentials.
    """
    envmap = {
        'PVE_USER': 'user',
        'PVE_PASSWORD': 'password',
        'PVE_TOKEN_NAME': 'token_name',
        'PVE_TOKEN_VALUE': 'token_value',
    }

    confvals = {}
    for envkey, confkey in envmap.items():
        filekey = f'{envkey}_FILE'
        if filekey in env and envkey in env:
            return ConfigInvalid(
                f"Both {envkey} and {filekey} are set. Use only one of them."
            )
        if filekey in env:
            # Do not include the path in errors, it might be a misplaced secret.
            try:
                with open(env[filekey], encoding='utf-8') as handle:
                    value = handle.readline().rstrip('\n')
            except OSError as err:
                return ConfigInvalid(f"Failed to read {filekey}: {err.strerror}")
            except UnicodeDecodeError:
                return ConfigInvalid(f"Failed to read {filekey}: Not valid UTF-8")
            if not value:
                return ConfigInvalid(f"The file referenced by {filekey} is empty.")
            confvals[confkey] = value
        elif envkey in env:
            confvals[confkey] = env[envkey]

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
