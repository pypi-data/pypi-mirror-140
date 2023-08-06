# -*- coding: utf-8 -*-
"""Custom pyro-compatiable distribution"""
from jax.scipy.special import betaln, gammaln
from jax import lax, random, jit, vmap
from .betainc import betainc, logbetainc
import jax.numpy as jnp
from scipy.stats import nbinom as scipy_nb, beta
from scipy.special import betaincinv
from functools import partial
from abc import abstractmethod


class Distribution():
    @staticmethod
    @abstractmethod
    def sample(size: int, **kwargs) -> jnp.ndarray:
        pass
    
    @staticmethod
    @abstractmethod
    def logprob(data: jnp.ndarray, **kwargs) -> jnp.ndarray:
        pass
    
    @staticmethod
    @abstractmethod
    def mean(**kwargs):
        pass
    
    @abstractmethod
    def cdf(**kwargs):
        pass
    
    @abstractmethod
    def sf(**kwargs):
        pass
    

class NB(Distribution):
    @staticmethod
    def sample(r, p, size):
        return scipy_nb.rvs(n=r, p=1.0 - p, size=size)

    @staticmethod
    @jit
    def logprob(x, r, p):
        p = r * jnp.log(p) + x * jnp.log1p(-p)
        return p  + gammaln(x + r) - gammaln(r) - gammaln(x + 1.0)

    @staticmethod
    def mean(r, p):
        return (1.0 - p) * r / p
    
    @staticmethod
    def cdf(x, r, p):
        return betainc(r, x + 1.0, p)

    @staticmethod
    def sf(x, r, p):
        return betainc(x + 1.0, r, 1.0 - p)

    @staticmethod
    def logsf(x, r, p):
        return logbetainc(x + 1.0, r, 1.0 - p)
    
class LeftTruncatedNB(NB):
    def __init__(self, r, probs, left=5, validate_args=None):
        self.left = left
        self.left_vals = jnp.arange(1, left)
        super().__init__(r, probs, validate_args=validate_args)

    @staticmethod
    def sample(r, p, left, size: int):
        raise NotImplementedError

    @staticmethod
    @partial(jit, static_argnames=('left'))
    def logprob(x, r, p, left):
        left = float(left)
        logprob = super(LeftTruncatedNB, LeftTruncatedNB).logprob
        lp = jnp.where(x <= left, -jnp.inf, logprob(x, r, p))
        lp = logprob(x, r, p) - jnp.log1p(-sum(jnp.exp(logprob(i, r, p))
                                               for i in range(int(left) + 1)))
        return jnp.where(x <= left, -jnp.inf, lp)

    @staticmethod
    def mean(r, p, left):
        s = super(LeftTruncatedNB, LeftTruncatedNB)
        m = s.mean(r, p) 
        m -= sum(i * jnp.exp(s.logprob(i, r, p)) for i in range(1, left + 1)) 
        return m / s.sf(left, r, p)

    @staticmethod
    def cdf(x, r, p, left):
        raise NotImplementedError

    @staticmethod
    def sf(x, r, p, left):
        raise NotImplementedError



class BetaNB(Distribution):
    @staticmethod
    def sample(mu, concentration, r, size: int):
        a = mu * concentration
        b = (1.0 - mu) * concentration
        p = beta.rvs(a, b, size=size)
        return scipy_nb.rvs(n=r, p=p)

    @staticmethod
    @jit
    def logprob(x, mu, concentration, r):
        a = mu * concentration
        b = (1.0 - mu) * concentration
        return betaln(a + r, b + x) - betaln(a, b) + gammaln(r + x) -\
               gammaln(x + 1.0) - gammaln(r)

    @staticmethod
    def mean(mu, concentration, r):
        a = mu * concentration
        b = (1.0 - mu) * concentration
        return r * b / (a - 1)
    
    @staticmethod
    def cdf(x, mu, concentration, r):
        return sum(jnp.exp(BetaNB.logprob(i, mu, concentration, r))
                   for i in range(x + 1))

    @staticmethod
    def sf(x, mu, concentration, r):
        return 1.0 - BetaNB.cdf(x, mu, concentration, r)
        
    


class LeftTruncatedBetaNB(BetaNB):
    def __init__(self, r, mu, concentration, left, validate_args=None):
        self.left_vals = jnp.arange(0, left + 1)
        self.left = left
        super().__init__(r, mu, concentration, validate_args=validate_args)

    @staticmethod
    def sample(r, mu, concentration, left, size: int):
        raise NotImplementedError

    @staticmethod
    @partial(jit, static_argnames=('left',))
    def logprob(x, mu, concentration, r, left=4):
        s = super(LeftTruncatedBetaNB, LeftTruncatedBetaNB)
        cdf = s.cdf
        logprob = s.logprob
        sm = -cdf(left, mu, concentration, r)
        lp = jnp.where(x <= left, -jnp.inf, logprob(x, mu, concentration, r))
        return lp - jnp.log1p(sm)

    @staticmethod
    def mean(mu, concentration, r, left):
        s = super(LeftTruncatedBetaNB, LeftTruncatedBetaNB)
        m = s.mean(mu, concentration, r) 
        return (m - sum(i * jnp.exp(s.logprob(i, mu, concentration, r))
                       for i in range(1, left + 1))) / s.sf(left, mu,
                                                            concentration, r)