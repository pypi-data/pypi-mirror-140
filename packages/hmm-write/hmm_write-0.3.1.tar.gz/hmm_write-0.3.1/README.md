## Hidden Markov Machine (HMM)

This module provides the function `write([prompt], [length], [bias])` which adds `[length]` words to the end of the prompt. If the bias is set to 0 (the minimum), there will be no bias, and the closer it gets to 1 (the maximum) nouns in the prompt are more likely to be chosen. If a bias is not supplied, the default is 0.