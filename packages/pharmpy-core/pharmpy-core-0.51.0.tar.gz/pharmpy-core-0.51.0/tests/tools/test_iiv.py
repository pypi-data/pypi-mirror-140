from io import StringIO

from pharmpy import Model
from pharmpy.modeling import add_peripheral_compartment, set_zero_order_elimination
from pharmpy.tools.iiv.algorithms import _get_possible_iiv_blocks
from pharmpy.tools.iiv.tool import _add_iiv


def test_get_iiv_combinations_4_etas(testdata, pheno_path):
    model = Model.create_model(
        StringIO(
            '''
$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN1 TRANS2

$PK
CL=THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V*EXP(ETA(3))*EXP(ETA(4))

$ERROR
Y=F+F*EPS(1)

$THETA (0,0.00469307) ; TVCL
$THETA (0,1.00916) ; TVV
$OMEGA DIAGONAL(4)
 0.0309626  ;       IVCL
 0.031128  ;        IVV
 0.031128
 0.031128
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
'''
        )
    )

    model.path = testdata / 'nonmem' / 'pheno.mod'  # To be able to find dataset

    iiv_single_block, iiv_multi_block = _get_possible_iiv_blocks(model)

    assert iiv_single_block == [
        ['ETA(1)', 'ETA(2)'],
        ['ETA(1)', 'ETA(3)'],
        ['ETA(1)', 'ETA(4)'],
        ['ETA(2)', 'ETA(3)'],
        ['ETA(2)', 'ETA(4)'],
        ['ETA(3)', 'ETA(4)'],
        ['ETA(1)', 'ETA(2)', 'ETA(3)'],
        ['ETA(1)', 'ETA(2)', 'ETA(4)'],
        ['ETA(1)', 'ETA(3)', 'ETA(4)'],
        ['ETA(2)', 'ETA(3)', 'ETA(4)'],
        ['ETA(1)', 'ETA(2)', 'ETA(3)', 'ETA(4)'],
    ]

    assert iiv_multi_block == [
        [['ETA(1)', 'ETA(2)'], ['ETA(3)', 'ETA(4)']],
        [['ETA(1)', 'ETA(3)'], ['ETA(2)', 'ETA(4)']],
        [['ETA(1)', 'ETA(4)'], ['ETA(2)', 'ETA(3)']],
    ]


def test_get_iiv_combinations_5_etas(testdata, pheno_path):
    model = Model.create_model(
        StringIO(
            '''
$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN1 TRANS2

$PK
CL=THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V*EXP(ETA(3))*EXP(ETA(4))*EXP(ETA(5))

$ERROR
Y=F+F*EPS(1)

$THETA (0,0.00469307) ; TVCL
$THETA (0,1.00916) ; TVV
$OMEGA DIAGONAL(5)
 0.0309626  ;       IVCL
 0.031128  ;        IVV
 0.031128
 0.031128
 0.031128
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
'''
        )
    )

    model.path = testdata / 'nonmem' / 'pheno.mod'  # To be able to find dataset

    iiv_single_block, iiv_multi_block = _get_possible_iiv_blocks(model)

    assert iiv_single_block == [
        ['ETA(1)', 'ETA(2)'],
        ['ETA(1)', 'ETA(3)'],
        ['ETA(1)', 'ETA(4)'],
        ['ETA(1)', 'ETA(5)'],
        ['ETA(2)', 'ETA(3)'],
        ['ETA(2)', 'ETA(4)'],
        ['ETA(2)', 'ETA(5)'],
        ['ETA(3)', 'ETA(4)'],
        ['ETA(3)', 'ETA(5)'],
        ['ETA(4)', 'ETA(5)'],
        ['ETA(1)', 'ETA(2)', 'ETA(3)'],
        ['ETA(1)', 'ETA(2)', 'ETA(4)'],
        ['ETA(1)', 'ETA(2)', 'ETA(5)'],
        ['ETA(1)', 'ETA(3)', 'ETA(4)'],
        ['ETA(1)', 'ETA(3)', 'ETA(5)'],
        ['ETA(1)', 'ETA(4)', 'ETA(5)'],
        ['ETA(2)', 'ETA(3)', 'ETA(4)'],
        ['ETA(2)', 'ETA(3)', 'ETA(5)'],
        ['ETA(2)', 'ETA(4)', 'ETA(5)'],
        ['ETA(3)', 'ETA(4)', 'ETA(5)'],
        ['ETA(1)', 'ETA(2)', 'ETA(3)', 'ETA(4)'],
        ['ETA(1)', 'ETA(2)', 'ETA(3)', 'ETA(5)'],
        ['ETA(1)', 'ETA(2)', 'ETA(4)', 'ETA(5)'],
        ['ETA(1)', 'ETA(3)', 'ETA(4)', 'ETA(5)'],
        ['ETA(2)', 'ETA(3)', 'ETA(4)', 'ETA(5)'],
        ['ETA(1)', 'ETA(2)', 'ETA(3)', 'ETA(4)', 'ETA(5)'],
    ]

    assert iiv_multi_block == [
        [['ETA(1)', 'ETA(2)'], ['ETA(3)', 'ETA(4)', 'ETA(5)']],
        [['ETA(1)', 'ETA(3)'], ['ETA(2)', 'ETA(4)', 'ETA(5)']],
        [['ETA(1)', 'ETA(4)'], ['ETA(2)', 'ETA(3)', 'ETA(5)']],
        [['ETA(1)', 'ETA(5)'], ['ETA(2)', 'ETA(3)', 'ETA(4)']],
        [['ETA(2)', 'ETA(3)'], ['ETA(1)', 'ETA(4)', 'ETA(5)']],
        [['ETA(2)', 'ETA(4)'], ['ETA(1)', 'ETA(3)', 'ETA(5)']],
        [['ETA(2)', 'ETA(5)'], ['ETA(1)', 'ETA(3)', 'ETA(4)']],
        [['ETA(3)', 'ETA(4)'], ['ETA(1)', 'ETA(2)', 'ETA(5)']],
        [['ETA(3)', 'ETA(5)'], ['ETA(1)', 'ETA(2)', 'ETA(4)']],
        [['ETA(4)', 'ETA(5)'], ['ETA(1)', 'ETA(2)', 'ETA(3)']],
    ]


def test_add_iiv(pheno_path):
    model = Model.create_model(pheno_path)
    set_zero_order_elimination(model)
    _add_iiv(iiv_as_fullblock=False, model=model)
    iivs = set(model.random_variables.iiv.names)
    assert iivs == {'ETA(1)', 'ETA(2)', 'ETA_KM'}
    add_peripheral_compartment(model)
    _add_iiv(iiv_as_fullblock=False, model=model)
    iivs = set(model.random_variables.iiv.names)
    assert iivs == {'ETA(1)', 'ETA(2)', 'ETA_KM', 'ETA_VP1', 'ETA_QP1'}

    model = Model.create_model(pheno_path)
    set_zero_order_elimination(model)
    add_peripheral_compartment(model)
    _add_iiv(iiv_as_fullblock=True, model=model)
    iivs = set(model.random_variables.iiv.names)
    assert iivs == {'ETA(1)', 'ETA(2)', 'ETA_KM', 'ETA_VP1', 'ETA_QP1'}
    eta1_joint_names = model.random_variables['ETA(1)'].joint_names
    assert set(eta1_joint_names) == {'ETA(1)', 'ETA(2)', 'ETA_KM', 'ETA_VP1', 'ETA_QP1'}
