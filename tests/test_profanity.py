from clipping.profanity import PROFANITY, mask


def test_mask_keeps_first_letter_and_punct() -> None:
    assert mask("Fucking,") == "F******,"
    assert mask("shit.") == "s***."
    assert mask('"Damn!"') == '"D***!"'


def test_mask_leaves_clean_words() -> None:
    for word in ["Hello", "assistant", "class", "shitake", "Scunthorpe", "hello."]:
        assert mask(word) == word


def test_mask_handles_suffix() -> None:
    assert mask("shitty") == "s*****"
    assert mask("fucked") == "f*****"
    assert mask("bitches") == "b******"


def test_mask_whole_sentence() -> None:
    assert mask("What the fuck, man") == "What the f***, man"


def test_list_has_enough_roots() -> None:
    assert len(PROFANITY) >= 30
    assert all(w == w.lower() for w in PROFANITY)
