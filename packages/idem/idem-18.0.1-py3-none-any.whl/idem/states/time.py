import asyncio
from typing import Dict


async def sleep(hub, ctx, name, duration: str = None) -> Dict[str, Dict]:
    """
    Sleep resource to be used by other resources to delay creation/deletion for a duration of time in seconds

    Examples:
        .. code-block:: sls

            sleep_60s:
                time.sleep:
                - duration: 60

            some_machine:
                cloud.instance.present:
                - name: my-instance
                - require:
                  - time.sleep: sleep_60s

    """
    result = dict(
        comment=f"Sleep-{duration}sec",
        old_state={},
        new_state={},
        name=name,
        result=True,
    )

    if duration is None or str(duration) == 0:
        result["result"] = False
        result["comment"] = "Duration is required."
        return result

    await asyncio.sleep(duration)

    result["comment"] = f"Successfully slept for {duration} seconds."

    return result
