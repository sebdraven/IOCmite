import os.path
from redis import StrictRedis


class LastRun:
    def __init__(self, is_redis=False, tmp_file="") -> None:
        self.__get_handle(is_redis, tmp_file)

    def __get_handle(self, is_redis, tmp_file):
        if is_redis:
            self.handle = StrictRedis(db=1)
        if tmp_file:
            if os.path.isfile(self.tmp_file):
                self.handle = self.tmp_file

    def get_last_run(self):
        if isinstance(self.handle, StrictRedis):
            return self.handle.get("last_run")
        if isinstance(self.handle, str):
            if os.path.is_file(self.tmp_file):
                return open(self.handle).readline()
            else:
                return None

    def set_last_run(self, last_run):
        if isinstance(self.handle, StrictRedis):
            self.handle.set("last_run", last_run)
        if isinstance(self.handle, str):
            if os.path.is_file(self.tmp_file):
                open(self.handle, "w").write(last_run)
