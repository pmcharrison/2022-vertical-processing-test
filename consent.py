from dominate.tags import div, p, span, h1, strong, ul, li, em

from psynet.consent import NoConsent
from psynet.modular_page import ModularPage, CheckboxControl
from psynet.page import InfoPage
from psynet.timeline import Module, join

information_sheet = div()

with information_sheet:
    h1("Information sheet")
    p(
        """
        Before you decide to take part in this study it is important for you to understand why the research is being done
        and what it will involve. Please take time to read the following information carefully and discuss it with
        others if you wish.
        """
    )
    with p():
        strong("Purpose of the study.")
        span(
            """
            Music is a complex yet fascinating phenomenon that appears in all known cultures. As music psychologists, we
            want to understand the mental processes that underpin music listening and music creation. In this particular
            experiment, we are studying how melodies can elicit different emotions."
            """
        )

    with p():
        strong("Do I have to take part?")
        span(
            """
            Taking part is entirely voluntary. Refusal or withdrawal will involve no penalty or loss, now or in the
            future.
            """
        )

    with p():
        strong("How long does the experiment last?")
        span(
            """
            The full experiment should last approximately 20 minutes, though individual times will vary, and your
            experiment may end early depending on various factors.
            """
        )


# with pages[1]:
    with p():
        strong("Benefits of taking part.")
        span(
            """
            Completing the entire experiment earns you a payment of approximately £3.33. This fee is calculated by
            multiplying a notional hourly rate of £10.00/hour by the estimated duration of the experiment. However,
            please note the following:
            """
        )
        with ul():
            li(
                """
                Taking the experiment more slowly does not earn you a greater total payment. The total payment is fixed
                according to the 
                """,
                em("estimated"),
                " duration of the experiment",
            )

            li(
                """
                Your experiment could end early for a number of reasons, including but not limited to technical failure
                and task performance. In this case you will be compensated pro rata for the portion of the experiment
                that you completed.
                """
            )

    with p():
        strong("What is the procedure?")
        p(
            """
            The experiment takes place in your web browser. You will be asked to perform simple tasks using your
            keyboard or mouse while listening to sounds.
            """
        )

    with p():
        strong("Risks of taking part.")
        p(
            """
            There are no risks involved beyond those associated with normal computer use.
            """
        )

    with p():
        strong("Confidentiality.")
        p(
            """
            No personal details (e.g. name, contact data) will be collected at any stage, so your data will be anonymous
            throughout. This anonymous data may eventually be shared in public data repositories, conferences, and
            scientific journals.
            """
        )

    with p():
        strong("Ethical review.")
        p(
            """
            The project has been approved by the University of Cambridge Faculty of Music Ethics Committee.
            """
        )

    with p():
        strong("Contact for further information.")
        p(
            """
            If you have further queries about this experiment, please contact Claire Anne Brillon at cb2211@cam.ac.uk.
            """
        )


consent_form = div()

with consent_form:
    h1("Consent form")

    p(em("Please read the following text and select ‘Agree’ if you consent to these terms."))

    p(
        """
        I have been informed about the procedures to be used in this experiment and the tasks I need to perform, and I
        have agreed to take part. I understand that taking part in this experiment is voluntary and I can withdraw from
        the experiment at any time.
        """
    )

    p(
        """
        I understand that the data collected in this testing session will be stored on electronic media or on paper and
        it may contribute to scientific publications and presentations. I agree that the data can be made available
        anonymously for other researchers, both inside and outside the Centre for Music and Science and Faculty of
        Music. These data will not be linked to me as an individual.
        """
    )

cms_consent = Module(
    "consent",
    join(
        NoConsent(),
        InfoPage(information_sheet, time_estimate=5),
        ModularPage(
            "consent_form",
            consent_form,
            CheckboxControl(
                choices=["I agree"],
                force_selection=True,
            ),
            time_estimate=10,
        ),
    )
)
