import streamlit as st
import pandas as pd
import numpy as np
import string
import re
from collections import defaultdict, Counter

# Load possible answers
with open('answers.txt') as file:
    possible_answers = file.readlines()

list_possible_answers = sorted([re.sub(r'[^A-Z]', '', t.upper()) for t in possible_answers[0].split(',')])

arr_words_5l = np.array([list(w) for w in list_possible_answers])
df_words_5l = pd.DataFrame(data=arr_words_5l, columns=[f'letter_{i + 1}' for i in range(5)])
df_words_5l['word'] = list_possible_answers


class Game:
    def __init__(self, df_all_5l_words):
        self.possible_letters = list(string.ascii_uppercase)
        self.dict_misplaced_letters = Counter()
        self.df_possible_5l_words = df_all_5l_words.copy(deep=True)
        self.dict_letters = defaultdict(str)
        for i in range(5):
            self.dict_letters[i + 1] = None
        self.dict_letter_counts = defaultdict(str)
        for i in range(5):
            self.dict_letter_counts[i + 1] = Counter(df_all_5l_words[f'letter_{i + 1}'])

    def calculate_freq_score(self, letters: str) -> int:
        letters = re.sub(r'[^A-Z]', '', letters.upper())
        assert len(letters) == 5, 'Word must be 5 characters long'
        score = 0
        for i, l in enumerate(list(letters.upper())):
            score += self.dict_letter_counts[i + 1][l]
        return score

    def guess(self):
        for i in range(5):
            self.dict_letter_counts[i + 1] = Counter(self.df_possible_5l_words[f'letter_{i + 1}'])
        vect_calculate_freq_score = np.vectorize(self.calculate_freq_score)
        self.df_possible_5l_words['freq_score'] = vect_calculate_freq_score(self.df_possible_5l_words['word'])
        self.df_possible_5l_words = self.df_possible_5l_words.sort_values(by='freq_score', ascending=False)
        return self.df_possible_5l_words

    def check_misplaced_letters(self, word: str) -> bool:
        word = re.sub(r'[^A-Z]', '', word.upper())
        assert len(word) == 5, 'Word must be 5 characters long'
        list_word = list(word)
        not_solved = [key for key, value in self.dict_letters.items() if value is None]
        list_word_unsolved = [list_word[i - 1] for i in not_solved]
        dict_count_letters = Counter(list_word_unsolved)
        valid = True
        for check_key, check_value in self.dict_misplaced_letters.items():
            if dict_count_letters[check_key] < check_value:
                valid = False
        return valid

    def update(self, guess: str, results: list):
        guess = re.sub(r'[^A-Z]', '', guess.upper())
        assert len(guess) == 5, 'Guess must be 5 characters long'
        assert len(results) == 5, 'Results list must contain 5 items'
        assert all([n in [0, 1, 2] for n in results]), 'Results list must only contain ints 0, 1, or 2'
        list_guess = list(guess.upper())
        df_guess_results = pd.DataFrame(data=list(zip(list_guess, results)), columns=['letter', 'result'],
                                        index=np.arange(1, 6))
        already_solved = [key for key, value in self.dict_letters.items() if value is not None]
        df_corr_answers = df_guess_results.query('result==2')
        if df_corr_answers.shape[0] > 0:
            for idx, row in df_corr_answers.iterrows():
                if idx in already_solved:
                    pass
                else:
                    corr_letter = row['letter']
                    self.dict_letters[idx] = corr_letter
                    if corr_letter in self.dict_misplaced_letters.keys():
                        self.dict_misplaced_letters[corr_letter] -= 1
                    self.df_possible_5l_words = self.df_possible_5l_words.query(f'letter_{idx}=="{corr_letter}"')
        df_mispl_answers = df_guess_results.query('result==1')
        if df_mispl_answers.shape[0] > 0:
            for idx, row in df_mispl_answers.iterrows():
                mispl_letter = row['letter']
                self.df_possible_5l_words = self.df_possible_5l_words.query(f'letter_{idx}!="{mispl_letter}"')
            guess_mispl_letters = df_mispl_answers['letter'].values
            dict_guess_mispl_letters = Counter(guess_mispl_letters)
            for key, value in dict_guess_mispl_letters.items():
                self.dict_misplaced_letters[key] = value
            vect_check_misplaced_letters = np.vectorize(self.check_misplaced_letters)
            self.df_possible_5l_words['valid'] = vect_check_misplaced_letters(self.df_possible_5l_words['word'])
            self.df_possible_5l_words = self.df_possible_5l_words.query('valid == True')
            self.df_possible_5l_words = self.df_possible_5l_words.drop('valid', axis=1)
        df_wrong_answers = df_guess_results.query('result==0')
        if df_wrong_answers.shape[0] > 0:
            for l in df_wrong_answers['letter'].unique():
                if self.dict_misplaced_letters[l] == 0:
                    self.possible_letters.remove(l)
        yet_to_solve = [key for key, value in self.dict_letters.items() if value is None]
        for position in yet_to_solve:
            position_letters = self.df_possible_5l_words[f'letter_{position}']
            position_in_possible_letters = [l in self.possible_letters for l in position_letters]
            self.df_possible_5l_words = (self.df_possible_5l_words[position_in_possible_letters].copy(deep=True))


def main():
    st.title("Wordle Solver")
    st.write("Enter the results of your Wordle guesses to get the next best guess.")

    try:
        if 'game' not in st.session_state:
            st.session_state.game = Game(df_words_5l)

        df_possible_words = st.session_state.game.guess()

        if not df_possible_words.empty:
            guess_word = df_possible_words.iloc[0]['word']
            st.write(f"Suggested guess: {guess_word}")
        else:
            st.write("No possible words found.")
            return

        guess_results = st.text_input(
            "Enter results (e.g., 0,1,2,0,1 for 'wrong, misplaced, correct, wrong, misplaced'):")

        if guess_results:
            list_guess_results = [int(n) for n in guess_results.split(',')]
            st.session_state.game.update(guess_word, list_guess_results)
            df_possible_words = st.session_state.game.guess()

            if not df_possible_words.empty:
                st.write("Updated possible answers:")
                st.dataframe(df_possible_words)
                st.write(f"Next suggested guess: {df_possible_words.iloc[0]['word']}")
            else:
                st.write("No possible words found. Please check your input and try again.")

            if df_possible_words.shape[0] == 1 and df_possible_words.iloc[0]['word'] == guess_word:
                st.write("Congratulations! The word is correctly guessed.")
                return
    except Exception as e:
        st.write(f"An error occurred (I have failed you!!!!!!) Sage :(")


if __name__ == "__main__":
    main()