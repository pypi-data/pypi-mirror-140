import contextlib
import json
import pathlib
from collections.abc import MutableMapping
from typing import Any
from typing import Dict

import dict_tools.data


class FileDict(MutableMapping):
    """
    Any time there is a change to this dictionary, it will immediately be reflected in a cache file
    """

    def __init__(self, cache_file: str, data: Dict = None):
        if data is None:
            data = {}
        self.file = pathlib.Path(cache_file)
        with self.file.open("w+") as fh:
            json.dump(data, fh)

    @property
    def data(self):
        with self.file.open("r+") as fh:
            return json.load(fh)

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, k):
        return self.data[k]

    def __delitem__(self, v):
        d = self.data
        d.pop(v)
        with self.file.open("w+") as fh:
            json.dump(d, fh)

    def __setitem__(self, k, v):
        d = self.data
        d[k] = v
        with self.file.open("w+") as fh:
            json.dump(d, fh)


@contextlib.asynccontextmanager
async def context(
    hub,
    run_name: str,
    cache_dir: str,
    esm_plugin: str = "local",
    esm_profile: str = "default",
    acct_file: str = None,
    acct_key: str = None,
    acct_blob: str = None,
):
    """
    Only allow one instance of this run within the context of the enforced state manager
    """
    cache_dir = pathlib.Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{run_name}.json"
    if acct_key:
        acct_data = await hub.idem.acct.ctx(
            f"esm.{esm_plugin}",
            acct_profile=esm_profile,
            acct_key=acct_key,
            acct_file=acct_file,
            acct_blob=acct_blob,
        )
    else:
        acct_data = {}
    ctx = dict_tools.data.NamespaceDict(
        run_name=run_name,
        cache_dir=cache_dir,
        acct=acct_data,
    )

    handle = None
    exception = None
    try:
        # Enter the context of the Enforced State Manager
        handle = await hub.esm[esm_plugin].enter(ctx)
        # Get the current state from the context
        state: Dict[str, Any] = await hub.esm[esm_plugin].get_state(ctx)
        cache_state = FileDict(str(cache_file), state or {})
        # The cache_state can be interacted with like a regular dictionary, but the file is always up-to-date
        yield cache_state
        # update the enforced state from the cache
        await hub.esm[esm_plugin].set_state(ctx, cache_state.data)
    except Exception as e:
        exception = e
        raise
    finally:
        # Exit the context of the Enforced State Manager
        await hub.esm[esm_plugin].exit_(ctx, handle, exception)
