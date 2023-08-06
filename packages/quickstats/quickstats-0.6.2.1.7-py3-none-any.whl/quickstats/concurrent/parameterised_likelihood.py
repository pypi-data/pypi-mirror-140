import os
import sys
import copy
import json
from typing import Optional, Union, Dict, List, Any
from itertools import repeat

import pandas as pd

import ROOT
from quickstats import semistaticmethod
from quickstats.parsers import ParamParser
from quickstats.concurrent import ParameterisedRunner
from quickstats.components import Likelihood
from quickstats.utils.common_utils import batch_makedirs
from quickstats.maths.numerics import pretty_value

class ParameterisedLikelihood(ParameterisedRunner):
    def __init__(self, input_file:str, param_expr:str,
                 data_name:str="combData", config:Optional[Dict]=None,
                 outdir:str="output", outname:str="{poi_names}.json",
                 cache:bool=True, save_log:bool=True, parallel:int=-1,
                 verbosity:Optional[Union[int, str]]="INFO"):
        
        super().__init__(file_expr=None, param_expr=param_expr,
                         parallel=parallel, timed=True, save_log=save_log,
                         cache=cache, verbosity=verbosity)
        
        self.attributes = {
            'input_file': input_file,
            'data_name': data_name,
            'config': config,
            'outdir': outdir,
            'outname': outname
        }
        
        self.attributes['poi_name'] = ParamParser._get_param_str_attributes(param_expr)

    def _prerun_batch(self):
        outdir = self.attributes['outdir']
        cache_dir = self.get_cache_dir()
        batch_makedirs([outdir, cache_dir])
    
    @semistaticmethod
    def _prerun_instance(self, filename:str, mode:int, poi_val:Optional[Union[float, Dict[str, float]]]=None, **kwargs):
        if mode == 2:
            param_str = "("+ParamParser.val_encode_parameters(poi_val)+")"
            self.stdout.info(f"INFO: Evaluating conditional NLL {param_str} for the workspace {filename}")
        elif mode == 1:
            self.stdout.info(f"INFO: Evaluating unconditional NLL for the workspace {filename}")
    
    @semistaticmethod
    def _cached_return(self, outname:str):
        with open(outname, 'r') as f:
            likelihood = json.load(f)
            if 'uncond_fit' in likelihood:
                return likelihood['uncond_fit']['nll']
            elif 'cond_fit' in likelihood:
                return likelihood['cond_fit']['nll']
            else:
                raise RuntimeError("unexpected output (expect only conditional/unconditional fit in each task)")
    
    @semistaticmethod
    def _run_instance(self, filename:str, mode:int,
                      poi_name:Optional[Union[str, List[str]]]=None,
                      poi_val:Optional[Union[float, Dict[str, float]]]=None,
                      data_name:str="combData",
                      config:Optional[Dict]=None,
                      outname:Optional[str]=None,
                      **kwargs):
        try:
            if mode not in [1, 2]:
                error_msg = "only unconditional/conditional fit is allowed in parameterised likelihood runner"
                self.stdout.error(error_msg)
                raise RuntimeError(error_msg)
            if config is None:
                config = {}
            verbosity = config.pop("verbosity", "INFO")
            do_minos = config.pop("do_minos", False)
            likelihood = Likelihood(filename=filename, poi_name=poi_name, data_name=data_name, 
                                    config=config, verbosity=verbosity)
            fit_result = likelihood.nll_fit(poi_val, mode=mode, do_minos=do_minos)
            # save results
            if outname is not None:
                with open(outname, 'w') as outfile:
                    json.dump(fit_result, outfile)
                print('INFO: Saved NLL result to {}'.format(outname))
            if mode == 1:
                return fit_result['uncond_fit']['nll']
            elif mode == 2:
                return fit_result['cond_fit']['nll']
        except:
            return None
        
    def get_cache_dir(self):
        return os.path.join(self.attributes['outdir'], 'cache')
    
    def prepare_task_inputs(self):
        
        poi_names = self.attributes['poi_name']
        if len(poi_names) == 0:
            raise RuntimeError("no POI(s) to scan for")
            
        input_file = self.attributes['input_file']
        cache_dir  = self.get_cache_dir()
        outname    = "{param_str}.json"
        param_points = self.get_param_points(input_file)
        param_data = self.get_serialised_param_data(param_points, outdir=cache_dir, outname=outname)
        
        # None is for unconditional NLL
        poi_values = [None]
        # 1 is for unconditional NLL, 2 is for conditional NLL
        modes = [1] + [2]*len(param_points)
        
        for param_point in param_points:
            poi_values.append(param_point['internal_parameters'])
            
        outname_uncond = os.path.join(cache_dir, "{}_uncond.json".format("_".join(poi_names)))
        param_dpd_kwargs = {
            'poi_val': poi_values,
            'mode': modes,
            'outname': [outname_uncond] + param_data['outnames']
        }
        
        filename = list(set(param_data['filenames']))
        
        if len(filename) != 1:
            raise RuntimeError("multiple input files detected: {}".format(", ".join(filename)))
            
        param_ind_kwargs = {
            'filename': filename[0],
            'poi_name': self.attributes['poi_name'],
            'data_name': self.attributes['data_name'],
            'config': self.attributes['config']
        }
        
        self.set_param_ind_kwargs(**param_ind_kwargs)
        self.set_param_dpd_kwargs(**param_dpd_kwargs)
        kwarg_set = self.create_kwarg_set()
        auxiliary_args = {
            'points': poi_values
        }
        return kwarg_set, auxiliary_args
    
    def postprocess(self, raw_result, auxiliary_args:Optional[Dict]=None):
        points = auxiliary_args['points']
        for nll, poi_values in zip(raw_result, points):
            if nll is None:
                if poi_values is None:
                    raise RuntimeError(f'NLL evaluation failed for the unconditional fit. '
                                       'Please check the log file for more details.')
                else:
                    param_str = parser.val_encode_parameters(poi_values)
                    raise RuntimeError(f'NLL evaluation failed for the conditional fit ({param_str}).'
                                       'Please check the log file for more details.')
        uncond_nll = raw_result[0]
        data = {'nll':[], 'qmu':[]}
        for nll in raw_result:
            data['nll'].append(nll)
            data['qmu'].append(2*(nll-uncond_nll))
        # only 1 POI
        if len(self.attributes['poi_name']) == 1:
            poi_name = self.attributes['poi_name'][0]
            data['mu'] = []
            for poi_values in points:
                mu = pretty_value(poi_values[poi_name]) if poi_values is not None else None
                data['mu'].append(mu)
        # multi POI case
        else:
            for poi_name in self.attributes['poi_name']:
                data[poi_name] = []
                for poi_values in points:
                    mu = pretty_value(poi_values[poi_name]) if poi_values is not None else None
                    data[poi_name].append(mu)
        outdir  = self.attributes['outdir']
        outname = self.attributes['outname'].format(poi_names="_".join(self.attributes['poi_name']))
        outpath = os.path.join(outdir, outname.format(poi_name=poi_name))
        with open(outpath, 'w') as outfile:
            json.dump(data, outfile, indent=3)