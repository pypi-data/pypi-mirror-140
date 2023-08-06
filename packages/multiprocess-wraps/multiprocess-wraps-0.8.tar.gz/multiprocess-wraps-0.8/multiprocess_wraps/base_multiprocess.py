"""A package of decorators to use multiprocessing easily."""

import json
import functools
import multiprocessing as mp


def _exec(params, func):
    args, kwargs = params
    return func(*args, **kwargs)


class _BaseMultiprocess():
    def __init__(self, func, n_workers=4, **multi_kwargs):
        """Initialization function of base class of multiprocessing.
        
        Args:
            n_workers:     How many workers for multiprocessing. (default: 4)
            multi_kwargs:  Other configs for multiprocessing. (default: None)

        Raises:
            ValueError: An error occurred when `self._n_workers` less than 0.
        """

        self.func = func

        # Set worker number.
        self._n_workers = min(n_workers, mp.cpu_count())
        if self._n_workers <= 0:
            raise ValueError(f'The number of workers must be positive, '
                            f'however, n_workers={n_workers} received.')

        # Whether to print infos.
        self.verbose = multi_kwargs.get('verbose', False)

        # Update and save the configs.
        multiprocess_type = self.__class__.__name__
        multi_kwargs.update(
            func_name=func.__name__,
            n_workers=n_workers,
            multiprocess_type=multiprocess_type)
        self.multi_kwargs = multi_kwargs

        if self.verbose:
            infos = ''
            infos += '=====================Configs=====================\n'
            infos += json.dumps(multi_kwargs, indent=4).replace('"', '\'') + '\n'
            infos += '=====================Configs=====================\n'
            print(infos)

    @property
    def n_workers(self):
        return self._n_workers

    @staticmethod
    def _check_args(*args, **kwargs):
        """Check whether all input configs are of the same length."""
        all_args = list(args) + list(kwargs.values())
        length = list(set(map(len, all_args)))

        # Illegal configs.
        if len(length) > 1:
            return -1, False

        return length[0], True

    @staticmethod
    def _parameter_wraps(func):
        """Wrappers to re-organize parameters of functions.

        NOTICE: It is now ABANDONED!

        Since `multiprocessing.Pool.imap` receives only one parameter as input,
        one has to re-organize the parameters to a tuple of (args, kwargs).

        E.g.: For the following function:

        >>> def original_function(x, y, z=1, w=2):
        >>>     print(x, y, z, w)
        >>> args, kwargs = [1, 2], dict(z=5)
        >>> original_function(*args, **kwargs)
        >>> # (1, 2, 5, 2)  # output

        one can rewrite it using this decorator by

        >>> @parameter_wraps
        >>> def rewrited_function(x, y, z=1, w=2):
        >>>     print(x, y, z, w)
        >>> args, kwargs = [1, 2], dict(z=5)
        >>> packaged_params = (arg, kwargs)
        >>> rewrited_function(packaged_params)
        >>> # (1, 2, 5, 2)  # output
        """

        @functools.wraps(func)
        def _func(tuple_dict_params):
            args, kwargs = tuple_dict_params
            return func(*args, **kwargs)
        return _func

    def __call__(self, *args, **kwargs):
        """The main function to call the input function."""

        # Check the paramters.
        length, legal = self._check_args(*args, **kwargs)
        if not legal:
            raise AssertionError(f'All input parameters should be of the '
                                 f'the same length.')

        # Print infos if needed.
        if self.verbose:
            infos = ''
            infos += '====================Check Arg====================\n'
            infos += f'args: {args}  kwargs: {kwargs}\n'
            infos += f'length: {length}\n'
            infos += '====================Check Arg====================\n'
            print(infos)

        # The main iteration.
        results = []
        with mp.Pool(self.n_workers) as pool:
            for idx in range(length):
                arg = [x[idx] for x in args]
                kwarg = {k: v[idx] for k, v in kwargs.items()}
                result = pool.apply_async(self.func, args=arg, kwds=kwarg)
                results.append(result.get())
        return results
