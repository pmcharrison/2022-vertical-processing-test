# from voice_leading import nonbijective_vl


def score_response(target: list[float], response: list[float]):
    score = 0.0
    remaining_target_pitches = target.copy()
    for sung_pitch in response:
        found_match = False
        for target_pitch in remaining_target_pitches:
            if abs(sung_pitch - target_pitch) < 0.5:
                found_match = True
                score += 1
                remaining_target_pitches.remove(target_pitch)
                break
        if not found_match:
            score -= 0.5
    return max(0, score)


# def get_minimal_voice_leading(x, y):
#     _, vl = nonbijective_vl(x, y, pcs=False)
#     return vl[:-1]
#
#
# def infer_target_pitches(target: list[float], sung: list[float]):
#     voice_leadings = get_minimal_voice_leading(target, sung)
#     voice_leadings.sort(key=lambda x: abs(x[1] - x[0]))
#
#     for voice_leading in voice_leadings:

