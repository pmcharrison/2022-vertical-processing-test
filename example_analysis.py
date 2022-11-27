import tempfile

from singing_analysis import *


def run_analysis():
    with tempfile.NamedTemporaryFile() as f_plot:
        return singing_extract.analyze(
                "example_audio.wav",
                SING4ME_CONFIG,
                plot_options=singing_extract.PlotOptions(
                    save=False,
                    path=f_plot.name,
                    format="png",
                )
            )

run_analysis()
