import configparser

# Global config object
_config = None


def load_config():
    """
    Load configuration from settings.ini file.
    If file doesn't exist or is missing sections/options, creates defaults.

    Returns:
        configparser.ConfigParser: Loaded configuration object
    """
    global _config
    _config = configparser.ConfigParser()
    _config.read('settings.ini')

    if not _config.has_section('application'):
        _config.add_section('application')

    if not _config.has_option('application', 'theme'):
        _config.set('application', 'theme', 'arc')

    if not _config.has_option('application', 'video_source'):
        _config.set('application', 'video_source', '0')

    if not _config.has_option('application', 'hand_preference'):
        _config.set('application', 'hand_preference', 'Right')

    if not _config.has_option('application', 'camera_orientation'):
        _config.set('application', 'camera_orientation', 'Front Facing')

    save_config()

    return _config


def save_config():
    """
    Save current configuration to settings.ini file.
    Creates the file if it doesn't exist.
    """
    global _config
    if _config is None:
        load_config()

    with open('settings.ini', 'w') as configfile:
        _config.write(configfile)


def get_config_value(section, option, default_value=None):
    """
    Get a value from the configuration.

    Args:
        section (str): Configuration section
        option (str): Option name within section
        default_value: Value to return if option doesn't exist

    Returns:
        The configuration value or default_value if not found
    """
    global _config
    if _config is None:
        load_config()

    try:
        return _config.get(section, option)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return default_value


def set_config_value(section, option, value):
    """
    Set a value in the configuration.

    Args:
        section (str): Configuration section
        option (str): Option name within section
        value: Value to set
    """
    global _config
    if _config is None:
        load_config()

    if not _config.has_section(section):
        _config.add_section(section)

    _config.set(section, option, value)