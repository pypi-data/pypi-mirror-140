""" make recursive cpy easy"""
import os
import shutil
import errno
from concurrent.futures import ThreadPoolExecutor, as_completed

from pathlib import Path
from tqdm import tqdm

from apu.io.fileformat import compair
from apu.io.file_chunk import Chunk


def copy_(file_, pbar=None):
    """simple copy for one file"""
    src_file = file_[0]
    dst_file = file_[1]

    shutil.copy(src_file, dst_file)

    if pbar is not None:
        pbar.update(1)


class Copy:
    """Copy data"""
    def __init__(self,
                 origin: str,
                 dest: str,
                 number: int = 1,
                 jobs: int = os.cpu_count(),
                 sort: bool = True,
                 verbose: bool = False):
        """copy from origin to destination. copy only a given
           number of objects of each subfolder to the destination.
           If you want you can sort the data in each subfolder. this
           makes it easy to make it more possible that the objects
           in the folder are arranged.
        """
        self.origin = Path(origin)
        self.destination = Path(dest)
        self.verbose = verbose
        self.count = 1 if number is None or number <= 0 else number

        self.jobs = 1 if jobs < 2 else jobs
        self.files = set()
        self.__files(sort=sort)

    def __files(self, sort):
        """create the file list. pleae keep in mind, that it can
           take longer if you tr to check if the
           files allready exists."""
        for src_dir, _, files in os.walk(self.origin):

            dst_dir = Path(
                src_dir.replace(str(self.origin), str(self.destination), 1))

            if not dst_dir.exists():
                if self.verbose:
                    print(f"{dst_dir} not exists")
                dst_dir.mkdir(parents=True, exist_ok=True)

            if sort:
                file_list = sorted(
                    files[:self.count] if len(files) >= self.count else files,
                    key=lambda path: path)
            else:
                file_list = files

            if len(file_list) == 0:
                print(f"{src_dir} is empty?")
                continue

            with tqdm(total=len(file_list)) as pbar:
                with ThreadPoolExecutor(max_workers=self.jobs) as ex:
                    futures = [
                        ex.submit(self.__add_file, file_, src_dir, dst_dir,
                                  pbar) for file_ in file_list
                    ]
                    for future in as_completed(futures):
                        future.result()

    def __add_file(self, file_, src_dir, dst_dir, pbar):
        """ add the file name to the list of files or
            continue with the next
        """
        src_file = Path(src_dir) / file_
        dst_file = dst_dir / file_

        if dst_file.is_file():
            if not compair(src_file, dst_file, method="md5"):
                self.files.add(tuple((src_file, dst_file)))
        else:
            self.files.add(tuple((src_file, dst_file)))

        pbar.update(1)

    def __call__(self):
        """ call the copy in parallel or serial"""

        if self.files is None or len(self.files) == 0:
            return

        with tqdm(total=len(self.files)) as pbar:
            with ThreadPoolExecutor(max_workers=self.jobs) as ex:
                futures = [
                    ex.submit(copy_, file_, pbar) for file_ in self.files
                ]
                for future in as_completed(futures):
                    future.result()

    @staticmethod
    def large_file(src, dst):
        """ copy a large file py chunks """
        src = Path(src)
        dst = Path(dst)

        if not src.exists():
            print(errno.ENOENT, f'ERROR: file does not exist: "{str(src)}"')
            raise SystemExit()

        if dst.exists():
            os.remove(dst)

        if dst.exists():
            print(errno.EROFS,
                  f' ERROR: file exists, cannot overwrite it: "{str(dst)}"')
            raise SystemExit()

        chunk_size = Chunk(src, divisor=10e5).size

        try:
            with open(src, 'rb') as ifp:
                with open(dst, 'wb') as ofp:
                    chunk = ifp.read(chunk_size)
                    while chunk:
                        ofp.write(chunk)
                        chunk = ifp.read(chunk_size)

        except IOError as ioerr:
            print(f'ERROR: {ioerr}')
            raise SystemExit() from ioerr
