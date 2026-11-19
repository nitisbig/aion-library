"""Named beats for video 013, resolved in order from assets/cue-per-word.srt. One section per storyboard scene."""
from aion import beats, cut, end, w  # noqa: F401

T = beats(
    # s01 cold_open
    take="Take a key", lay="lay it on a flat grid", lift="pick up the whole plane", lean1="Lean it to one side", pull="Pull it upward",
    lean2="Lean it again", lean3="and once more", four_mv="Four moves", single="a single matrix", question="So here's the question",
    can="Can we put it back", we_can="We can", one_more="One more matrix", smooth="one smooth motion",
    returns="every point returns", exact="exactly where it started", inverse_word="called the inverse",
    cut_crush=cut("the inverse.", "Now try a matrix"),
    # s02 the_crush
    twin="looks almost the same", second_col="second column", flat="The plane falls flat", streak="a streak",
    put_back="Put this one back", no_hold="nothing to hold on to", this_key="this key", flipped="with a tooth flipped",
    four_teeth="Four teeth", sixteen="sixteen different keys", same_mark="exactly the same mark", shadow="It's a shadow",
    cut_promise=cut("key cast it.", "Why can one matrix"),
    # s03 promise
    why="Why can one matrix", game="a video game", drone_q="how a drone reads", eqn_q="solves an equation",
    blur_q="a blurred picture", sharp="sharp again", impossible="sounds impossible", rebuild="rebuild this key",
    cut_simple=cut("its shadows.", "A matrix is a move"),
    # s04 simple_moves
    move="A matrix is a move", columns="Its columns", two_arrows="two basic arrows", rest="the rest of the plane", easy="Some moves are easy",
    turn="Turn the plane", turn_back="turns it the same", stretch="Stretch it", shrinks="shrinks it", slide="Slide each row",
    cards="deck of cards", deck="pushes the deck",
    cut_wrong=cut("other way.", "That stretch suggests"),
    # s05 wrong_rule
    shortcut="suggests a shortcut", half="became a half", third="became a third", flip="flip every number", but_deck="But the sliding deck",
    zero="has a zero", cant="be flipped", undid="we undid", sign="a single sign", mat_crush="the matrix that crushed", no_zeros="has no zeros",
    one_at="read one at a time", wont="tell us", whole="the whole matrix",
    cut_threads=cut("to space.", "Follow one point"),
    # s06 threads
    one_point="Follow one point", thread="draw a thread", now_do="Now do the same", every_pt="every other point", web="That web of threads",
    back_web="The way back is", opposite="opposite direction", thats="what an inverse is", reversed_="Every thread, reversed",
    cut_identity=cut("thread, reversed.", "Go out along"),
    # s07 identity
    out_back="Go out along", come_back="come back", round_trip="The round trip", does_nothing="does nothing at all", has_matrix="Doing nothing has",
    its_cols="Its columns leave", identity="the identity", number_one="the number one", mult="multiply by it", so_inv="So the inverse is",
    after_a="applied after A", back_first="Take the way back first", gets_home="everyone still gets home", either="Either order",
    cut_rewind=cut("the identity.", "Most moves come"),
    # s08 rewind
    stages="Most moves come", lean="we lean the plane", quarter="a quarter turn", how_back="How do we get back", wrong="Undo the lean",
    undo_t="then undo the turn", no_home="doesn't come home", last="The turn happened last", off_first="come off first",
    right="Undo the turn, then the lean", then_l="then the lean", lines_up="everything lines up", film="a film played backward",
    chain="inverse of a chain", reverse_o="in reverse order", broken="broken into simple", rewind_it="rewind it", simple="one simple move",
    cut_four=cut("a time.", "Let's do that"),
    # s09 four_moves
    bent="the matrix that bent our key", slides="using only slides", move1="The first slide", upright="pulls one arrow", move2="A second slide",
    axis="onto the axis", belongs="exactly where it belongs", other="The other arrow", tall="four times too tall", move3="we squash the plane",
    quarter_h="a quarter of its height", move4="One last slide", straightens="straightens it", four_home="Four moves", home4="the key is home",
    cut_record=cut("is home.", "But we never"),
    # s10 recording
    never="we never wrote", play_same="play the same four", second_grid="a second grid", untouched="starts untouched", as_bent="As the bent grid",
    bends="the straight grid bends", record="keeping a record", reaches="reaches the identity", became="has become the inverse",
    row_red="row reduction", blocks="those two blocks", these_two="these two grids", rewinds="One rewinds", records="the other records",
    cut_check=cut("other records.", "Let's check it"),
    # s11 check
    check="Let's check it", multiply="Multiply the inverse", cancel="the fractions cancel", ones="ones on the diagonal",
    zeros_e="zeros everywhere", recognize="recognize those four moves", same_four="the same four",
    cut_det=cut("played backward.", "And there's something"),
    # s12 det_emerges
    hiding="something hiding", slide_a="A slide never", area="never changes area", shrink="all of the shrinking", squash_again="that single squash",
    quarter_a="down to a quarter", four="Four is exactly", grew="grew every area", det="It's the determinant", run="Run the same steps",
    letters="with letters", recipe="the recipe", swap="Swap these two", negate="negate those two", divide="divide by the determinant",
    uneasy="a little uneasy", what_h="What happens", nothing_div="nothing to divide by",
    cut_tilt=cut("divide by?", "Take our matrix"),
    # s13 tilt
    tilt="slowly tilt", thinner="grows thinner", det_falls="the determinant falls", harder="work harder", reopen="To reopen", x10="factor of ten",
    x100="Then a hundred", x1000="Then a thousand", keep="Keep this nearly flat", line_up="finally line up", flat_is="the plane is flat",
    det_zero="the determinant is zero", infinity="off to infinity",
    cut_many=cut("to infinity.", "Pick one spot"),
    # s14 many_to_one
    pick="Pick one spot", who="which points landed", fan="The threads come in", entire="an entire line", rays="the rays that cast",
    way_back="A way back would", at_once="all of those points", matrix_gives="a matrix gives", one_answer="just one answer",
    cut_columns=cut("one answer.", "You can read"),
    # s15 columns
    read_cols="read this in the columns", twice="exactly twice", nothing_new="adds nothing new", dependent="linearly dependent",
    crushed="the crushed arrow", recipe_cols="one of the first", minus="minus two", makes_nothing="makes nothing",
    cut_fact=cut("nothing.", "So these are"),
    # s16 one_fact
    one_fact="one fact", four_sides="seen from four sides", f_cols="The columns depend", f_area="The area drops", f_dir="A whole direction",
    f_back="there is no way back", if_any="If any one", all_true="all of them are",
    cut_powders=cut("them are.", "Undoing a matrix"),
    # s17 powders
    solve_eq="solve an equation", powders="mixing two powders", p1="A scoop of the first", p1_pro="three grams", p2="A scoop of the second",
    p2_pro="one of protein", cols_mat="the columns of our matrix", scoops_in="Give it a number", get="tells you what", other_way="runs the other way",
    target="seven grams", six="six of fibre", how_many="How many scoops",
    cut_solve=cut("is that?", "Geometrically, that asks"),
    # s18 solve
    geo="Geometrically, that asks", landed="landed on this target", apply="Apply the inverse", follow="follow the thread home",
    answer="two scoops of the first", one_of="one of the second", every_sys="Every linear system", ended="ended up", want="you want to know",
    cut_weak=cut("it started.", "Now swap in"),
    # s19 weak
    weak="exactly half as strong", every_mix="Every mix", line1="on a single line", off="off that line", norec="no recipe exists", on_line="something on it",
    endless="endless recipes", no_ans="No answer", too_many="or too many", two_ways="two ways a system fails",
    collapse_saw="the collapse we",
    cut_drone=cut("just saw.", "Two observers"),
    # s20 drone
    observers="Two observers", drone="To a drone", landmark="this landmark", steps="two steps ahead", axes="the drone's axes",
    inv_map="its inverse translates", pov="the drone's point",
    cut_camera=cut("of view.", "A video game"),
    # s21 camera
    game2="A video game", placed="placed in the world", sees="what it sees", applies="applies the inverse",
    never_walk="you never walk", carried="The world gets carried",
    cut_blur=cut("past you.", "Now here's a picture"),
    # s22 blur
    picture="here's a picture", smeared="smeared by", average="an average of", averages="averages are exactly",
    has_inv="This blur has", apply_blur="Apply it", edge="every edge",
    cut_noise=cut("comes back.", "But remember"),
    # s23 noise
    remember="But remember", squeezes="Blur squeezes", enormous="an enormous amount", noise="a trace of noise",
    buried="the picture is buried", useless="can still be useless", stops="Real deblurring", only="undoes only",
    cut_second=cut("that survived.", "Which brings us"),
    # s24 second_shadow
    brings="Which brings us", one_sh="From one shadow", another="taking another", turn_light="Turn the light",
    falls="falls in a different", new_eq="new equations", fewer="fewer and fewer",
    cut_ct=cut("them all.", "Two shadows"),
    # s25 ct_reconstruct
    two="Two shadows", four_s="Four", sixteen_s="Sixteen", blur_first="A blur at first", outline="then an outline",
    enough="With enough angles", forgets="no longer forgets", teeth="teeth and all", ct="a CT scanner",
    angles="hundreds of angles", solves="then solves",
    cut_outro=cut("cast them.", "Every matrix moves"),
    # s26 outro
    every="Every matrix moves", forgot="what that move forgot", nothing_f="If it forgot nothing", home_ex="the way home exists",
    something="If it forgot something", gone="that part is gone", look="go and look again", new_place="from somewhere new",
)
