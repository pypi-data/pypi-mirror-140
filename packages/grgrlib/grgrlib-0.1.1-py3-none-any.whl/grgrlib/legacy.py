#!/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt


def find_ss(
    ss_func,
    par,
    init_par,
    init_guess=None,
    ndim=None,
    max_iter=500,
    tol=None,
    method=None,
    debug=False,
):
    """Finds steady states for parameters give a set of parameters where the steady state is known. This is useful if you don't have a nice initial guess, but know some working parameters.
    ...

    Parameters
    ----------
    ss_func : callable
        A vector function to find a root of.
    par : list or ndarray
        Paramters for which you want to solve for the steady state
    init_par : list or ndarray
        Parameters for which you know that the steady state can be found given the initial guess `init_guess`
    init_guess : list or ndarray (optional)
        Initial guess which leads to the solution of the root problem of `ss_func` with `init_par`. Defaults to a vector of ones.
    ndim : dimensionality of problem (optional, only if `init_guess` is not given)
    max_iter : int
    debug : bool

    Returns
    -------
    list
        The root / steady state

    Raises
    -------
    ValueError
        If the given problem cannot be solved for the initial parameters and guess
    """
    import scipy.optimize as so

    # convert to np.arrays to allow for math
    par = np.array(par)
    cur_par = np.array(init_par)
    last_par = cur_par

    if init_guess is None:
        # very stupid first guess
        sval = np.ones(ndim)
    else:
        sval = init_guess

    cnt = 0

    if method is None:
        method = "hybr"

    if debug:
        res = so.root(lambda x: ss_func(x, list(cur_par)), sval, tol=tol, method=method)
        return res

    while last_par is not par:

        try:
            res = so.root(
                lambda x: ss_func(x, list(cur_par)), sval, tol=tol, method=method
            )
            suc = res["success"]
        except:
            # if this is not even evaluable set success to False manually
            suc = False

        if not suc:

            if cnt == 0:
                raise ValueError("Can not find steady state of initial parameters.")
            # if unsuccessful, chose parameters closer to last working parameters
            cur_par = 0.5 * last_par + 0.5 * cur_par

        else:
            # if successful, update last working parameter and try final paramter
            last_par = cur_par
            cur_par = par
            sval = res["x"]

        cnt += 1
        if cnt >= max_iter:
            print(
                "Steady state could not be found after %s iterations. Message from last attempt: %s"
                % (max_iter, res["message"])
            )
            break

    return res
