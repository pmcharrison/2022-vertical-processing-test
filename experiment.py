# pylint: disable=unused-import,abstract-method,unused-argument

import random

from flask import Markup

import psynet.experiment
from psynet.consent import MainConsent, NoConsent
from psynet.modular_page import PushButtonControl
from psynet.page import InfoPage, SuccessfulEndPage, ModularPage
from psynet.timeline import Timeline
from psynet.trial.static import StaticTrial, StaticNode, StaticTrialMaker
from psynet.utils import get_logger

from psynet.js_synth import JSSynth, Chord, StretchedTimbre

logger = get_logger()


nodes = [
    StaticNode(
        definition={
            "timbre": timbre,
            "presentation": presentation,
            "repetition": repetition,
        },
        block=presentation,
    )
    for timbre in ["stretched"]
    for presentation in ["dichotic", "diotic"]
    for repetition in range(25)
]

timbres = {
    "stretched": StretchedTimbre(
        attack=0.2,
        decay=0.1,
        sustain_amp=0.8,
        release=1.0
    ),
}


class ConsonanceTrial(StaticTrial):
    time_estimate = 5

    def finalize_definition(self, definition, experiment, participant):
        definition["duration"] = 1.8  # The original duration in Marjieh et al. was 1.3 s
        definition["lower_pitch"] = random.uniform(55, 65)
        definition["pitch_interval"] = random.uniform(11, 13.5)
        definition["upper_pitch"] = definition["lower_pitch"] + definition["pitch_interval"]

        if definition["presentation"] == "diotic":
            definition["lower_pan"] = 0
            definition["upper_pan"] = 0
        else:
            if random.choice([False, True]):
                definition["lower_pan"] = -1
                definition["upper_pan"] = 1
            else:
                definition["lower_pan"] = 1
                definition["upper_pan"] = -1

        return definition

    def show_trial(self, experiment, participant):
        return ModularPage(
            "chord_player",
            JSSynth(
                Markup("Please rate the sound for <strong>pleasantness</strong> on a scale from 1 to 7."),
                [
                    Chord(
                        [
                            self.definition["lower_pitch"],
                            self.definition["upper_pitch"],
                        ],
                        duration=self.definition["duration"],
                        pan=[
                            self.definition["lower_pan"],
                            self.definition["upper_pan"],
                        ],
                    )
                ],
                timbre=timbres[self.definition["timbre"]],
            ),
            PushButtonControl(
                choices=[1, 2, 3, 4, 5, 6, 7],
                labels=[
                    "(1) Very unpleasant",
                    "(2)",
                    "(3)",
                    "(4)",
                    "(5)",
                    "(6)",
                    "(7) Very pleasant",
                ],
                arrange_vertically=False,
            )
        )


class Exp(psynet.experiment.Experiment):
    label = "Dichotic stretching experiment"

    timeline = Timeline(
        NoConsent(),
        InfoPage(
            "Welcome to the experiment!",
            time_estimate=5,
        ),
        StaticTrialMaker(
            id_="consonance_main_experiment",
            trial_class=ConsonanceTrial,
            nodes=nodes,
            expected_trials_per_participant=len(nodes),
            max_trials_per_participant=len(nodes),
            recruit_mode="n_participants",
            allow_repeated_nodes=False,
            n_repeat_trials=0,
            balance_across_nodes=False,
            target_n_participants=50,
        ),
        SuccessfulEndPage(),
    )

    def __init__(self, session=None):
        super().__init__(session)
        self.initial_recruitment_size = (
            1
        )
