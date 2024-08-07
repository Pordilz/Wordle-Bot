import re
feedback = '--+-+'
current_guess = 'clime'
prev_guesses = ['shine', 'abide', 'clime']
misplaced_letters = []
excluded_letters = {'a', 's', 'd', 'm', 'v', 'h', 'l', 'c', 'e', 'n', 'b'}
def make_guess(feedback, current_guess, prev_guesses, misplaced_letters, excluded_letters):
    # Simulate API response
    words = ['amite', 'boite', 'clite', 'elite', 'evite', 'flite', 'jaite', 'olite', 'quite', 'shite', 'skite', 'smite', 'spite', 'suite', 'trite', 'twite', 'unite', 'waite', 'white', 'write']

    for word in words:
        # Skip previous guesses
        if word in prev_guesses:
            continue

        # Check for excluded letters
        if any(letter in word for letter in excluded_letters):
            continue

        # Check if word matches feedback pattern
        pattern = '^' + ''.join([char if char in ('+', '-') else '.' for char in feedback]) + '$'
        if not re.match(pattern, word):
            continue

        # Check misplaced letters
        if misplaced_letters:
            if not all(letter in word for letter, _ in misplaced_letters):
                continue
            if any(word.index(letter) == pos for letter, pos in misplaced_letters):
                continue

        return word  # Return the first valid word

    return None  # No valid word found

# Example usage


next_guess = make_guess(feedback, current_guess, prev_guesses, misplaced_letters, excluded_letters)
print(f"Next guess: {next_guess}")