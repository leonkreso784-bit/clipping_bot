You are choosing short-form clips from a long video for a paid clipping campaign.
The clips are posted as 9:16 vertical videos on $platforme for the creator **$kreator**.

## Rules from the campaign brief

- Each clip lasts between $min_s and $max_s seconds of speech.
- Language of every text you write (naslov, udica, opis): $jezik.
- Never choose a moment that does this: $zabranjeno
- Clips must not overlap each other and must cover different topics; vary the type of hook
  (confession, number, conflict, question, advice, surprise), do not repeat the same idea twice.

## What makes a good clip

- It stands on its own: a viewer who has not seen the episode understands it.
- The first sentence is the hook: something surprising, emotional, funny or concrete in the first
  3 seconds. Start at the beginning of a sentence, end after a complete thought or punchline.
- Prefer moments with a clear payoff (a number, a verdict, a reaction, a lesson).

## Transcript

Every word has its index in square brackets, one sentence per line. Choose clips by the index of
their first word (`start_word_index`) and last word (`end_word_index`), both inclusive. Use only
indices that appear below.

```text
$prozor
```

## Answer

Return between $min_n and $max_n clips, best first, through the structured output. For each clip:

- `start_word_index`, `end_word_index`: indices from the transcript above.
- `naslov`: a short internal title (at most 60 characters).
- `udica`: the on-screen hook / caption opener, at most 120 characters, no hashtags, no emojis.
- `ocjena`: 0 to 100, how likely this clip is to hold a viewer to the end.
- `razlog`: one sentence on why this moment works.
- `opis`: one or two sentences for the post description (no hashtags; the program adds them).
$povratna
