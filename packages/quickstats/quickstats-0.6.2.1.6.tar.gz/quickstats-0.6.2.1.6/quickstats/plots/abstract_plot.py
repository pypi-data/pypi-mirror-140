from typing import Optional, Union, Dict, List, Tuple
from cycler import cycler

import matplotlib

from quickstats.plots.color_schemes import QUICKSTATS_PALETTES
from quickstats.plots.template import (single_frame, parse_styles, format_axis_ticks,
                                       parse_analysis_label_options)
from quickstats.utils.common_utils import combine_dict

class AbstractPlot:
    
    STYLES = {}
    
    COLOR_CYCLE = QUICKSTATS_PALETTES['default']
    
    COLOR_PALLETE = {}
    COLOR_PALLETE_SEC = {}
    
    CONFIG = {}
    
    def __init__(self,
                 color_pallete:Optional[Dict]=None,
                 color_pallete_sec:Optional[Dict]=None,
                 color_cycle:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None,
                 figure_index:Optional[int]=None,
                 config:Optional[Dict]=None):
        
        self.color_pallete = combine_dict(self.COLOR_PALLETE, color_pallete)
        self.color_pallete_sec = combine_dict(self.COLOR_PALLETE_SEC, color_pallete_sec)
            
        self.styles = combine_dict(self.STYLES, styles)
        self.styles = parse_styles(self.styles)
        
        if analysis_label_options is None:
            self.analysis_label_options = None
        else:
            self.analysis_label_options = parse_analysis_label_options(analysis_label_options)
            
        self.legend_order = self.get_default_legend_order()
        
        self.legend_data = {}
        self.legend_data_sec = {}
        
        self.figure_index = figure_index
        
        self.config = combine_dict(self.CONFIG)
        if config is not None:
            self.config = combine_dict(self.config, config)

        if color_cycle is None:
            self.prop_cycle = (cycler(color=self.COLOR_CYCLE))
        else:
            self.prop_cycle = (cycler(color=color_cycle))
        
    def get_default_legend_order(self):
        return []
    
    def update_legend_handles(self, handles:Dict, sec:bool=False):
        if not sec:
            legend_data = self.legend_data
        else:
            legend_data = self.legend_data_sec
            
        for key in handles:
            handle = handles[key]
            if isinstance(handle, matplotlib.container.Container):
                label = handle.get_label()
            elif isinstance(handle, (tuple, list)):
                label = handle[0].get_label()
            else:
                label = handle.get_label()               
            if label and not label.startswith('_'):
                legend_data[key] = {
                    'handle': handle,
                    'label': label
                }
            else:
                raise RuntimeError(f"the handle {handle} does not have an associated label")

    def get_legend_handles_labels(self, sec:bool=False):
        handles = []
        labels = []
        if not sec:
            legend_data = self.legend_data
        else:
            legend_data = self.legend_data_sec        
        for key in self.legend_order:
            if key in legend_data:
                handle = legend_data[key]['handle']
                label = legend_data[key]['label']
                handles.append(handle)
                labels.append(label)
        return handles, labels
    
    def draw_frame(self, frame_method=None, **kwargs):
        if frame_method is None:
            frame_method = single_frame
        ax = frame_method(styles=self.styles,
                          prop_cycle=self.prop_cycle,
                          analysis_label_options=self.analysis_label_options,
                          figure_index=self.figure_index,
                          **kwargs)
        self.figure = matplotlib.pyplot.gcf()
        return ax
    
    def draw_axis_labels(self, ax, xlabel:Optional[str]=None, ylabel:Optional[str]=None):
        if xlabel is not None:
            ax.set_xlabel(xlabel, **self.styles['xlabel'])
        if ylabel is not None:
            ax.set_ylabel(ylabel, **self.styles['ylabel'])
            
    def draw_axis_components(self, ax, xlabel:Optional[str]=None, ylabel:Optional[str]=None,
                             ylim:Optional[Tuple[float]]=None, xlim:Optional[Tuple[float]]=None):
        
        self.draw_axis_labels(ax, xlabel, ylabel)
        
        format_axis_ticks(ax, **self.styles['axis'],
                          xtick_styles=self.styles['xtick'],
                          ytick_styles=self.styles['ytick'])
        
        if ylim is not None:
            ax.set_ylim(*ylim)
        if xlim is not None:
            ax.set_xlim(*xlim)