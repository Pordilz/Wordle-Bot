
import requests
import re

# Constants
WORDLE_WORD_URL = "https://wordle-game-api1.p.rapidapi.com/word"

# Replace with your WordsAPI RapidAPI key


# Function to fetch daily word from Wordle API
def fetch_daily_word():
    payload = {"timezone": "UTC + 0"}
    headers = {
        "x-rapidapi-key": "69292308e2msh054aed81b925dc8p19e95ajsna1b0d2374a79",
        "x-rapidapi-host": "wordle-game-api1.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(WORDLE_WORD_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["word"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching daily word: {e}")
        return None

def feedback(word):
    url = "https://wordle-game-api1.p.rapidapi.com/guess"

    payload = {
        "word": word,
        "timezone": "UTC + 0"
    }
    headers = {
        "x-rapidapi-key": "69292308e2msh054aed81b925dc8p19e95ajsna1b0d2374a79",
        "x-rapidapi-host": "wordle-game-api1.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()["result"]

# Function to make a guess using WordsAPI and Wordle feedback



def make_guess(feedback, guess):
    if feedback is None:
        return "chink"  # Initial guess

    correct_positions = ["." for _ in range(len(guess))]
    misplaced_letters = []
    excluded_letters = []

    for i in range(len(guess)):
        if feedback[i] == '+':
            correct_positions[i] = guess[i]
        elif feedback[i] == '-':
            excluded_letters.append(guess[i])
        elif feedback[i] == 'x':
            misplaced_letters.append(guess[i])
            correct_positions[i] = "."

    letter_pattern = "^" + "".join(correct_positions) + "$"

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

        if "data" in data and data["data"]:
            possible_words = data["data"]
            for word in possible_words:
                if all(letter in word for letter in misplaced_letters) and not any(letter in word for letter in excluded_letters):
                    if all(word.index(letter) != guess.index(letter) for letter in misplaced_letters):
                        print(f"Next guess: {word}")
                        return word
            print("No suitable words found")
            return None
        else:
            print("No results found")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching words: {e}")
        return None



# Main solving function
def solve_wordle():
    max_guesses = 6  # Adjust as needed
    current_guess = None
    result = None

    for attempt in range(max_guesses):
        if current_guess:
            result = feedback(current_guess)
            if len(result) != len(current_guess):
                print("Invalid feedback length. Expected feedback format: ++-xx.")
                continue

            if feedback == len(current_guess) * '+':
                print(f"Congratulations! Guessed the word '{current_guess}' in {attempt + 1} attempts.")
                break

        current_guess = make_guess(result, current_guess)
        if not current_guess:
            print("Failed to generate a guess.")
            break

        print(f"Guess {attempt +1}: {current_guess}")

    if not current_guess:
        print("Failed to guess the word. Better luck next time!")



# Run the main solving function
if __name__ == "__main__":
    solve_wordle()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


