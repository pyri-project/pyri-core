import RobotRaconteur as RR
import asyncio

from . import core

class RRPyriCore:
    def __init__(self, pyri_core: core.PyriCore):
        super().__init__()

        self._core = pyri_core

    @property
    def device_info(self):
        future = asyncio.run_coroutine_threadsafe(
            self._do_get_device_info(),
            self._core.get_loop()
        )
         
        return future.result(5)
    
    async def _do_get_device_info(self):
        return None