import random, requests, math
def write(prompt, length = 10, bias = 0):
    if bias >= 0 and bias <= 1:
        nouns = requests.get("https://raw.githubusercontent.com/TallonKH/NounPlurals/master/pluralnouns.txt").text.split("\n")
        final = prompt
        options_length = 0
        last_word = final.split(" ")[-1]
        training_data = requests.get("https://raw.githubusercontent.com/TobyCK/markov-chain-training/main/Training/mywriting.txt").text.split(" ")
        if last_word in training_data:
            for i in range(length):
                last_word = final.split(" ")[-1]
                options = []
                for j in range(len(training_data)):
                    if training_data[j] == last_word:
                        options_length += 1
                for k in range(len(training_data)):
                    if training_data[k] == last_word:     
                        if bias > 0:
                            if training_data[k+1] in prompt and training_data[k+1] in nouns:
                                for l in range(math.ceil(options_length*bias)):
                                    options.append(training_data[(k+1)%len(training_data)])
                        else:
                            options.append(training_data[(k+1)%len(training_data)])
                    else:
                        options.append(training_data[(k+1)%len(training_data)])
                final += " " + random.choice(options)
        else:
            raise ValueError("The last word of the prompt is not in the training data.")
        return final
    else:
        raise ValueError("The weight must be between 0 and 1.")