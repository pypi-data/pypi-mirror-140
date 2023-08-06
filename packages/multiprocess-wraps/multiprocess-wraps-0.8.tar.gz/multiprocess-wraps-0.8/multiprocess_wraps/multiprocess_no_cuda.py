
"""Class for multiprocessing WITHOUT CUDA."""

from .base_multiprocess import _BaseMultiprocess


class multiprocess_no_cuda(_BaseMultiprocess):
    def __init__(self, func, n_workers=4, **multi_kwargs):
        super().__init__(func, n_workers, **multi_kwargs)
