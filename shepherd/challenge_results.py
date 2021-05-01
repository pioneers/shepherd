from collections import defaultdict

results = [False, False, False, False, False, False, False, False]

CHALLENGE_RESULTS = defaultdict(lambda: results)
CHALLENGE_RESULTS[12] = [True] * 8
CHALLENGE_RESULTS[26] = [True] * 8
CHALLENGE_RESULTS[31] = [True] * 8
CHALLENGE_RESULTS[35] = [True] * 8
CHALLENGE_RESULTS[42] = [True, True, True, True, True, False, True, False]
CHALLENGE_RESULTS[44] = [True, True, False, True, True, True, False, False]
CHALLENGE_RESULTS[46] = [True] * 8
CHALLENGE_RESULTS[6] = [True] * 8
CHALLENGE_RESULTS[40] = [True, True, True, True, True, True, True, False]
CHALLENGE_RESULTS[2] = [True] * 8
CHALLENGE_RESULTS[15] = [True, False, True, True, True, True, True, True]
CHALLENGE_RESULTS[10] = [True] * 8
CHALLENGE_RESULTS[8] = [True] * 8 # Bishop
CHALLENGE_RESULTS[17] = [True, False, True, True, True, False, False, False]
