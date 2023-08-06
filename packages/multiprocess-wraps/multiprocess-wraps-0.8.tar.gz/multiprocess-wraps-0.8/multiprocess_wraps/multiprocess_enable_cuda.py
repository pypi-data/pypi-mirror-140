"""Class for multiprocessing WITH CUDA."""

import os
import multiprocessing as mp

from .base_multiprocess import _BaseMultiprocess

try:
    import torch
except ImportError:
    raise ImportError(f'No module of `torch`.')

class multiprocess_enable_cuda(_BaseMultiprocess):
    def __init__(self, func, n_workers=4, **multi_kwargs):
        # get and then set the gpu_ids
        gpu_ids = multi_kwargs.get('gpu_ids', '0')
        self.gpu_ids = list(map(lambda x: f'cuda:{x}', gpu_ids.split(',')))
        multi_kwargs.update(gpu_ids=self.gpu_ids)
        super().__init__(func, n_workers, **multi_kwargs)

        # check the cuda device
        if not torch.cuda.is_available():
            raise AssertionError(f'Try to use CUDA while no available CUDA'
                                f'devices.')

    def __call__(self, *args, **kwargs):
        """The main function to decorate the input function."""
        mp.set_start_method('spawn', force=True)
        results = super().__call__(*args, **kwargs)
        return results
