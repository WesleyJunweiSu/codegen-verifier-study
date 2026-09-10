"""Task-paired correctness inference for a prespecified comparison."""
import math


def exact_mcnemar(left, right):
    """Two-sided exact conditional test; no discordant tasks gives p=1."""
    if not left or len(left) != len(right):
        raise ValueError('Expected nonempty, equally sized paired outcomes')
    if any(type(x) is not bool for x in list(left) + list(right)):
        raise ValueError('Correctness outcomes must be booleans')
    wins = sum(a and not b for a, b in zip(left, right))
    losses = sum(b and not a for a, b in zip(left, right))
    discordant = wins + losses
    p = min(1.0, 2 * sum(math.comb(discordant, k) for k in range(min(wins, losses) + 1)) / (2 ** discordant))
    return {'tasks': len(left), 'left_correct': sum(left), 'right_correct': sum(right),
            'wins': wins, 'losses': losses, 'discordant_tasks': discordant,
            'accuracy_difference': (wins - losses) / len(left), 'exact_two_sided_p': p}
