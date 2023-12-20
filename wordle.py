import random
import re

class Node:
    def __init__(self, parent):
        self.parent = parent
        self.children = {}
        self.value = None
        self.word = None
        self.level = parent.level + 1 if parent is not None else 0
        self.total_successors = 0

    def add(self, word, final_word=None):
        if final_word is None:
            final_word = word

        self.value = word[0]

        if len(word) == 1:
            self.word = final_word
            self.total_successors = 1
            return

        self.total_successors += 1

        next_value = word[1]

        if next_value not in self.children:
            self.children[next_value] = Node(parent=self)

        self.children[next_value].add(word[1:], final_word)

    def lock_letter(self, level, value):
        if self.level == level and self.value != value:
            self.remove()
        else:
            for child in self.children.values():
                child.lock_letter(level, value)

    def remove(self):
        if self.parent is not None and self.value in self.parent.children:
            del self.parent.children[self.value]
            self.parent.total_successors -= 1
            self.parent.remove()

    def most_likely_recursive(self):
        max_successors = -1
        max_node = None

        for node in self.children.values():
            child_successors = node.total_successors if node is not None else 0
            if child_successors > max_successors:
                max_successors = child_successors
                max_node = node

        return max_node

class NodeCollection:
    def __init__(self):
        self.root = Node(None)
        self.locked_letters = [None] * 6
    
    def add_dictionary(self, path):
            with open(path, "r") as file:
                for line in file:
                    line = line.strip()
                    if len(line) == 5:
                        line = "#" + line.lower()  # Convert to lowercase
                        self.root.add(line)

    def lock_letter_recursive(self, level, value, search):
        if search is None:
            return

        if search.level < level:
            for node in list(search.children.values()):  # Convert values() to list to avoid dictionary size change during iteration
                self.lock_letter_recursive(level, value, node)

        if search.level == level and search.value != value:
            search.remove()

    def remove_letter_at_level(self, level, value, search):
        nodes_to_remove = []
        for node in search.children.values():
            if node.level + 1 == level and value in node.children and node.children[value] is not None \
                    and self.is_not_locked(node.children[value]):
                nodes_to_remove.append(node.children[value])
            else:
                self.remove_letter_at_level(level, value, node)

        for node in nodes_to_remove:
            node.remove()

    def remove_letter(self, value):
        self.remove_letter_recursive(value, self.root)

    def remove_letter_recursive(self, value, search):
        if search is None:
            return

        if search.value == value and self.is_not_locked(search):
            search.remove()
            return

        for node in list(search.children.values()):  # Create a copy of the dictionary values
            self.remove_letter_recursive(value, node)


    def float_letter(self, levels, value):
        nodes_to_remove = []
        for level in levels:
            for node in list(self.root.children.values()):
                self.remove_letter_at_level(level, value, node)
                self.must_have_letter(value, len(levels), node, 0)

    def must_have_letter(self, value, occurrences, search, found):
        if search is None:
            return

        nodes_to_remove = []

        if search.value == value and self.is_not_locked(search):
            found += 1
            nodes_to_remove.append(search)

        if found >= occurrences:
            return

        if search.level == 5 and found < occurrences:
            nodes_to_remove.append(search)

        for node in nodes_to_remove:
            node.remove()

        for node in list(search.children.values()):  # Create a copy of the dictionary values
            self.must_have_letter(value, occurrences, node, found)

    def remove_letter_at_level(self, level, value, search):
        if search is None:
            return

        if search.level > level:
            return

        if search.level + 1 == level and value in search.children and search.children[value] is not None \
                and self.is_not_locked(search.children[value]):
            search.children[value].remove()
            return

        if search.level + 1 < level:
            for node in list(search.children.values()):  # Create a copy of the dictionary values
                self.remove_letter_at_level(level, value, node)


    def is_not_locked(self, node):
        return self.locked_letters[node.level] != node.value

    def most_likely_recursive(self, search):
        max_successors = -1
        max_node = None

        for node in search.children.values():
            child_successors = node.total_successors if node is not None else 0
            if child_successors > max_successors:
                max_successors = child_successors
                max_node = node

        if max_node is not None and max_node.level == 5:
            return max_node
        elif max_node is not None:
            return self.most_likely_recursive(max_node)
        else:
            return None

    def most_likely(self):
        root = self.root
        most_likely_node = self.most_likely_recursive(root)

        if most_likely_node is not None:
            return most_likely_node.word
        else:
            # If no word is most likely, choose a random word from the tree
            return self.random_search()

    def random_search(self):
        search = self.root
        while search.level < 5:
            children = [
                node
                for node in search.children.values()
                if (
                    node is not None
                    and node.total_successors > 0
                    and self.is_not_locked(node)
                    and node.value not in self.locked_letters
                )
            ]
            if not children:
                break

            probabilities = [node.total_successors for node in children]
            total_probabilities = sum(probabilities)

            if total_probabilities == 0:
                break

            normalized_probabilities = [prob / total_probabilities for prob in probabilities]
            index = random.choices(range(len(children)), weights=normalized_probabilities)[0]
            search = children[index]

        if search.level == 5:
            return search.word
        else:
            return self.most_likely_recursive(search)

    def update_tree(self, locked_letters, removed_letters, floating_letters):
        # Resolve Green Locked Squares
        self.resolve_locked_letters(locked_letters)

        # Resolve Grey Removed Squares
        self.resolve_removed_letters(removed_letters)

        # Resolve Orange Floating Squares
        self.resolve_floating_letters(floating_letters)

    def resolve_locked_letters(self, locked_letters):
        for level, value in locked_letters.items():
            if value is not None:
                self.lock_letter_recursive(level, value, self.root)

    def resolve_removed_letters(self, removed_letters):
        for value in removed_letters:
            self.remove_letter(value)

    def resolve_floating_letters(self, floating_letters):
        for level, value in floating_letters:
            self.float_letter([level], value)
    


