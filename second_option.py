import requests
#"69292308e2msh054aed81b925dc8p19e95ajsna1b0d2374a79"
import re


def make_guess(feedback, guess, prev_guesses, misplaced_letters, excluded_letters):
    if feedback is None:
        return "shine"  # Initial guess

    correct_positions = ["." for _ in range(len(guess))]

    for i in range(len(guess)):
        if feedback[i] == '+':
            correct_positions[i] = guess[i]
        elif feedback[i] == '-':
            excluded_letters.add(guess[i])
        elif feedback[i] == 'x':
            misplaced_letters.append((guess[i], i))
            excluded_letters.add(guess[i])
            correct_positions[i] = "."

    letter_pattern = "^" + "".join(correct_positions) + "$"

    print(f"Letter Pattern: {letter_pattern}")
    print(f"Misplaced Letters: {misplaced_letters}")
    print(f"Excluded Letters: {excluded_letters}")

    WORDS_API_URL = "https://wordsapiv1.p.rapidapi.com/words/"
    headers = {
        "x-rapidapi-key": "69292308e2msh054aed81b925dc8p19e95ajsna1b0d2374a79",
        "x-rapidapi-host": "wordsapiv1.p.rapidapi.com"
    }
    params = {
        "letterPattern": letter_pattern,
        "limit": 100
    }

    try:
        response = requests.get(WORDS_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"API Response: {data}")

        if "results" in data and "data" in data["results"]:
            possible_words = data["results"]["data"]
            for word in possible_words:
                # Skip previous guesses
                if word in prev_guesses:
                    continue

                # Check for letter pattern
                if not re.match(letter_pattern, word):
                    continue

                # Check for excluded letters
                if any(letter in word for letter in excluded_letters):
                    continue

                # Check for misplaced letters
                if misplaced_letters:
                    if not all(letter in word for letter, _ in misplaced_letters):
                        continue
                    if any(word.index(letter) == pos for letter, pos in misplaced_letters):
                        continue

                return word  # Return the first valid word

            return None  # No valid word found
        else:
            print("No results found")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching words: {e}")
        return None

def solve_wordle():
    max_guesses = 6
    current_guess = None
    prev_guesses = []
    misplaced_letters = []
    excluded_letters = set()
    feedback = None

    for attempt in range(max_guesses):
        if current_guess:
            feedback = input(f"Feedback for guess {attempt + 1} (e.g., ++-x-): ").strip()
            if len(feedback) != 5:
                print("Invalid feedback length. Expected feedback format: ++-x-.")
                continue

            if feedback == len(feedback) * '+':
                print(f"Congratulations! Guessed the word '{current_guess}' in {attempt + 1} attempts.")
                break

        current_guess = make_guess(feedback, current_guess, prev_guesses, misplaced_letters, excluded_letters)
        if not current_guess:
            print("Failed to generate a guess.")
            break

        prev_guesses.append(current_guess)
        print(f"Guess {attempt + 1}: {current_guess}")

    if not current_guess:
        print("Failed to guess the word. Better luck next time!")

# Example usage
solve_wordle()