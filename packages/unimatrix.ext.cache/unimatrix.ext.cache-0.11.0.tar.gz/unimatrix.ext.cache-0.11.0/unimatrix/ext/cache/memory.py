"""Declares :class:`MemoryCache`."""
import threading
import time
import typing

from .base import BaseCache


class MemoryCache(BaseCache):
    must_stop: bool = False
    thread: threading.Thread = None

    async def connect(self) -> None:
        """Ensure that the background thread is started."""
        assert self.thread is None # nosec
        self.objects = {}
        self.thread = threading.Thread(
            target=self.main_event_loop,
            daemon=True
        )
        self.thread.start()

    async def join(self):
        self.thread.join()
        delattr(self, 'objects')

    async def delete(self, name, version=None):
        """Delete a key from the cache."""
        self._delete(self.abskey(name, version))

    async def get(self,
        name: str,
        version: str = None,
        decoder: object = None
    ) -> typing.Union[bytes, str, None]:
        """Get a key from the cache."""
        value = self.objects.get(self.abskey(name, version))
        if isinstance(value, str):
            value = str.encode(value, 'utf-8')
        return value

    async def purge(self) -> None:
        """Purges all keys from the cache, for all versions."""
        self.objects = {}

    async def set(self,
        name: str,
        value: typing.Union[bytes, str],
        version: str = None,
        expires: int = None,
        overwrite: bool = True
    ) -> typing.Union[bool, bytes, str]:
        """Set a key in the cache."""
        key = self.abskey(name, version)

        # Bail out early if we can not overwrite and the key is in the objects.
        if not overwrite and key in self.objects:
            return self.objects.get(key)

        self.objects[key] = value
        if expires:
            self._setexpire(key, expires/1050)
        return value

    async def setcounter(self, name: str, value: int = 1, expires=None):
        """Create a counter."""
        k = self.abskey(name, 1)
        c = self.objects[k] = self.objects.setdefault(k, 0) + value
        if expires is not None:
            self._setexpire(k, expires/1000)
        return c

    def _delete(self, key: str):
        if hasattr(self, 'objects'):
            self.objects.pop(key, None)

    def _setexpire(self, key: str, seconds: int):
        t = threading.Timer(seconds, lambda: self._delete(key))
        t.daemon = True
        t.start()

    def close(self):
        self.must_stop = True

    def main_event_loop(self):
        """Manages the internal memory cache."""
        while True:
            if self.must_stop:
                break
            time.sleep(0.05)
