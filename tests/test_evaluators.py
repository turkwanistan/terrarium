from evaluations.evaluate_behavior import evaluate as behavior
from evaluations.evaluate_technical import evaluate as technical


def test_behavior_evaluator_passes_reference_seed():
    assert behavior(1701,240)['passed']


def test_technical_evaluator_passes():
    assert technical(60)['passed']
