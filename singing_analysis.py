import json

from sing4me import singing_extract  # noqa - something weird about the sing4me package definition?

SING4ME_CONFIG = dict(
    # Defaults taken from sing4me/sing_experiments/singing_2intervals;
    # these are the the parameters used for the oral transmission journal article first submitted in autumn 2022.
    #
    # There are lots of typos! but these are inherited from the current state of the sing4me package.
    #
    # See also
    # - https://gitlab.com/computational-audition-lab/sing4me/-/blob/master/sing_experiments/params.py
    # and
    # - https://gitlab.com/computational-audition-lab/sing4me/-/blob/master/sing4me/singing_extract.py
    # and
    # - https://gitlab.com/computational-audition-lab/iterated-singing/currentbio22/iterated-singing
    sample_rate=44100,
    peak_time_difference=70,  # Calculated with: ms_to_samples(70, fs=STANDARD_FS),
    minimum_peak_height=0.05,
    db_threshold=-30, # used to be -22 (-30 means probably that the pitch extraction blobs are mainly used for the syllable calc_segments)
    db_end_threshold_realtive_2note_start=-15, # used to be -10 (changed )
    #max_vs_start_threshold_importance = 0.9, #I got rid of this parameters as I am calculating min as threshold
    msec_silence=30,  # was 90 (minimal silence between segments - increase to require more time between segments
    silence_beginning_ms= 50,
    extend_pitch_threshold_semitones=2.0,
    praat_extend_proximity_threshold_ms=150.0,  # (ms) max allowed extension of onset of the sung tone based on paraat - if the onset computed from paraat is deviating more than this threshold the onset would not be extended!
    cut_pre=40,  # EXPERIMENTAL used to be 30 - time ignored at start of seg (ms)
    cut_post=50,  # time ignored at end of seg (ms)
    minimal_segment_duration=40, # experimental  used to be 35
    pitch_range_allowed=[36, 75],
    singing_bandpass_range=[80, 6000],  # in Hz - we use this to bandpass filtering the audio
    singing_bandpass_range_praat_syllable=[40,8000], # in Hz - we use this to bandpass filter the audio for syllable extraction
    smoothing_env_window_ms=40,
    compresssion_power=0.5, # non linear compression - no compression = 1
    allowed_pitch_flactuations_witin_one_tone=8.0,  # in semitones - max flactuations that is considered OK
    percent_of_flcatuating_within_one_tone=35.0, #
    # exclude tones with more than that percent if they fluctuate more than allowed_pitch_flactuations_witin_one_tone
    praat_octave_jump_cost=0.55,
    # praat default is 0.35 but we suspect that this is not good enough (too many octave doubling "jumps")
    praat_high_frequncy_favoring_octave_cost=0.03,
    # control octave_cost parms parrat dedault is 0.01  see https://www.fon.hum.uva.nl/praat/manual/Sound__To_Pitch__ac____.html
    praat_silence_threshold=0.03,  # praat default: silence_threshold = 0.03
)


def analyze_recording(
        audio_path,
        plot_path,
):
    raw = singing_extract.analyze(
        audio_path,
        SING4ME_CONFIG,
        plot_options=singing_extract.PlotOptions(
            save=True,
            path=plot_path,
            format="png",
        )
    )

    return {
        "pitches": [float(note["median_f0"]) for note in raw],
        "raw": simplify_numpy_types(raw),
    }


def simplify_numpy_types(x):
    return json.loads(json.dumps(x))


# sing_duration = 4,
# max_abs_interval_error_treshold = 5.5,  # we used 5 in pilot 2-3
# max_melody_pitch_range = 99,  # we used 9 in pilot 2-3
# num_int = 2,
# reference_mode = "pitch_mode",  # three options: first_note, previous_note, or "pitch_mode"
# max_pitch_height_seed = 9.5,
# max_pitch_height = 15,
# discrete = False,  # True means that everything is quantized to the 12-tone scale
# max_mean_interval_error = 5.5,