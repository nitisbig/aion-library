"""Named beats, resolved IN ORDER from assets/cue-per-word.srt (run `uv run aion beats {{slug}}`).

Use `uv run aion plan {{slug}}` to see phrases, silences and suggested cuts.
  name="phrase"                 start of the phrase (searched after the previous beat)
  name=end("phrase")            end of the phrase
  name=w("phrase", offset=-.1)  nudged
  cutN=cut("before", "after")   scene boundary in the real silence between two phrases
"""
from aion import beats, cut, end, w  # noqa: F401

T = beats(
    # intro="imagine a grid",
    # cut1=cut("of lines", "this arrow"),
)
