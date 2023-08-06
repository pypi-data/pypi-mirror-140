import contextlib
import pathlib
from collections.abc import MutableMapping
from typing import Any
from typing import Callable
from typing import Dict


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
    serial_plugin: str = "msgpack",
):
    """
    Only allow one instance of this run within the context of the enforced state manager
    """
    cache_dir = pathlib.Path(cache_dir)
    esm_cache_file = cache_dir / "esm" / "cache" / f"{run_name}.{serial_plugin}"
    esm_cache_file.parent.mkdir(parents=True, exist_ok=True)
    ctx = await hub.idem.acct.ctx(
        f"esm.{esm_plugin}",
        acct_profile=esm_profile,
        acct_key=acct_key,
        acct_file=acct_file,
        acct_blob=acct_blob,
    )
    # If no profile was specified then use the default profile
    if esm_plugin == "local" and not ctx.acct:
        hub.log.debug("Using the default local ESM profile")
        ctx = await hub.idem.acct.ctx(
            "esm.local",
            acct_profile=None,
            acct_data={
                "profiles": {
                    "esm.local": {
                        None: {
                            "run_name": run_name,
                            "cache_dir": cache_dir,
                            "serial_plugin": serial_plugin,
                        }
                    }
                }
            },
        )

    exception = None
    # Enter the context of the Enforced State Manager
    # Do this outside of the try/except so that exceptions don't cause unintentional release of lock in exit
    handle = await hub.esm[esm_plugin].enter(ctx)
    try:
        # Get the current state from the context
        state: Dict[str, Any] = await hub.esm[esm_plugin].get_state(ctx) or {}
        cache_state = hub.idem.managed.file_dict(
            cache_file=str(esm_cache_file), data=state, serial_plugin=serial_plugin
        )
        # The cache_state can be interacted with like a regular dictionary, but the file is always up-to-date
        yield cache_state
        # update the enforced state from the cache
        data = cache_state.data
        if data:
            await hub.esm[esm_plugin].set_state(ctx, data)
    except Exception as e:
        exception = e
        raise
    finally:
        # Exit the context of the Enforced State Manager
        await hub.esm[esm_plugin].exit_(ctx, handle, exception)


def file_dict(hub, cache_file: str, data: Dict = None, serial_plugin: str = "msgpack"):
    return FileDict(
        cache_file=cache_file,
        serializer=hub.serial[serial_plugin].dump,
        deserializer=hub.serial[serial_plugin].load,
        data=data,
    )


class FileDict(MutableMapping):
    """
    Any time there is a change to this dictionary, it will immediately be reflected in a cache file
    """

    def __init__(
        self,
        cache_file: str,
        deserializer: Callable,
        serializer: Callable,
        data: Dict = None,
    ):
        self.deserialize = deserializer
        self.serialize = serializer
        if data is None:
            data = {}
        self.file = pathlib.Path(cache_file)
        with self.file.open("wb+") as fh:
            byte_data: bytes = self.serialize(data)
            fh.write(byte_data)

    @property
    def data(self):
        with self.file.open("rb+") as fh:
            return self.deserialize(fh.read())

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, k):
        return self.data[k]

    def __delitem__(self, v):
        data = self.data
        data.pop(v)
        with self.file.open("wb+") as fh:
            fh.write(self.serialize(data))

    def __setitem__(self, k, v):
        data = self.data
        data[k] = v
        with self.file.open("wb+") as fh:
            byte_data: bytes = self.serialize(data)
            fh.write(byte_data)
