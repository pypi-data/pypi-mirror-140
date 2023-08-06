#!/usr/bin/env python3
from .stats import calc_pvalues_mixture, calc_eff_sizes
from .models import ModelMixture
from .utils import get_params_at_slice, readjust_w
from pickle import load
import pandas as pd
import numpy as np
import os


__filenames = {
    'ref':
        {
            'params': 'ref_params.tsv',
            'stats': 'ref_stats.tsv',
            'result': 'ref_result.txt',
            'params_slices': 'ref_params_slices.tsv',
            'logpdf': 'ref_logpdf.pickle'
        },
    'alt':
        {
            'params': 'alt_params.tsv',
            'stats': 'alt_stats.tsv',
            'result': 'alt_result.txt',
            'params_slices': 'alt_params_slices.tsv',
            'logpdf': 'alt_logpdf.pickle'
        },
    'counts': 'stats.tsv'
    }



def calc_pvalue_and_es(ref_count: int, alt_count: int, params: dict,
                       w_ref: float, w_alt: float,
                       m: ModelMixture, _swap=False):
    n = max(ref_count, alt_count)
    try:
        mask_n = calc_pvalue_and_es._mask_n
        if mask_n < n:
            calc_pvalue_and_es._mask_n = n * 2
            mask_n = n * 2
    except AttributeError:
        calc_pvalue_and_es._mask_n = max(n, 200)
        mask_n = max(n, 200)
    if _swap:
        allele = 'alt'
        w = w_alt
    else:
        allele = 'ref'
        w = w_ref
    w = np.clip(w, 0.0, 1.0)
    ps = params[allele][m.bad]['params']['Estimate']
    pdict = get_params_at_slice(ps, alt_count)
    if w is not None:
        pdict['w'] = w
    pdict['w'] = readjust_w(m.dist, pdict, m.left, m.ps[0], m.ps[1])
    ps = m.dict_to_vec(pdict)
    data = np.array([[ref_count, 1]])
    es = calc_eff_sizes(m, data, ps)[0]
    pval = calc_pvalues_mixture(m, data, params=ps, mask_n=mask_n)[0]
    if _swap:
        return pval, es
    pval2, es2 = calc_pvalue_and_es(alt_count, ref_count, params, w_ref, w_alt,
                                    m,  _swap=True)
    if pval in (0.0, 1.0):
        es = None
    if pval2 in (0.0, 1.0):
        es2 = None
    return (pval, pval2), (es, es2)
    
        
        
def read_dist_from_folder(folder: str, filenames=__filenames):
    """
    Read betanegbinfit results folder into a dictionary.

    Parameters
    ----------
    folder : str
        Path to results folder.
    filenames : dict, optional
        Dictionary with mapping of certain types of data into filenames as
        produced by betanegbinfit. The default is __filenames.

    Returns
    -------
    results : dict
        Results.

    """
    
    results = dict()
    bads = dict()
    for f in filter(lambda x: x.startswith('BAD'), os.listdir(folder)):
        try:
            bad = float(f[3:])
            bads[bad] = os.path.join(folder, f)
        except ValueError:
            pass
    for allele in ('ref', 'alt'):
        d = dict()
        results[allele] = d
        fnames = filenames[allele]
        for bad, path in bads.items():
            dbad = dict()
            d[bad] = dbad
            dbad['params'] = pd.read_csv(os.path.join(path, fnames['params']),
                                         sep='\t', index_col=0).to_dict()
            for _, it in dbad['params'].items():
                for p, v in it.items():
                    try:
                        it[p] = float(v)
                    except ValueError:
                        try:
                            it[p] = bool(v)
                        except ValueError:
                            pass
            dbad['stats'] = pd.read_csv(os.path.join(path, fnames['stats']),
                                        sep='\t', index_col=0).to_dict()
            with open(os.path.join(path, fnames['logpdf']), 'rb') as f:
                dbad['logpdf'] = load(f)
            with open(os.path.join(path, fnames['result']), 'r') as f:
                dbad['model_name'] = f.readline().strip()
        print(d.keys())
    results['counts'] = pd.read_csv(os.path.join(path, filenames['counts']),
                                    header=None, sep='\t').values
    
    return results