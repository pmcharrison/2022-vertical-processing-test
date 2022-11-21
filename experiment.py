# pylint: disable=unused-import,abstract-method,unused-argument
import json
import random
from statistics import mean

from flask import Markup

import psynet.experiment
from psynet.consent import MainConsent, NoConsent
from psynet.modular_page import PushButtonControl
from psynet.page import InfoPage, SuccessfulEndPage, ModularPage
from psynet.timeline import Timeline, Module, CodeBlock
from psynet.trial.static import StaticTrial, StaticNode, StaticTrialMaker
from psynet.utils import get_logger

from psynet.js_synth import JSSynth, Chord, InstrumentTimbre

logger = get_logger()

with open("chord_types.json") as file:
    NODES = [
        StaticNode(
            definition={
                "chord_type": chord_type,
                "duration": 2.5,
                "roving_radius": 2.5,
                "timbres": ["piano"],
            },
        )
        for chord_type in json.load(file)
    ]

TIMBRES = {
    "piano": InstrumentTimbre(
        type="piano",
    ),
}

VOCAL_RANGES = {
    "Soprano": 69,
    "Alto": 65,
    "Tenor": 57,
    "Bass": 52,
}


class VerticalProcessingTrial(StaticTrial):
    time_estimate = 5

    def finalize_definition(self, definition, experiment, participant):
        mean_target_pitch = random.uniform(
            participant.var.vocal_centre - self.definition["roving_radius"],
            participant.var.vocal_centre + self.definition["roving_radius"]
        )

        mean_original_pitch = mean(definition["chord_type"])
        pitch_translation = mean_target_pitch - mean_original_pitch
        target_pitches = [p + pitch_translation for p in self.definition["chord_type"]]

        definition["mean_target_pitch"] = mean_target_pitch
        definition["target_pitches"] = target_pitches

        return definition

    def show_trial(self, experiment, participant):
        timbre = [TIMBRES[timbre] for timbre in self.definition["timbres"]]

        return ModularPage(
            "vertical_processing_page",
            JSSynth(
                Markup("Please rate the sound for <strong>pleasantness</strong> on a scale from 1 to 7."),
                [
                    Chord(
                        self.definition["target_pitches"],
                        duration=self.definition["duration"],
                        timbre=timbre,
                    )
                ],
                timbre=timbre,
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

def get_voice_type():
    return Module(
        "get_voice_type",
        ModularPage(
            "get_voice_type",
            "What voice type best describes you?",
            PushButtonControl(
                [
                    "Soprano",
                    "Alto",
                    "Tenor",
                    "Bass",
                ]
            ),
            time_estimate=5,
            save_answer="voice_type"
        ),
        CodeBlock(lambda participant: participant.var.set(
                "vocal_centre",
                VOCAL_RANGES[participant.var.voice_type],
            )
        )
    )

class Exp(psynet.experiment.Experiment):
    label = "Vertical processing experiment"

    timeline = Timeline(
        NoConsent(),
        InfoPage(
            "Welcome to the experiment!",
            time_estimate=5,
        ),
        get_voice_type(),
        StaticTrialMaker(
            id_="consonance_main_experiment",
            trial_class=VerticalProcessingTrial,
            nodes=NODES,
            expected_trials_per_participant=len(NODES),
            max_trials_per_participant=len(NODES),
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
