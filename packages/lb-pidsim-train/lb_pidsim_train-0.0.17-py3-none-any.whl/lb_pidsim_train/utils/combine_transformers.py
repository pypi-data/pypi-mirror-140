#from __future__ import annotations

import numpy as np


def combine_transformers (transformers, variables) -> tuple:   # TODO add docstring
  if len(transformers) != len(variables):
    raise ValueError ("Transformers and variables length don't match.")

  unique_vars = list()
  unique_transformers = list ( np.unique (transformers) )
  for u_transf in unique_transformers:
    arranged_vars = list()
    for transf, var in zip (transformers, variables):
      if transf == u_transf:
        arranged_vars . append (var)
    unique_vars . append (arranged_vars)

  return unique_transformers, unique_vars
  