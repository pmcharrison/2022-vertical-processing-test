# Chooses k chord types from each cardinality
import itertools
import json
import random

cardinalities = [2, 3, 4]
k = 12  # This means that we cover all 12 dyads within the octave

chosen = []

random.seed(42)  # Setting the random seed to a fixed value before we start guarantees reproducibility

for cardinality in cardinalities:
    bass = 0
    n_non_bass_pitches = cardinality - 1
    possible_non_bass_pitches = range(1, 13)  # Numbers between 1 and 12 inclusive
    possible_non_bass_combinations = list(itertools.combinations(possible_non_bass_pitches, n_non_bass_pitches))
    chosen_non_bass_combinations = random.sample(possible_non_bass_combinations, k=k)
    chosen_chord_types = [[bass] + list(non_bass) for non_bass in chosen_non_bass_combinations]
    chosen_chord_types.sort()
    chosen = chosen + chosen_chord_types

print(f"Generated {len(chosen)} chord types.")

with open("chord_types.json", "w") as file:
    json.dump(chosen, file, indent=4, )
