import enchant

def check_and_autocorrect_mispelled_word(word):
    d = enchant.Dict("en_US")
    if d.check(word):
        data = {
            'word_mispelled': False
            }
        return data
    else:
        suggestions = d.suggest(word) + [f"{word}"]
        data = {
            'word_mispelled': True,
            'suggestions': suggestions,
        }
        return data