"""
Method MLM.
Code to run the Multivariate Linear Model (MLM) method.
"""

import numpy as np
import pandas as pd

from .pre import extract, match, rename_net, get_net_mat, filt_min_n

from anndata import AnnData
from scipy import stats

from tqdm import tqdm

import numba as nb


@nb.njit(nb.f4[:, :](nb.f4[:, :], nb.f4[:, :], nb.f4[:, :], nb.i4), parallel=True, cache=True)
def fit_mlm(X, y, inv, df):
    X = np.ascontiguousarray(X)
    n_samples = y.shape[1]
    n_fsets = X.shape[1]
    coef, _, _, _ = np.linalg.lstsq(X, y)
    sse = np.sum((X.dot(coef) - y)**2, axis=0) / df
    se = np.zeros((n_samples, n_fsets), dtype=nb.f4)
    for i in nb.prange(n_samples):
        se[i] = np.sqrt(np.diag(sse[i] * inv))
    t = coef.T/se
    return t.astype(nb.f4)


def mlm(mat, net, batch_size=10000, verbose=False):

    # Get number of batches
    n_samples = mat.shape[0]
    n_features, n_fsets = net.shape
    n_batches = int(np.ceil(n_samples / batch_size))

    # Add intercept to network
    net = np.column_stack((np.ones((n_features, ), dtype=np.float32), net))

    # Compute inv and df for lm
    inv = np.linalg.inv(np.dot(net.T, net))
    df = n_features - n_fsets

    # Init empty acts
    es = np.zeros((n_samples, n_fsets), dtype=np.float32)
    for i in tqdm(range(n_batches), disable=not verbose):

        # Subset batch
        srt, end = i*batch_size, i*batch_size+batch_size
        y = mat[srt:end].A.T

        # Compute MLM for batch
        es[srt:end] = fit_mlm(net, y, inv, df)[:, 1:]

    # Get p-values
    pvals = 2 * (1 - stats.t.cdf(np.abs(es), df))

    return es, pvals


def run_mlm(mat, net, source='source', target='target', weight='weight', batch_size=10000,
            min_n=5, verbose=False, use_raw=True):
    """
    Multivariate Linear Model (MLM).

    Wrapper to run MLM.

    Parameters
    ----------
    mat : list, pd.DataFrame or AnnData
        List of [features, matrix], dataframe (samples x features) or an AnnData instance.
    net : pd.DataFrame
        Network in long format.
    source : str
        Column name in net with source nodes.
    target : str
        Column name in net with target nodes.
    weight : str
        Column name in net with weights.
    batch_size : int
        Size of the samples to use for each batch. Increasing this will consume more memmory but it will run faster.
    min_n : int
        Minimum of targets per source. If less, sources are removed.
    verbose : bool
        Whether to show progress.
    use_raw : bool
        Use raw attribute of mat if present.

    Returns
    -------
    Returns mlm activity estimates and p-values or stores them in `mat.obsm['mlm_estimate']` and `mat.obsm['mlm_pvals']`.
    """

    # Extract sparse matrix and array of genes
    m, r, c = extract(mat, use_raw=use_raw, verbose=verbose)

    # Transform net
    net = rename_net(net, source=source, target=target, weight=weight)
    net = filt_min_n(c, net, min_n=min_n)
    sources, targets, net = get_net_mat(net)

    # Match arrays
    net = match(c, targets, net)

    if verbose:
        print('Running mlm on mat with {0} samples and {1} targets for {2} sources.'.format(m.shape[0], len(c), net.shape[1]))

    # Run MLM
    estimate, pvals = mlm(m, net, batch_size=batch_size, verbose=verbose)

    # Transform to df
    estimate = pd.DataFrame(estimate, index=r, columns=sources)
    estimate.name = 'mlm_estimate'
    pvals = pd.DataFrame(pvals, index=r, columns=sources)
    pvals.name = 'mlm_pvals'

    # AnnData support
    if isinstance(mat, AnnData):
        # Update obsm AnnData object
        mat.obsm[estimate.name] = estimate
        mat.obsm[pvals.name] = pvals
    else:
        return estimate, pvals
