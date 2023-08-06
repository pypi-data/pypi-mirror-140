""" calculate blocksize for chunk. so it is dynamic"""
from pathlib import Path


class Chunk:
    """handle chunks"""
    def __init__(self, filepath: Path, divisor: int = 1000):
        self.file = Path(filepath)
        self.divisor = divisor

    @property
    def size(self):
        """ get chunksize """
        size = self.file.stat().st_size
        chunk_size = size / self.divisor
        while chunk_size == 0 and self.divisor > 0:
            self.divisor /= 10
            chunk_size = size / self.divisor
        return chunk_size
