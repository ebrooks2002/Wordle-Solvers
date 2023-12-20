from common import Common
import random

def main():
    SIZE = "small"  # "small", "medium", or "large"
    Common.set_word_lists(SIZE)
    answers = Common.answers()
    guessed_words = set()

    # Randomly select the correct word
    correct_word = random.choice(answers)
    print(f"Target word: {correct_word}")

    output_file = open(f"inputs/guesses-small.txt", "w")

    for i in range(len(answers)):
        # Choose a random word from the guess list that has not been guessed before
        remaining_guesses = set(Common.guesses()) - guessed_words
        if not remaining_guesses:
            print("No more unique guesses available.")
            break

        random_guess = random.choice(list(remaining_guesses))
        guessed_words.add(random_guess)

        # Display the current guess in the desired format
        print(f"Guess {i + 1}: {random_guess}", end=", ")
        output_file.write(f"Guess {i+1}: {random_guess}\n")

        # Display optimal responses for the current guess
        strategy = Common.solve(answers[:i+1])
        output_file.write(f"Responses: {strategy[2]}\n")

        # Check if the correct word has been guessed
        if correct_word == random_guess:
            print(f"Correct word '{correct_word}' guessed! Stopping.")
            output_file.write(f"Correct word '{correct_word}' guessed! Stopping.\n")
            break

    output_file.close()

if __name__ == "__main__":
    main()
