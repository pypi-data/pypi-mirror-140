"""
This file contains routines to get sls files from references
"""


async def ref(hub, name, sls):
    """
    Cache the given file from the named reference point
    """
    if hub.idem.RUNS[name]["params_processing"]:
        sources = hub.idem.RUNS[name]["param_sources"]
    else:
        sources = hub.idem.RUNS[name]["sls_sources"]

    for source in sources:
        proto = source[: source.index(":")]
        path = sls.replace(".", "/")
        locs = [f"{path}.sls", f"{path}/init.sls"]
        for loc in locs:
            cfn = await hub.pop.ref.last(f"idem.sls.{proto}.cache")(
                hub.idem.RUNS[name]["cache_dir"], source, loc
            )
            if cfn:
                return cfn
