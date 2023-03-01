from dominate import tags

from psynet.js_synth import Chord, InstrumentTimbre, JSSynth
from psynet.modular_page import ModularPage
from psynet.page import InfoPage
from psynet.timeline import join, MediaSpec, Event

html = tags.div()


def page_1():
    with html:
        tags.p(
            "This experiment tests your ability to 'hear out' the notes in musical chords. "
            "This is an important skill in many musical contexts from music performance to analytic listening."
        )

        tags.p(
            """
            You will hear a series of chords.
            After each chord, you will have to sing the notes in the chord back to the computer.
            Please sing each note for 1-2 seconds to the syllable of 'ta', leaving a small gap between each one. 
            Please sing each note at a steady pitch, try to avoid wobbling or sliding.
            When you've finished singing, press 'Next' to continue.
            """
        )

        tags.p(
            """
            Press 'Next' to hear an example.
            """
        )
    return InfoPage(html, time_estimate=7.5)


def page_2():
    return ModularPage(
        "example_trial",
        prompt=JSSynth(
            "For example, you might hear a chord like this, and sing the following response:",
            [
                Chord(
                    [47, 54],
                    duration=3.5,
                    # timbre="piano",
                )
            ],
            timbre=InstrumentTimbre(type="piano"),
        ),
        media=MediaSpec(
            audio={
                "sung_response": "static/example-trial.m4a"
            }
        ),
        time_estimate=7.5,
        events={
            "playSinging": Event(is_triggered_by="promptEnd", delay=0.5, js="psynet.audio.sung_response.play()"),
        }
    )


def instructions():
    return join(
        page_1(),
        page_2(),
    )
