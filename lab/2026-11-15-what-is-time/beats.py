"""Beats for 'What Is Time?' (lab). Every visual event is tied to a word of the narration."""
from pathlib import Path

from aion import beats, cut, end, w

HERE = Path(__file__).resolve().parent

T = beats(
    HERE / "assets" / "cue-per-word.srt", fps=30, audio=HERE / "assets" / "audio.wav",
    # DARK
    q=w("What is time"), feel=w("We feel"), heart=w("beat of a heart"), evening=w("light that fades"),
    space=w("quiet space"), next=w("the next"), hold=w("try to hold"), slips=w("slips away"),
    c_road=cut("away.", "We"),
    # ROAD
    road=w("single road"), behind=w("Behind us"), past=w("the past"), ahead=w("Ahead lies"),
    open=w("open, unformed"), written=w("not yet written"), between=w("between them"), now=w("we call now"),
    c_fabric=cut("now.", "But"),
    # FABRIC
    physics=w("But physics"), einstein=w("In Einstein's"), woven=w("woven together"), spacetime=w("called spacetime"),
    when=w("not only a when"), place=w("It is a place"), four=w("four dimensions"),
    c_bend=cut("dimensions.", "And"),
    # BEND
    bends=w("fabric bends"), fast=w("Move fast"), slower=w("ticks slower"), behind2=w("left behind"),
    sink=w("Sink deeper"), runs=w("runs slow"), illusion=w("not an illusion"), sats=w("Satellites"),
    every=w("every single day"), nonow=w("no single now"), whole=w("the whole universe"), each=w("Each of us"),
    own=w("our own time"),
    c_block=cut("time.", "Some"),
    # BLOCK
    further=w("Some physicists"), block=w("four-dimensional block"), passes=w("truly passes"),
    simply=w("Every moment"), frames=w("frames of a film"),
    c_arrow=cut("film.", "And"),
    # ARROW
    remember=w("we remember"), order=w("Order gives"), coffee=w("Coffee cools"), stars=w("Stars burn"),
    arrow=w("the arrow"), oneway=w("only one way"),
    c_end=cut("way.", "So"),
    # END
    flow=w("truly flow"), bring=w("something we bring"), story=w("a story"), moment=w("one moment"),
    deepest=w("Perhaps the deepest"), why=w("But why"), all=end("anything at all"),
)

if __name__ == "__main__":
    for k, b in T.items.items():
        print(f"{k:10s} {float(b):7.2f}")
    print("duration", T.duration)
