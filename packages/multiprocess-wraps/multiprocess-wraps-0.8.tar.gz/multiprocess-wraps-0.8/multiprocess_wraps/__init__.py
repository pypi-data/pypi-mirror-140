import functools
from .multiprocess_no_cuda import multiprocess_no_cuda
from .multiprocess_enable_cuda import multiprocess_enable_cuda

'''
def multiprocess(n_workers=4, **multi_kwargs):
    use_cuda = multi_kwargs.get('cuda', False)
    if not use_cuda:
        return multiprocess_no_cuda(n_workers, **multi_kwargs)
    return multiprocess_enable_cuda(n_workers, **multi_kwargs)
'''

class multiprocess():
    def __init__(self, func, n_workers=4, **multi_kwargs):
        self.n_workers = n_workers
        self.cuda = multi_kwargs.get('cuda', False)
        self.multi_kwargs = multi_kwargs

        if self.cuda:
            self.func = multiprocess_enable_cuda(func,
                                                 n_workers,
                                                 **multi_kwargs)
        else:
            self.func = multiprocess_no_cuda(func,
                                             n_workers,
                                             **multi_kwargs)
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)