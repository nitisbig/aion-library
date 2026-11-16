"""Beats for 'What Is Consciousness?' (lab). Every visual event is tied to a word of the narration.
Phrase search is in order, so repeated words ('dark', 'experience', 'sky') resolve to the next occurrence."""
from pathlib import Path

from aion import beats, cut, end, w

HERE = Path(__file__).resolve().parent

T = beats(
    HERE / "assets" / "cue-per-word.srt", fps=30, audio=HERE / "assets" / "audio.wav",
    # DARK: particles awaken
    why=w("Why does"), inside=w("from the inside"), billions=w("For billions"), dark1=w("moving in the dark"),
    dust=w("Dust, gathering"), stars=w("into stars"), felt=w("was felt"), somewhere=w("And then, somewhere"),
    notice=w("began to notice"),
    c_matter=cut("notice.", "Look"),
    # MATTER: neurons connect
    look=w("Look closely"), cells=w("Only cells"), neurons=w("Eighty-six"), reaching=w("reaching out"),
    pulses=w("Tiny pulses"), chem=w("Chemicals drift"), physics=w("nothing here but physics"), atoms=w("Atoms,"),
    forged=w("forged in stars"), laws=w("same laws"),
    c_brain=cut("else.", "And"),
    # BRAIN: the storm becomes a brain
    andyet=w("And yet, from"), storm=w("electrical storm"), appears=w("something extraordinary"),
    pounds=w("Three pounds"), sky=w("color of the sky"), sea=w("tastes the sea"), voice=w("remembers a voice"),
    c_tunnel=cut("loved.", "Inside,"),
    # TUNNEL: perception
    world=w("Inside, there is"), model=w("but a model"), darkness=w("built in darkness"), skull=w("inside the skull"),
    light=w("Light becomes"), sigcol=w("Signals become"), depth=w("and depth"), face=w("and a face"),
    c_memory=cut("face.", "Memories"),
    # MEMORY: fragmented landscapes that rebuild
    memories=w("Memories are"), photos=w("like photographs"), remember=w("Each time you remember"),
    rebuild=w("rebuild the moment"), differently=w("a little differently"), thought=w("Every thought"),
    pattern=w("was a pattern"), rising=w("rising"), fading=w("fading away"),
    c_gap=cut("away.", "But"),
    # GAP: the map without the experience
    mystery=w("here is the mystery"), trace=w("trace every"), map=w("map every"), spike=w("measure every"),
    nowhere=w("nowhere in that map"), blue=w("blue of the sky"), being=w("feeling of being you"),
    hard=w("hard problem"), howdoes=w("How does"), experience=w("experience"), why2=w("Why doesn't"),
    indark=w("happen in the dark"),
    c_flux=cut("dark.", "Some"),
    # FLUX: forming, dissolving, forming again
    some=w("Some think"), woven=w("woven together"), others=w("Others suspect"), deeper=w("something deeper"),
    property=w("a property of the universe"), noone=w("No one knows"), still=w("never stands still"),
    forms=w("It forms"), dissolves=w("dissolves"), again=w("forms again"), replaced=w("Much of the matter"),
    remain=w("you remain"),
    c_end=cut("remain.", "Perhaps"),
    # END: back to darkness and the question
    process=w("but a process"), running=w("universe is running"), askyou=w("So ask yourself"),
    q1=w("Is consciousness something"), created=w("universe created"), q2=w("Or is it a way"),
    itself=end("experience itself"),
)

if __name__ == "__main__":
    for k, b in T.items.items():
        print(f"{k:12s} {float(b):7.2f}")
    print("duration", T.duration)
