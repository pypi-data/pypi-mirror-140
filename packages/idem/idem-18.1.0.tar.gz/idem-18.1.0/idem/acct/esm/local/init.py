def gather(hub, profiles):
    """
    The "default" profile for esm.local is created with configuration values
    Other profiles can be created manually with the following format.

    .. code-block:: sls

        esm.local:
            profile_name:
                run_name: ...
                cache_dir: /path/to/cache/dir
                serial_plugin: json|msgpack
    """
    sub_profiles = {}
    for profile, ctx in profiles.get("esm.local", {}).items():
        # Fill in any missing params from hub.OPT if possible
        ctx.run_name = ctx.get("run_name", hub.OPT.idem.run_name)
        ctx.cache_dir = ctx.get("run_name", hub.OPT.idem.cache_dir)
        ctx.serial_plugin = ctx.get("run_name", hub.OPT.idem.serial_plugin)
        sub_profiles[profile] = ctx
    return sub_profiles
