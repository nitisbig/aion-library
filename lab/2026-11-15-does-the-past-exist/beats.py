"""Beats for 'Does the Past Still Exist?' (lab). Every visual event is tied to a word of the narration.
Phrase search is in order, so repeated words resolve to the next occurrence."""
from pathlib import Path

from aion import beats, cut, end, w

HERE = Path(__file__).resolve().parent

T = beats(
    HERE / "assets" / "cue-per-word.srt", fps=30, audio=HERE / "assets" / "audio.wav",
    # FORM: a remembered scene condenses, then dissolves into darkness
    think=w("Think of"), place=w("A place"), light=w("The light"), people=w("The people"),
    solid=w("felt solid"), real=w("Real"), andthen=w("And then"), gone=w("was gone"), q=w("Does the past"),
    c_flow=cut("exist?", "We"),
    # FLOW: the tunnel of time
    live=w("We live"), instant=w("moving instant"), arrives=w("Each moment arrives"), slips=w("slips behind"),
    tunnel=w("endless tunnel"), motion=w("call that motion"), leaves=w("leaves behind"), past=w("the past"),
    c_memory=cut("past.", "But"),
    # MEMORY: looking back; fragments of the scene, rebuilt, fading
    where=w("But where"), pieces=w("keep pieces"), recordings=w("not recordings"), remember=w("Each time we remember"),
    rebuilds=w("rebuilds the scene"), differently=w("differently"), fragments=w("Fragments fade"), blur=w("Edges blur"),
    c_light=cut("blur.", "And"),
    # LIGHT: the universe keeps records; old light still arriving
    records=w("keeps its own records"), sunlight=w("The sunlight"), sun=w("left the Sun"), eight=w("eight minutes"),
    andromeda=w("Andromeda galaxy"), million=w("half million"), lookout=w("To look out"), back=w("look back"),
    arriving=w("still arriving"),
    c_layers=cut("arriving.", "Physics"),
    # LAYERS: moments laid side by side; tilted 'nows'; the block
    further=w("Physics goes"), einstein=w("In Einstein's"), nonow=w("universal now"), whatis=w("What is now"),
    observer=w("one observer"), pastfut=w("can be past"), another=w("for another"), block=w("as a block"),
    together=w("laid out together"), nothing=w("Nothing disappears"), simply=w("simply is"), besso=w("Michele Besso"),
    wrote=w("Einstein wrote"), illusion=w("persistent illusion"),
    c_doubt=cut("illusion.", "But"),
    # DOUBT: presentism, growing block, eternalism
    agree=w("not everyone"), present=w("only the present"), traces=w("in its traces"), fixed=w("past is fixed"),
    written=w("being written"), every=w("every moment exists"), feel=w("something we feel"), decided=w("not decided"),
    c_end=cut("decided.", "The"),
    # END: empty, infinite space; the question
    lived=w("just lived"), behindyou=w("behind you"), travelling=w("still travelling"), scattered=w("scattered"),
    q1=w("So, if"), exists=w("no longer exists"), q2=w("Where did"), go=end("did it go"),
)

if __name__ == "__main__":
    for k, b in T.items.items():
        print(f"{k:12s} {float(b):7.2f}")
    print("duration", T.duration)