class WordleSolver:
    def __init__(self):
        self.words = NodeCollection()
        self.words.add_dictionary("words.txt")

    def update_tree_based_on_guess(self, guess):
        locked_letters, removed_letters, floating_letters = self.parse_guess_feedback(guess)

        print(f"Locked Letters: {locked_letters}")
        print(f"Removed Letters: {removed_letters}")
        print(f"Floating Letters: {floating_letters}")

        self.words.update_tree(locked_letters, removed_letters, floating_letters)

    def parse_guess_feedback(self, guess):
        locked_letters = {}
        removed_letters = set()
        floating_letters = {}

        for i, char in enumerate(guess):
            if char.isalpha():
                level = i + 1  # Level is 1-indexed
                if char.islower():
                    floating_letters[level] = char
                else:
                    locked_letters[level] = char
            elif char.isdigit():
                level = int(char)
                removed_letters.add(level)

        return locked_letters, removed_letters, floating_letters

    def update_tree(self, locked_letters, removed_letters, floating_letters):
        self.resolve_locked_letters(locked_letters)
        self.resolve_removed_letters(removed_letters)
        self.resolve_floating_letters(floating_letters)

    def resolve_locked_letters(self, locked_letters):
        for level, value in locked_letters.items():
            if value is not None:
                self.words.lock_letter_recursive(level, value, self.words.root)

    def resolve_removed_letters(self, removed_letters):
        for level in removed_letters:
            self.words.remove_letter_at_level(level, None, self.words.root)

    def resolve_float_letters(self, floating_letters):
        for level, value in floating_letters.items():
            self.words.float_letter([level], value)
    
    
    def is_word_solved(self):
        return all(letter.islower() for letter in self.words.most_likely())

    def play_wordle(self):
        for i in range(1, 7):
            guess = self.words.random_search()
            print(f"\n\nGuess #{i}: {guess}")

            locked_letters_input = input("Green/Locked Letters (e.g., o3): ")
            removed_letters_input = input("Grey/Removed Letters (e.g., m1 e4 y5): ")
            float_letters_input = input("Orange/Mismatched Letters (e.g., o2 s3): ")

            locked_letters = self.parse_letter_input(locked_letters_input)
            removed_letters = self.parse_letter_input(removed_letters_input)
            floating_letters = self.parse_letter_input(float_letters_input)

            self.resolve_locked_letters(locked_letters)
            self.resolve_removed_letters(removed_letters)
            self.resolve_float_letters(floating_letters)

            if self.is_word_solved():
                print("Congratulations! The word is solved.")
                break

    def parse_letter_input(self, input_str):
        letters = {}
        pattern = re.compile(r"(?P<value>[a-z])(?P<level>[0-9])")
        matches = pattern.finditer(input_str)

        for match in matches:
            value = match.group("value")
            level = int(match.group("level"))
            letters[level] = value

        return letters    

if __name__ == "__main__":
    wordle_solver = WordleSolver()
    wordle_solver.play_wordle()
