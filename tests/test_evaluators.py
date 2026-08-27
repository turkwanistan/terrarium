from evaluations.evaluate_behavior import evaluate as behavior
from evaluations.evaluate_technical import evaluate as technical
from evaluations.evaluate_spatial import evaluate as spatial


def test_behavior_evaluator_passes_reference_seed():
    assert behavior(1701,240)['passed']


def test_technical_evaluator_passes():
    assert technical(60)['passed']


def test_spatial_evaluator_passes_reference_seed():
    assert spatial(1701,500)["passed"]
