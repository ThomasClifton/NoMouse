import configparser

# Global config object
_config = None


def load_config():
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
    global _config
    if _config is None:
        load_config()

    with open('settings.ini', 'w') as configfile:
        _config.write(configfile)


def get_config_value(section, option, default_value=None):
    global _config
    if _config is None:
        load_config()

    try:
        return _config.get(section, option)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return default_value


def set_config_value(section, option, value):
    global _config
    if _config is None:
        load_config()

    if not _config.has_section(section):
        _config.add_section(section)

    _config.set(section, option, value)