from gartersnake.pip import installed_packages


def vcs_version() -> str:
    try:
        if 'dunamai' not in installed_packages():
            print('`dunamai` is not installed; version will default to `0.0.0`')

        from dunamai import Version

        version = Version.from_any_vcs().serialize()
    except (ModuleNotFoundError, RuntimeError) as error:
        print(error)
        version = '0.0.0'

    return version
