# This file is autogenerated with reference to psynet/resources/experiment_scripts/test.py.

# To run this test via Docker, run the following in your terminal:
#
# bash docker/run pytest test.py

# You can customize the behavior of the automated tests by overriding certain methods within
# your experiment class, located in experiment.py:
# - test_experiment
# - test_create_bots
# - test_run_bots
# - test_check_bots
# - test_check_bot

import os
import pytest

# from voice_leading import nonbijective_vl
from .scoring import score_response
# from experiment import VerticalProcessingTrial

pytest_plugins = ["pytest_dallinger", "pytest_psynet"]
experiment_dir = os.path.dirname(__file__)


@pytest.mark.parametrize("experiment_directory", [experiment_dir], indirect=True)
def test_experiment(launched_experiment):
    launched_experiment.test_experiment()


# def test_voice_leading():
#     assert get_minimal_voice_leading([60, 64, 67], [60, 64.5]) == [[60, 60], [64, 64.5], [67, 64.5]]
#
#     assert infer_target_pitches(target=[60, 64, 67], sung=[64.2, 67.1]) == [64, 67]
#     assert infer_target_pitches(target=[60, 64, 67], sung=[63.2, 64.2, 67.1], ) == [60, 64, 67]
#     assert infer_target_pitches(target=[60, 64, 67], sung=[50, 60.1, 64.2, 67.1]) == [None, 60, 64, 67]

# @pytest.mark.parametrize("experiment_directory", [experiment_dir], indirect=True)
def test_scoring():
    # The participant gets 1 point for every note in the chord (within 0.5 semitones accuracy),
    # but you can't sing the same note twice, and singing a note not in the chord loses you 0.5 points.
    assert score_response(target=[60, 64], response=[60, 64]) == 2
    assert score_response(target=[60, 64], response=[60, 65]) == 0.5
    assert score_response(target=[60, 64], response=[61]) == 0
    assert score_response(target=[60, 64], response=[60]) == 1
    assert score_response(target=[60, 64], response=[60, 60]) == 0.5

