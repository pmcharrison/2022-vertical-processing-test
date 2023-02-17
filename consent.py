from dominate.tags import div, p, span, h1, strong, ul, li, em

from psynet.consent import NoConsent
from psynet.modular_page import ModularPage, CheckboxControl
from psynet.page import InfoPage
from psynet.timeline import Module, join

information_and_consent = div()

with information_and_consent:
    h1("Information sheet")
    p(
        """
        Thank you for your interest in taking part in this study. It will be looking at developing
        an accurate psychometric test of musical vertical processing ability in the general
        population. Your participation entails filling in a short form asking about a few basic
        personal details, general musical ability, and any conditions which may affect your
        performance in the test, followed by taking the vertical processing test, which will ask
        you to identify how many notes are in a played chord followed by singing the notes
        that you hear. There will be a short debrief at the end of the test.
        """
    )
    p(
        """
        You must be 18 or older to participate in this study. Your information and performance on the test will be kept strictly
        anonymous, and the recordings taken will only be used by the researchers – they will never be played in a public
        setting. If there are any questions in the questionnaire that you wish not to answer, you may simply omit them.
        If you wish to stop taking the test at any time, please simply close the tab in which the test is
        open. Please only take the test once.
        """
    )
    p(
        """
         By clicking onto the next page, you confirm that you give your full informed consent.
        """
    )


def consent():
    return Module(
        "consent",
        join(
            NoConsent(),
            InfoPage(information_and_consent, time_estimate=30),
        )
    )
