# The order of the sequence that needs to be implemented:
# Start with a single sls file, just like you started with salt
# Stub out the routines around gathering the initial sls file
# Just use a yaml renderer and get it to where we can manage some basic
# includes to drive to highdata
# Then we can start to fill out renderers while at the same time
# deepening the compiler
import pathlib
import sys


def __init__(hub):
    hub.pop.sub.load_subdirs(hub.idem, recurse=True)
    hub.idem.RUNS = {}
    hub.pop.sub.add(dyne_name="log")
    hub.pop.sub.add(dyne_name="acct")
    hub.pop.sub.add(dyne_name="rend")
    hub.pop.sub.add(dyne_name="output")
    hub.pop.sub.add(dyne_name="evbus")
    hub.pop.sub.add(dyne_name="reconcile")
    hub.pop.sub.load_subdirs(hub.reconcile, recurse=True)
    hub.pop.sub.add(dyne_name="tool")
    hub.pop.sub.load_subdirs(hub.tool, recurse=True)
    hub.pop.sub.add(dyne_name="esm")
    hub.pop.sub.add(dyne_name="exec")
    hub.pop.sub.load_subdirs(hub.exec, recurse=True)
    hub.pop.sub.add(dyne_name="states")
    hub.pop.sub.load_subdirs(hub.states, recurse=True)
    hub.idem.RMAP = hub.idem.req.init.define()
    hub.idem.RUN_NAME = "cli"


def cli(hub):
    """
    Execute a single idem run from the cli
    """
    hub.pop.config.load(["idem", "acct", "rend", "evbus"], cli="idem")
    # Initialize the async loop for the entire project
    hub.pop.loop.create()
    # Start the main program within the async loop
    retcode = hub.pop.Loop.run_until_complete(hub.idem.init.cli_apply())
    sys.exit(retcode)


async def cli_apply(hub) -> int:
    """
    Run the CLI routine in a loop
    """
    if hub.SUBPARSER in ("encrypt", "decrypt"):
        # Break early for acct commands
        return await hub.acct.init.cli_apply()

    # Initialize the broker queue for evbus
    await hub.evbus.broker.init()

    # Specify the serializing plugin for evbus
    hub.evbus.SERIAL_PLUGIN = hub.OPT.evbus.serial_plugin
    # Use the run name as a routing key for exec modules
    hub.idem.RUN_NAME = hub.OPT.idem.run_name

    # Collect ingress profiles from acct
    ingress_profiles = await hub.evbus.acct.profiles(
        acct_file=hub.OPT.acct.acct_file,
        acct_key=hub.OPT.acct.acct_key,
    )

    # Start the listener in it's own task
    listener = hub.pop.Loop.create_task(hub.evbus.init.start(ingress_profiles))
    try:
        await hub.evbus.init.join()

        if hub.SUBPARSER == "state":
            return await hub.idem.cli.sls()
        elif hub.SUBPARSER == "exec":
            return await hub.idem.cli.exec()
        elif hub.SUBPARSER == "describe":
            return await hub.idem.cli.desc()
        elif hub.SUBPARSER == "validate":
            return await hub.idem.cli.validate()
        elif hub.SUBPARSER == "refresh":
            return await hub.idem.cli.refresh()
        elif hub.SUBPARSER == "restore":
            return await hub.idem.cli.restore()
        else:
            print(hub.args.parser.help())
            return 2
    finally:
        await hub.evbus.init.stop()
        await listener


def get_refs(hub):
    """
    Determine where the sls sources are
    """
    sls_sources = []
    slses = []
    if hub.OPT.idem.tree:
        tree = f"file://{hub.OPT.idem.tree}"
        sls_sources.append(tree)
    for sls in hub.OPT.idem.sls:
        process_sls(sls_sources, slses, sls)

    sls_sources.extend(hub.OPT.idem.sls_sources)

    return {"sls_sources": sls_sources, "sls": slses}


def get_param_refs(hub):
    """
    Determine where the param sls sources are
    """
    params_file = hub.OPT.idem.params
    if params_file is None or len(params_file) == 0:
        return {"param_sources": [], "sls": None}

    param_sources = []
    slses = []
    process_sls(param_sources, slses, params_file)
    param_sources.extend(hub.OPT.idem.param_sources)

    return {"param_sources": param_sources, "sls": slses[0]}


def process_sls(sources, slses, sls):
    path = pathlib.Path(sls)
    if path.is_file():
        ref = str(path.stem if path.suffix == ".sls" else path.name)
        slses.append(ref)
        implied = f"file://{path.parent}"
        if implied not in sources:
            sources.append(implied)
    else:
        slses.append(sls)
