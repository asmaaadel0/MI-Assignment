from typing import Tuple, List
import utils
from helpers.test_tools import read_text_file, read_word_list

'''
    The DecipherResult is the type defintion for a tuple containing:
    - The deciphered text (string).
    - The shift of the cipher (non-negative integer).
        Assume that the shift is always to the right (in the direction from 'a' to 'b' to 'c' and so on).
        So if you return 1, that means that the text was ciphered by shifting it 1 to the right, and that you deciphered the text by shifting it 1 to the left.
    - The number of words in the deciphered text that are not in the dictionary (non-negative integer).
'''
DechiperResult = Tuple[str, int, int]


def caesar_dechiper(ciphered: str, dictionary: List[str]) -> DechiperResult:
    '''
        This function takes the ciphered text (string)  and the dictionary (a list of strings where each string is a word).
        It should return a DechiperResult (see above for more info) with the deciphered text, the cipher shift, and the number of deciphered words that are not in the dictionary. 
    '''
    # utils.NotImplemented()

    dictionary_set = set(dictionary)

    def is_english_word(word: str) -> bool:
        return word.lower() in dictionary_set

    def decipher(text, shift):
        deciphered_text = []
        for char in text:
            if char.isalpha():
                shifted_char = chr((ord(char) - shift - ord('A' if char.isupper()
                                   else 'a')) % 26 + ord('A' if char.isupper() else 'a'))
                deciphered_text.append(shifted_char)
            else:
                deciphered_text.append(char)
        return "".join(deciphered_text)

    min_non_dictionary_words = float('inf')
    best_deciphered_text = ""
    best_shift = 0

    words = ciphered.split()

    for shift in range(26):
        decrypted_text = " ".join(decipher(word, shift) for word in words)
        non_dictionary_words = sum(not is_english_word(
            word) for word in decrypted_text.split())

        if non_dictionary_words == 0 and decrypted_text.split()[0].lower() in dictionary:
            return decrypted_text, shift, 0

        if non_dictionary_words < min_non_dictionary_words:
            min_non_dictionary_words = non_dictionary_words
            best_deciphered_text = decrypted_text
            best_shift = shift

    return best_deciphered_text, best_shift, min_non_dictionary_words
