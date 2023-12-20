import sys
import itertools
import math
import collections

SOLVED_RESPONSE = int("22222", 3)

class Common:
    _answers = []
    _guesses = []
    cache = {}
    answer_letters = {}

    @staticmethod
    def set_word_lists(size):
        with open(f"inputs/answers-{size}.txt", "r") as f:
            Common._answers = [sys.intern(word.strip().upper()) for word in f.readlines()]

        # Initialize the cache for each answer
        Common.cache = {answer: {} for answer in Common._answers}

        with open(f"inputs/guesses-{size}.txt", "r") as f:
            Common._guesses = [sys.intern(word.strip().upper()) for word in f.readlines()] + Common._answers

    @staticmethod
    def answers():
        return Common._answers

    @staticmethod
    def guesses():
        return Common._guesses

    @staticmethod
    def response_repr(response):
        ret = ""
        for i in range(5):
            ret += ["X", "Y", "G"][response % 3]
            response //= 3
        return ret

    @staticmethod
    def strategy_repr(strategy, depth=1):
        if strategy is None:
            return ""
        _, guess, responses = strategy
        repr_str = guess
        indentation = " " * depth * 5 + " " * (depth - 1) * 8
        repr_str += ("\n" + indentation).join([
            " " + Common.response_repr(x) + str(depth) + (
                (" " + Common.strategy_repr(responses[x], depth + 1)) if x != SOLVED_RESPONSE else "") for x in responses
        ])
        return repr_str

    @staticmethod
    def guess_response(guess, answer):
        """Returns a list of GuessResponse colors for the given guess."""
        if len(answer) < len(guess):
            return 0

        if guess not in Common.cache[answer]:
            for c in answer:
                Common.answer_letters[c] = 0
            for c in guess:
                Common.answer_letters[c] = 0
            for c in answer:
                Common.answer_letters[c] += 1

            response = 0
            # Make 2 passes, where "G" responses take priority over "Y".
            # For example, if guess_word = "AABAA" and answer_word = "BXBXX", the response
            # should be "XXGXX", not "YXXXX".
            for (index, letter) in enumerate(guess):
                if answer[index] == letter:
                    response += 2 * (3 ** index)
                    Common.answer_letters[letter] -= 1
            for (index, letter) in enumerate(guess):
                if answer[index] != letter and Common.answer_letters[letter] > 0:
                    response += 1 * (3 ** index)
                    Common.answer_letters[letter] -= 1

            Common.cache[answer][guess] = response
        return Common.cache[answer][guess]

    @staticmethod
    def group_answers_by_response(guess_word, answers_left):
        answers_by_response = {}
        for answer_word in answers_left:
            if len(answer_word) != len(guess_word):
                continue
            response = Common.guess_response(guess_word, answer_word)
            if response not in answers_by_response:
                answers_by_response[response] = []
            answers_by_response[response].append(answer_word)
        return answers_by_response

    @staticmethod
    def entropy(guess_word, answers_left):
        answers_by_response = Common.group_answers_by_response(guess_word, answers_left)
        probabilities = [len(x) / len(answers_left) for x in answers_by_response.values()]
        return sum([-p * math.log(p, 2) for p in probabilities])

    @staticmethod
    def solve(answers):
        key = tuple(answers)
        if key not in Common.cache:
            if len(answers) == 1:
                Common.cache[key] = (1, answers[0], {SOLVED_RESPONSE: None})
            else:
                best = None
                guesses_with_entropy = [(g, Common.entropy(g, answers)) for g in Common.guesses()]
                guesses_with_entropy.sort(key=lambda pair: pair[1], reverse=True)
                for (g, e) in guesses_with_entropy:
                    if e == 0:
                        break

                    response_groups = Common.group_answers_by_response(g, answers)
                    ordered_responses = list(response_groups.keys())
                    ordered_responses.sort(key=lambda r: len(response_groups[r]))

                    lower_bound = len(answers)
                    for response in response_groups:
                        if response == SOLVED_RESPONSE:
                            continue
                        lower_bound += 2 * len(response_groups[response]) - 1

                    tree = {}
                    score = len(answers)
                    for response in ordered_responses:
                        tree[response] = Common.solve(response_groups[response])
                        if response != SOLVED_RESPONSE:
                            score += tree[response][0]
                            lower_bound += tree[response][0] - (2 * len(response_groups[response]) - 1)
                    if best is None or lower_bound < best[0]:
                        best = (score, g, tree)
                Common.cache[key] = best
        return Common.cache[key]
