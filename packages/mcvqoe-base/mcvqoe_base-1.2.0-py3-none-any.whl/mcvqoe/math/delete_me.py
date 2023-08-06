# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 11:55:08 2021

@author: jkp4
"""
import numpy as np
import resample_techniques as rt
import mcvqoe.math
mu = 0
sig = 1
rng = np.random.default_rng()
N_tests = 1000
N = 50

results = []
for k in range(N_tests):
    if k % 50 == 0:
        print(f'{100*k/N_tests}% done')
    sample = rng.normal(mu, sig, N)
    obs = np.mean(sample)
    # ci, _ = rt.bootstrap_ci(sample)
    ci, _ = mcvqoe.math.bootstrap_ci(sample, method="p", R=1e4)
    if ci[0] <= mu and mu <= ci[1]:
        results.append(True)
    else:
        results.append(False)

print(f'Percent success: {np.mean(results)}')
