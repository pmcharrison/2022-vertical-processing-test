# pylint: disable=unused-import,abstract-method,unused-argument
import json
import math
import random
import tempfile
import time
from statistics import mean

import psynet.experiment
from dallinger import db
from psynet.asset import ExperimentAsset, Asset, LocalStorage
from psynet.consent import NoConsent
from psynet.js_synth import JSSynth, Chord, InstrumentTimbre
from psynet.modular_page import PushButtonControl, AudioRecordControl, MusicNotationPrompt, SurveyJSControl, \
    RadioButtonControl, AudioMeterControl
from psynet.page import InfoPage, SuccessfulEndPage, ModularPage, VolumeCalibration
from psynet.timeline import Timeline, Module, CodeBlock, Event, ProgressDisplay, ProgressStage, join
from psynet.trial.static import StaticTrial, StaticNode, StaticTrialMaker
from psynet.utils import get_logger

from dominate import tags

from . import singing_analysis
from .consent import consent
from .utils import midi_to_abc

logger = get_logger()


with open("chord_types.json") as file:
    NODES = [
        StaticNode(
            definition={
                "chord_type": chord_type,
                "timbre_type": "same",
            },
        )
        for chord_type in json.load(file)
    ]


TRIALS_PER_PARTICIPANT = len(NODES)


PRACTICE_NODES = [
    StaticNode(
        definition={
            "chord_type": chord_type,
            "timbre_type": "same",
        }
    )
    for chord_type in [[0, 4], [0, 6]]
]


AVAILABLE_TIMBRES = [
    "piano",
    "flute",
    "trumpet",
    "saxophone",
]


