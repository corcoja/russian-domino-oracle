# Kozel Domino Oracle

This project follows a house scoring variant that is quite common in the Republic of Moldova.

At the end of a game, each player scores points from the dominoes still left in their hand. Lower is better. A player who finishes first has no tiles left and therefore scores `0` points.

For normal scoring, add together all pips on all remaining dominoes.

Examples:

- `2-3`, `4-6`, and `0-4` score `2 + 3 + 4 + 6 + 0 + 4 = 19` points.
- A `6-6` domino normally scores `12` points when counted together with other dominoes.
- A `0-0` domino normally scores `0` points when counted together with other dominoes.

There are two special single-domino exceptions:

- If a player finishes with exactly one domino and it is `6-6`, the hand scores `50` points.
- If a player finishes with exactly one domino and it is `0-0`, the hand scores `25` points.

These exceptions only apply when that domino is the only tile left in the hand. If there are any other dominoes alongside it, the hand is scored normally by pip sum.
