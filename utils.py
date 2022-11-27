import music21


def midi_to_abc(midi, duration=4):
    if len(midi) == 0:
        return f"z{duration}"

    pitch_list = [music21.pitch.Pitch(pitch) for pitch in midi]
    respelled_pitches = music21.analysis.enharmonics.EnharmonicSimplifier(pitch_list).bestPitches()

    letters = [pitch.step for pitch in respelled_pitches]
    octaves = [pitch.octave - 4 for pitch in respelled_pitches]
    octaves_up = [max([0, octave]) for octave in octaves]
    octaves_down = [int(max(0, - octave)) for octave in octaves]
    sharps = [int(max(0, pitch.alter)) for pitch in respelled_pitches]
    flats = [int(max(0, - pitch.alter)) for pitch in respelled_pitches]
    naturals = [int(pitch.alter == 0) for pitch in respelled_pitches]

    pitch_strings = [
        "^" * sharp + "=" * natural + "_" * flat + letter + "'" * octave_up + "," * octave_down + f"{duration}"
        for sharp, natural, flat, letter, octave_up, octave_down
        in zip(sharps, naturals, flats, letters, octaves_up, octaves_down)
    ]

    return " ".join(pitch_strings)

assert midi_to_abc([60, 64, 67]) == "=C4 =E4 =G4"

assert midi_to_abc([60, 63, 67]) == "=C4 _E4 =G4"