VOCAL_RANGES = {
    "soprano": 69,
    "alto": 65,
    "tenor": 57,
    "bass": 52,
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

    wait_for_feedback = True
    show_running_total = False

    def show_feedback(self, experiment, participant):
        text = tags.div()
        with text:
            tags.p(f"You scored {self.var.score} out of 5.")

            if self.show_running_total:
                tags.p(f"Your running total is {participant.var.running_total}.")

            target_pitches_text, sung_pitches_text, abc = self.get_notation_for_feedback()
            tags.p(f"Target pitches = {target_pitches_text}, sung pitches = {sung_pitches_text}.")

        return ModularPage(
            "show_feedback",
            MusicNotationPrompt(abc, text=text),
            time_estimate=0,
        )

    def get_notation_for_feedback(self):
        target_pitches = self.definition["target_pitches"]
        transposition = target_pitches[0] - math.floor(target_pitches[0])  # Transpose down to the nearest integer
        target_pitches = [round(pitch - transposition) for pitch in target_pitches]
        target_pitches_text = ", ".join([f"{pitch}" for pitch in target_pitches])
        target_pitches_abc = midi_to_abc(target_pitches)

        sung_pitches = [pitch - transposition for pitch in self.var.sung_pitches]  # Apply the same transposition
        if len(sung_pitches) == 0:
            sung_pitches_text = "none"
        else:
            sung_pitches_text = ", ".join([f"{pitch:.2f}" for pitch in sung_pitches])
        sung_pitches_int = [round(pitch) for pitch in sung_pitches]
        sung_pitches_abc = midi_to_abc(
            sung_pitches_int)  # Warning: music21 errors seem to cause feedback page to be skipped

        abc = target_pitches_abc + " | " + sung_pitches_abc + "|\\nw: Target | Sung"
        if mean(target_pitches + sung_pitches) < 60:
            abc = "K: 1 clef=bass\\n" + abc

        return target_pitches_text, sung_pitches_text, abc

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


def requirements():
    html = tags.div()
    with html:
        tags.p(
            "For this experiment we need to you to be sitting in a quiet room with a good internet connection. "
            "If you can, please wear headphones or earphones for the best experience; "
            "however, we ask that you do not wear wireless headphones/earphones (e.g. EarPods), "
            "because they often introduce recording issues. "
            "If you are not able to satisfy these requirements currently, please do not take the test now "
            "but instead come back when you can."
        )

    return InfoPage(requirements, time_estimate=15)


def overview():
    html = tags.div()
    with html:
        tags.p("Thank you again for participating in this experiment. Your contribution is really appreciated!")

        tags.p(
            "The experiment has several components, which in total should take about 20 minutes. "
            "As part of it you will get your own 'vertical-processing ability' score, which you can compare "
            "with other people who took this test. "
            "These are the different components: "
        )

        tags.ol(
            tags.li("Equipment test;"),
            tags.li("Voice type assignment;"),
            tags.li("Instructions and practice;"),
            tags.li("Main test;"),
            tags.li("Questionnaire."),
        )

        tags.p(
            "By completing all of these components you will help us to acquire the best data for the further "
            "development of this test."
        )

    return InfoPage(html, time_estimate=20)


def equipment_test():
    # Ask about what equipment they are using
    return Module(
        "equipment_test",
        volume_calibration(),
        audio_output_question(),
        mic_test(),
        audio_input_question(),
    )


def audio_output_question():
    return ModularPage(
        "audio_output",
        prompt="What are you using to play sound?",
        control=RadioButtonControl(
            choices=["headphones", "earphones", "internal_speakers", "external_speakers"],
            labels=[
                "Headphones",
                "Earphones",
                "Internal computer speakers",
                "External computer speakers",
            ],
            show_free_text_option=True,
        ),
        time_estimate=7.5,
        save_answer="audio_output"
    )


def audio_input_question():
    return ModularPage(
        "audio_input",
        prompt="What are you using to record sound?",
        control=RadioButtonControl(
            choices=["headphones", "earphones", "internal_microphone", "external_microphone"],
            labels=[
                "Headphone microphone",
                "Earphone microphone",
                "Internal computer microphone",
                "External computer microphone",
            ],
            show_free_text_option=True,
        ),
        time_estimate=7.5,
        save_answer="audio_input"
    )


def volume_calibration():
    return ModularPage(
        "volume_calibration",
        JSSynth(
            "Please adjust your computer volume to a comfortable level where you can hear the chord clearly."
            [
                Chord(
                    [60, 64, 67],
                    duration=100000,
                )
            ],
            timbre=InstrumentTimbre("flute"),
        )
    )


def mic_test():
    return ModularPage(
        "mic_test",
        tags.div(
            tags.p(
                "Please try singing into the microphone. If your microphone is set up correctly, "
                "you should see the audio meter move. If it is not working, please update your audio settings and "
                "try again."
            ),
            tags.p(tags.strong("Tips:")),
            tags.p(tags.ul(
                tags.li("If you see a dialog box requesting microphone permissions, please click 'Accept'."),
                tags.li("If you think refreshing this page might help, do give it a try."),
            )),
        ),
        AudioMeterControl(),
    )


def instructions():
    html = tags.div()
    with html:
        tags.p(
            "This experiment tests your ability to 'hear out' the notes in musical chords. "
            "This is an important skill in many musical contexts from music performance to analytic listening."
        )
        tags.p(
            "In each trial of the experiment you will be played a chord comprising multiple notes. "
            "Your task is to sing these notes into the microphone, starting with the lowest and finishing with "
            "the highest."
        )


def get_voice_type():
    return Module(
        "get_voice_type",
        ModularPage(
            "get_voice_type",
            tags.p(
                "We'd like to play chords that fill well with your vocal range. ",
                "What voice type best describes you?"
            ),
            PushButtonControl(
                choices=["soprano", "alto", "tenor", "bass"],
                labels=[
                    "Soprano (high female voice)",
                    "Alto (low female voice)",
                    "Tenor (high male voice)",
                    "Bass (low male voice)",
                ],
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


def main():
    return StaticTrialMaker(
        id_="practice_trials",
        trial_class=VerticalProcessingTrial,
        nodes=PRACTICE_NODES,
        expected_trials_per_participant=2,
        max_trials_per_participant=2,
        allow_repeated_nodes=False,
        n_repeat_trials=0,
        balance_across_nodes=False,
    )


def main():
    return StaticTrialMaker(
        id_="main_trials",
        trial_class=VerticalProcessingTrial,
        nodes=NODES,
        expected_trials_per_participant=TRIALS_PER_PARTICIPANT,
        max_trials_per_participant=TRIALS_PER_PARTICIPANT,
        recruit_mode="n_participants",
        allow_repeated_nodes=False,
        n_repeat_trials=0,
        balance_across_nodes=False,
        target_n_participants=50,
    )


class Exp(psynet.experiment.Experiment):
    label = "Vertical processing experiment"
    asset_storage = LocalStorage()

    variables = {
        "show_bonus": False
    }

    timeline = Timeline(
        requirements(),
        consent(),
        overview(),
        equipment_test(),
        get_voice_type(),
        # To do - volume calibration, mic test, instructions, practice,
        instructions(),
        practice(),
        main(),
        questionnaire(),
        SuccessfulEndPage(),
    )
