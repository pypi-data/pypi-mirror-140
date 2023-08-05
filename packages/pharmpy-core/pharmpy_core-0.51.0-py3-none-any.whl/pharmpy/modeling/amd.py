from functools import partial

from pharmpy.results import Results
from pharmpy.workflows import default_tool_database

from .data import remove_loq_data
from .run import run_tool


class AMDResults(Results):
    def __init__(self, final_model=None):
        self.final_model = final_model


def run_amd(model, mfl=None, lloq=None, order=None):
    """Run Automatic Model Development (AMD) tool

    Runs structural modelsearch, IIV building, and resmod

    Parameters
    ----------
    model : Model
        Pharmpy model
    mfl : str
        MFL for search space for structural model
    lloq : float
        Lower limit of quantification. LOQ data will be removed.
    order : list
        Runorder of components

    Returns
    -------
    Model
        Reference to the same model object

    Examples
    --------
    >>> from pharmpy.modeling import *
    >>> model = load_example_model("pheno")
    >>> run_amd(model)      # doctest: +SKIP

    See also
    --------
    run_iiv
    run_tool

    """
    if lloq is not None:
        remove_loq_data(model, lloq=lloq)

    default_order = ['structural', 'iiv', 'residual']
    if order is None:
        order = default_order

    if mfl is None:
        mfl = (
            'ABSORPTION([ZO,SEQ-ZO-FO]);'
            'ELIMINATION([ZO,MM,MIX-FO-MM]);'
            'LAGTIME();'
            'TRANSITS([1,3,10],*);'
            'PERIPHERALS([1,2])'
        )

    run_funcs = []
    for section in order:
        if section == 'structural':
            func = partial(_run_modelsearch, mfl=mfl)
        elif section == 'iiv':
            func = _run_iiv
        elif section == 'residual':
            func = _run_resmod
        else:
            raise ValueError(
                f"Unrecognized section {section} in order. Must be one of {default_order}"
            )
        run_funcs.append(func)

    db = default_tool_database(toolname='amd')
    run_tool('modelfit', model, path=db.path / 'modelfit')

    next_model = model
    for func in run_funcs:
        next_model = func(next_model)

    res = AMDResults(final_model=next_model)
    return res


def _run_modelsearch(model, mfl):
    res_modelsearch = run_tool('modelsearch', 'exhaustive_stepwise', mfl=mfl, model=model)
    selected_model = res_modelsearch.best_model
    return selected_model


def _run_iiv(model):
    res_iiv = run_iiv(model)
    selected_iiv_model = res_iiv.best_model
    return selected_iiv_model


def _run_resmod(model):
    res_resmod = run_tool('resmod', model)
    selected_model = res_resmod.best_model
    res_resmod = run_tool('resmod', selected_model)
    selected_model = res_resmod.best_model
    res_resmod = run_tool('resmod', selected_model)
    selected_model = res_resmod.best_model
    return selected_model


def run_iiv(model, add_iivs=False, iiv_as_fullblock=False, rankfunc='ofv', cutoff=None):
    """Run IIV tool

    Runs two IIV workflows: testing the number of etas and testing which block structure

    Parameters
    ----------
    model : Model
        Pharmpy model
    add_iivs : bool
        Whether to add IIV on structural parameters. Default is False
    iiv_as_fullblock : bool
        Whether added etas should be as a fullblock. Default is False
    rankfunc : str
        Which ranking function should be used (OFV, AIC, BIC). Default is OFV
    cutoff : float
        Cutoff for which value of the ranking function that is considered significant. Default
        is 3.84

    Returns
    -------
    Model
        Reference to the same model object

    Examples
    --------
    >>> from pharmpy.modeling import *
    >>> model = load_example_model("pheno")
    >>> run_iiv(model)      # doctest: +SKIP

    See also
    --------
    run_amd
    run_tool

    """
    res_no_of_etas = run_tool(
        'iiv',
        'brute_force_no_of_etas',
        add_iivs=add_iivs,
        iiv_as_fullblock=iiv_as_fullblock,
        rankfunc=rankfunc,
        cutoff=cutoff,
        model=model,
    )
    res_block_structure = run_tool(
        'iiv',
        'brute_force_block_structure',
        rankfunc=rankfunc,
        cutoff=cutoff,
        model=res_no_of_etas.best_model,
    )

    from pharmpy.modeling import summarize_modelfit_results

    summary_models = summarize_modelfit_results(
        [model] + res_no_of_etas.models + res_block_structure.models
    )

    from pharmpy.tools.iiv.tool import IIVResults

    res = IIVResults(
        summary_tool=[res_no_of_etas.summary_tool, res_block_structure.summary_tool],
        summary_models=summary_models,
        best_model=res_block_structure.best_model,
        models=res_no_of_etas.models + res_block_structure.models,
        start_model=model,
    )

    return res
