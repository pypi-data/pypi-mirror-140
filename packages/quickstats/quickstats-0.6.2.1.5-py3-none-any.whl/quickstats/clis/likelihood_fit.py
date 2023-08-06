import os
import click

@click.command(name='likelihood_fit')
@click.option('-i', '--input_file', "filename", required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--outname', default='fit_result.json', show_default=True,
              help='Name of output.')
@click.option('--display/--no-display', default=True, show_default=True,
              help='Display fit result.')
@click.option('--save/--no-save', "save_result", default=False, show_default=True,
              help='Save fit result')
@click.option('--save_log/--skip_log', default=False, show_default=True,
              help='Save log file')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL (i.e. include systematics)')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use per parameter')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Convergence criterium')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level')
@click.option('--fix-cache/--no-fix-cache', default=True, show_default=True,
              help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-cache',  default=True, show_default=True,
              help='Fix MultiPdf level 2')
@click.option('--max_calls', type=int, default=-1, show_default=True,
              help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, show_default=True,
              help='Maximum number of Minuit iterations')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def likelihood_fit(**kwargs):
    """
    Perform likelihood fit on a workspace
    """
    _kwargs = {}
    for arg_name in ["outname", "save_log", "display", "save_result"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _init_kwargs = {}
    for arg_name in ["filename", "data_name", "verbosity"]:
        _init_kwargs[arg_name] = kwargs.pop(arg_name)
    _init_kwargs['config'] = kwargs
    from quickstats.components import AnalysisBase   
    if _kwargs['save_log']:
        from quickstats.concurrent.logging import standard_log
        log_path = os.path.splitext(_kwargs["outname"])[0] + ".log"
        with standard_log(log_path) as logger:
            analysis = AnalysisBase(**_init_kwargs)
            fit_result = analysis.nll_fit(mode=3)
        print(f"INFO: Saved fit log to `{log_path}`")
    else:
        analysis = AnalysisBase(**_init_kwargs)
        fit_result = analysis.nll_fit(mode=3)
    output = {}
    output['fit_result'] = fit_result
    df = {'pois':{}, 'nuisance_parameters':{}}
    analysis.load_snapshot("currentSnapshot")
    df['pois']['prefit'] = analysis.model.as_dataframe('pois')
    df['nuisance_parameters']['prefit'] = analysis.model.as_dataframe('nuisance_parameters')
    analysis.load_snapshot("nllFit")
    df['pois']['postfit'] = analysis.model.as_dataframe('pois')
    df['nuisance_parameters']['postfit'] = analysis.model.as_dataframe('nuisance_parameters')
    if _kwargs['display']:
        import pandas as pd
        pd.set_option('display.max_rows', None)
    for key in ['pois', 'nuisance_parameters']:
        df[key]['combined'] = df[key]['prefit'].drop(["value", "error"], axis=1)
        df[key]['combined']['value_prefit'] = df[key]['prefit']['value']
        df[key]['combined']['value_postfit'] = df[key]['postfit']['value']
        df[key]['combined']['error_prefit'] = df[key]['prefit']['error']
        df[key]['combined']['error_postfit'] = df[key]['postfit']['error']
        output[key] = df[key]['combined'].to_dict("list")
        if _kwargs['display']:
            print("{}:".format(key.title()))
            print(df[key]['combined'])
            print()
    if _kwargs['save_result']:
        import json
        with open(_kwargs["outname"], "w") as f:
            json.dump(output, f, indent=2)
        print(f"INFO: Saved fit result to `{_kwargs['outname']}`")