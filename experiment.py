# pylint: disable=unused-import,abstract-method,unused-argument
import json
import math
import random
import tempfile
import time
from statistics import mean

import psynet.experiment

from psynet.asset import DebugStorage, ExperimentAsset, Asset
from psynet.consent import NoConsent
from psynet.js_synth import JSSynth, Chord, InstrumentTimbre
from psynet.modular_page import PushButtonControl, AudioRecordControl, MusicNotationPrompt
from psynet.page import InfoPage, SuccessfulEndPage, ModularPage
from psynet.timeline import Timeline, Module, CodeBlock, Event, ProgressDisplay, ProgressStage
from psynet.trial.static import StaticTrial, StaticNode, StaticTrialMaker
from psynet.utils import get_logger

from dallinger import db

from .utils import midi_to_abc
from . import singing_analysis

logger = get_logger()


with open("chord_types.json") as file:
    NODES = [
        StaticNode(
            definition={
                "chord_type": chord_type,
                "timbre_type": timbre_type,
            },
        )
        for chord_type in json.load(file)
        for timbre_type in ["same"]
    ]

AVAILABLE_TIMBRES = [
    "piano",
    "flute",
    "trumpet",
    "saxophone",
]

VOCAL_RANGES = {
    "Soprano": 69,
    "Alto": 65,
    "Tenor": 57,
    "Bass": 52,
}


class VerticalProcessingTrial(StaticTrial):
    time_estimate = 5

    def finalize_definition(self, definition, experiment, participant):
        n_pitches = len(definition["chord_type"])
        definition["chord_duration"] = 3.5  # How long is the chord? (seconds)
        definition["roving_radius"] = 1.0  # The centre pitch of the chord roves +/- this value in semitones
        definition["silence_duration"] = 0.5  # How long do we wait between the chord and the recording?
        definition["record_duration"] = 1.0 + n_pitches * 1.25  # How long is the recording?

        # definition["timbre"] = ["piano" for _ in definition["chord_type"]]

        if definition["timbre_type"] == "same":
            _timbre = random.choice(AVAILABLE_TIMBRES)
            definition["timbre"] = [_timbre for _ in range(n_pitches)]
        else:
            assert definition["timbre_type"] == "different"
            definition["timbre"] = random.sample(AVAILABLE_TIMBRES, k=n_pitches)

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
        timbre_library = {
            timbre_label: InstrumentTimbre(
                type=timbre_label,
            )
            for timbre_label in self.definition["timbre"]
        }

        return ModularPage(
            "singing",
            JSSynth(
                "Sing back the notes in the chord in any order.",
                [
                    Chord(
                        self.definition["target_pitches"],
                        duration=self.definition["chord_duration"],
                        timbre=self.definition["timbre"],
                    ) 
                ],
                timbre=timbre_library,
            ),
            AudioRecordControl(
                duration=self.definition["record_duration"],
                bot_response_media="example_audio.wav",
            ),
            events={
                "recordStart": Event(
                    is_triggered_by="promptEnd",
                    delay=self.definition["silence_duration"],
                ),
                "submitEnable": Event(
                    is_triggered_by="recordEnd",
                ),
            },
            progress_display=ProgressDisplay(
                stages=[
                    ProgressStage(
                        self.definition["chord_duration"],
                        "Listen to the chord...",
                        color="green",
                    ),
                    ProgressStage(
                        self.definition["silence_duration"],
                        "Wait a moment...",
                        color="grey"
                    ),
                    ProgressStage(
                        self.definition["record_duration"],
                        "Sing back the chord!",
                        color="red",
                    ),
                    ProgressStage(
                        0.25,
                        "Click 'Next' when you are ready to continue.",
                        color="grey",
                        persistent=True,
                    )
                ]
            )
        )

    def show_feedback(self, experiment, participant):
        target_pitches = self.definition["target_pitches"]
        transposition = target_pitches[0] - math.floor(target_pitches[0])  # Transpose down to the nearest integer
        target_pitches = [round(pitch - transposition) for pitch in target_pitches]
        target_pitches_text = ", ".join([f"{pitch}" for pitch in target_pitches])
        target_pitches_abc = midi_to_abc(target_pitches)

        sung_pitches = [pitch - transposition for pitch in self.var.sung_pitches]  # Apply the same transposition
        sung_pitches_text = ", ".join([f"{pitch:.2f}" for pitch in sung_pitches])
        sung_pitches_int = [round(pitch) for pitch in sung_pitches]
        sung_pitches_abc = midi_to_abc(sung_pitches_int)  # Warning: music21 errors seem to cause feedback page to be skipped

        abc = target_pitches_abc + " | " + sung_pitches_abc + "|\\nw: Target | Sung"
        if mean(target_pitches + sung_pitches) < 60:
            abc = "K: 1 clef=bass\\n" + abc

        return ModularPage(
            "show_feedback",
            MusicNotationPrompt(
                abc,
                text=f"Target pitches = {target_pitches_text}, sung pitches = {sung_pitches_text}."
            ),
            time_estimate=0,
        )

    wait_for_feedback = True

    def async_post_trial(self):
        with tempfile.NamedTemporaryFile() as f_audio, tempfile.NamedTemporaryFile() as f_plot:
            try:
                self.assets["singing"].export(f_audio.name)
            except KeyError:
                # This is some debugging code that I inserted in order to track a rare error ####
                # It can be ignored unless this error recurs again in the future! ####
                logger.info(
                    "Failed to find self.assets['stimulus']. This error happens occasionally "
                    "and we haven't been able to debug it yet. It may be some kind of race condition. "
                    "We'll now print some debugging information to try and help solve this mystery. "
                )
                logger.info("Does our trial's node have pending async processes?")
                logger.info(self.node.async_processes)
                if len(self.node.async_processes) > 0:
                    logger.info([x.__json__() for x in self.node.async_processes])

                logger.info("What happens if we refresh the object?")
                db.session.refresh(self)
                logger.info(self.assets["stimulus"])

                logger.info("What happens if we perform a fresh database query?")
                asset = Asset.query.filter_by(trial_id=self.id).all()
                logger.info(asset)

                logger.info("How about waiting a bit?")
                time.sleep(0.5)

                logger.info("Another fresh database query?")
                asset = Asset.query.filter_by(trial_id=self.id).all()
                logger.info(asset)

                assert False, "Throw an error here so we can check the logs and learn what happened"
                ####

            result = singing_analysis.analyze_recording(
                f_audio.name,
                f_plot.name
            )
            self.var.sung_pitches = result["pitches"]
            self.var.singing_analysis = result["raw"]

            plot = ExperimentAsset(
                f_plot.name,
                parent=self,
                extension=".png",
            )
            plot.deposit()


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

    asset_storage = DebugStorage()

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
