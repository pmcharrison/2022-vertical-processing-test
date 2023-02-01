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
from psynet.demography.general import Age, Gender
from psynet.demography.gmsi import GMSI
from psynet.js_synth import JSSynth, Chord, InstrumentTimbre
from psynet.modular_page import PushButtonControl, AudioRecordControl, MusicNotationPrompt, SurveyJSControl, \
    RadioButtonControl, AudioMeterControl
from psynet.page import InfoPage, SuccessfulEndPage, ModularPage, VolumeCalibration
from psynet.timeline import Timeline, Module, CodeBlock, Event, ProgressDisplay, ProgressStage, join
from psynet.trial.static import StaticTrial, StaticNode, StaticTrialMaker
from psynet.utils import get_logger

from dominate import tags
from scipy import stats

from . import singing_analysis
from .consent import consent
from .scoring import score_response
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


TRIALS_PER_PARTICIPANT = 5 # for testing
# TRIALS_PER_PARTICIPANT = len(NODES)


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
    time_estimate = 15

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

        prompt = tags.div()

        with prompt:
            self.display_trial_position_alert()
            tags.p("Sing back the notes in the chord in any order.")

        return ModularPage(
            "singing",
            JSSynth(
                prompt,
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

    def display_trial_position_alert(self):
        with tags.em():
            # tags.attr(cls="alert alert-secondary")
            tags.p(
                "Trial ",
                tags.strong(self.position + 1),
                " out of ",
                tags.strong(self.expected_n_trials),
            )
    expected_n_trials = None
    wait_for_feedback = True
    show_running_score = False
    should_display_trial_position_alert = None

    def show_feedback(self, experiment, participant):
        score = self.score
        assert isinstance(score, (float, int))

        max_score = len(self.definition["chord_type"])

        if score == max_score:
            alert_type = "success"
        elif score == 0:
            alert_type = "danger"
        else:
            alert_type = "primary"

        text = tags.div()
        with text:
            if self.should_display_trial_position_alert:
                self.display_trial_position_alert()

            with tags.div():
                tags.attr(cls=f"alert alert-{alert_type}")
                tags.p(
                    "You scored ",
                    tags.strong(score),
                    " out of a possible ",
                    tags.strong(max_score),
                    " points.",
                )

                if self.show_running_score:
                    running_score = self.calculate_running_score(participant)
                    assert isinstance(running_score, (float, int))

                    tags.p(
                        "Your total score so far is ",
                        tags.strong(running_score),
                        "."
                    )

            target_pitches_text, sung_pitches_text, abc = self.get_notation_for_feedback()
            # tags.p(f"Target pitches = {target_pitches_text}, sung pitches = {sung_pitches_text}.")

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

    def score_answer(self, answer, definition):
        return score_response( 
            target=definition["target_pitches"],
            response=self.var.sung_pitches,
        )

    def calculate_running_score(self, participant):
        trials = self.__class__.query.filter_by(participant_id=participant.id).all()
        return sum([trial.score for trial in trials if trial.score is not None])


class PracticeVerticalProcessingTrial(VerticalProcessingTrial):
    show_running_score = False
    should_display_trial_position_alert = False
    expected_n_trials = 2


class MainVerticalProcessingTrial(VerticalProcessingTrial):
    show_running_score = True
    should_display_trial_position_alert = True
    expected_n_trials = TRIALS_PER_PARTICIPANT


def requirements():
    html = tags.div()
    with html:
        tags.p(
            "For this experiment we need to you to be sitting in a quiet room with a good internet connection. "
            "If you can, please wear headphones or earphones for the best experience; "
            "however, we ask that you do not wear wireless headphones/earphones (e.g. EarPods), "
            "because they often introduce recording issues. "
            "If you are not able to satisfy these requirements currently, please try again later."
        )

    return InfoPage(html, time_estimate=15)


def overview():
    html = tags.div()
    with html:
        tags.p("Thank you again for participating in this experiment. Your contribution is really appreciated!")

        tags.p(
            "The experiment has several components, which in total should take about 20 minutes:"
        )

        # tags.p("The sesssion will ")

        tags.ol(
            tags.li("Equipment test;"),
            tags.li("Voice type assignment;"),
            tags.li("Instructions and practice;"),
            tags.li("Main test;"),
            tags.li("Questionnaire."),
        )

        tags.p(
            "At the end you will get your own 'vertical-processing ability' score, which you can compare "
            "with other people who took this test. "
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
            "Please adjust your computer volume to a comfortable level where you can hear the chord clearly.",
            sequence=[
                Chord(
                    [60, 64, 67],
                    duration=3,
                )
            ] * 1000,
            timbre=InstrumentTimbre("flute"),
        ),
        time_estimate=10,
    )


def mic_test():
    html = tags.div()

    with html:
        tags.p(
            "Please try singing into the microphone. If your microphone is set up correctly, "
            "you should see the audio meter move. If it is not working, please update your audio settings and "
            "try again."
        )

        with tags.div():
            tags.attr(cls="alert alert-primary")
            tags.p(tags.ul(
                tags.li("If you see a dialog box requesting microphone permissions, please click 'Accept'."),
                tags.li("You can refresh the page if you like."),
            ))

    return ModularPage(
        "mic_test",
        html,
        AudioMeterControl(),
        time_estimate=10,
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
            "Your task is to sing these notes into the microphone in any order."
        )

    return InfoPage(
        html,
        time_estimate=15,
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


class VerticalProcessingTrialMaker(StaticTrialMaker):
    pass


class PracticeVerticalProcessingTrialMaker(VerticalProcessingTrialMaker):
    pass


class MainVerticalProcessingTrialMaker(VerticalProcessingTrialMaker):
    give_end_feedback_passed = True
    performance_check_type = "score"

    def get_end_feedback_passed_page(self, score):
        all_results = self.get_all_participant_performance_check_results()
        all_scores = [results["score"] for results in all_results if results["score"] is not None]
        percentile = stats.percentileofscore(all_scores, score)

        html = tags.div()
        with html:
            tags.p(
                "You finished the singing experiment! ",
                "Your total score was ",
                tags.strong(f"{score}"),
                f". This puts you in the top {100 - percentile:.0f}% of people who took the test so far."
            )

        return InfoPage(html, time_estimate=7.5)


def practice():
    html = tags.div()

    with html:
        tags.p(
            "We're now ready to try a couple of practice trials. "
            "Your score won't be counted here, it's just a chance to experience the paradigm."
        )
        with tags.div():
            tags.attr(cls="alert alert-warning")
            tags.strong("Please remember the following:")
            with tags.ul():
                tags.li("Sing each note to 'ta';")
                tags.li("Sing at a moderate tempo;")
                tags.li("Sing not too legato, not too staccato.")

    return join(
        InfoPage(html, time_estimate=5),
        PracticeVerticalProcessingTrialMaker(
            id_="practice_vertical_processing_trials",
            trial_class=PracticeVerticalProcessingTrial,
            nodes=PRACTICE_NODES,
            expected_trials_per_participant=2,
            max_trials_per_participant=2,
            allow_repeated_nodes=False,
            n_repeat_trials=0,
            balance_across_nodes=False,
        )
    )


def main():
    html = tags.div()

    with html:
        tags.p(
            "We're now ready to start the main experiment. "
            "You'll take ",
            tags.strong(TRIALS_PER_PARTICIPANT),
            " trials in total. Good luck!"
        )
        with tags.div():
            tags.attr(cls="alert alert-warning")
            tags.strong("Remember:")
            with tags.ul():
                tags.li("Sing each note to 'ta';")
                tags.li("Sing at a moderate tempo;")
                tags.li("Sing not too legato, not too staccato.")

    return join(
        InfoPage(html, time_estimate=5),
        MainVerticalProcessingTrialMaker(
            id_="main_vertical_processing_trials",
            trial_class=MainVerticalProcessingTrial,
            nodes=NODES,
            expected_trials_per_participant=TRIALS_PER_PARTICIPANT,
            max_trials_per_participant=TRIALS_PER_PARTICIPANT,
            recruit_mode="n_participants",
            allow_repeated_nodes=False,
            n_repeat_trials=0,
            balance_across_nodes=False,
            target_n_participants=50,
            check_performance_at_end=True,
        )
    )


def questionnaire():
    introduction_text = tags.div()
    with introduction_text:
        tags.p(
            "Before we finish, we just have a few more questions to ask you. ",
            "They should only take a couple of minutes to complete.",
        )
        tags.p(
            "None of these questions are about personal or sensitive topics. "
            "However, if you decide that you feel uncomfortable answering any of the questions, "
            "you may close the window and your preceding data will still be saved."
        )

    return join(
        InfoPage(
            introduction_text,
            time_estimate=5,
        ),
        Age(),
        Gender(),
        GMSI(subscales=[
            "Musical Training",
            "Perceptual Abilities",
            "Singing Abilities"
        ]),
        extra_questions(),
    )


def extra_questions():
    return ModularPage(
        "extra_questions",
        prompt="",
        control=SurveyJSControl({
            # "logoPosition": "right",
            "pages": [
                {
                    "name": "page1",
                    "elements": [
                        {
                         "type": "radiogroup",
                         "name": "absolute_pitch",
                         "title": "Do you have absolute pitch (a.k.a. perfect pitch)?",
                         "isRequired": True,
                         "choices": [
                              {
                               "value": "yes",
                               "text": "Yes"
                              },
                              {
                               "value": "no",
                               "text": "No"
                              },
                              {
                               "value": "not_known",
                               "text": "I don't know"
                              }
                         ],
                         # "showOtherItem": True
                        }
                    ]
                }
            ],
            # "showTitle": false,
            # "showQuestionNumbers": "off"
            }),
        time_estimate=20,
        bot_response={
            "absolute_pitch": "Yes"
        },
        save_answer="extra_questions",
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
        instructions(),
        practice(),
        main(),
        questionnaire(),
        SuccessfulEndPage(),
    )

    test_num_bots = 3

