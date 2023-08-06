from typing import Any
from typing import Dict
from typing import List


async def run(
    hub,
    plugin: str = "none",
    pending_plugin: str = "default",
    name: str = None,
    sls_sources: List[str] = None,
    render: str = None,
    runtime: str = None,
    cache_dir: str = None,
    sls: str = None,
    test: bool = False,
    acct_file: str = None,
    acct_key: str = None,
    acct_profile: str = None,
    acct_blob: str = None,
    subs: List[str] = None,
    managed_state: Dict[str, Any] = None,
):
    ret = await hub.reconcile[plugin].loop(
        pending_plugin,
        name,
        sls_sources,
        render,
        runtime,
        cache_dir,
        sls,
        test,
        acct_file,
        acct_key,
        acct_profile,
        acct_blob,
        subs,
        managed_state,
    )

    return ret
