"""Named beats for video 012, resolved in order from assets/cue-per-word.srt. One section per storyboard scene."""
from aion import beats, cut, end, w  # noqa: F401

T = beats(
    # s01 dido_coast
    queen="a queen in exile", africa="North Africa", king="asked the local king", joke="He offered her a joke",
    hide="the hide of a single ox", strips="So she cut the hide", thread="thin as thread", rope="one enormous rope",
    shore="Then she walked to the shore", guard="the sea would guard", one_q="Only one question", shape_q="What shape should",
    cut_question=cut("the rope make?", "That is a very human"),
    # s02 question
    human="That is a very human", best_we="But, what is the best", fixed_rope="A fixed length of rope", budget="A fixed budget",
    bridge="bridge that must stand", steel="as little steel",
    cut_fermat=cut("as possible.", "Around sixteen thirty-six"),
    # s03 fermat
    fermat="Around sixteen thirty-six", no_hold="nothing holds you back", flat="the ground goes flat", flats="Find the flat places",
    candidates="you have found",
    cut_trail=cut("your candidates.", "But limits break"),
    # s04 trail
    limits="But limits break", hike="hiking a trail", summit="The summit is right there", stay="stay on the path",
    where="So where on this path", stand="Stand at that spot", not_flat="the ground is not flat", rises="The mountain still rises",
    cant="You just can't go",
    cut_lagrange=cut("go that way.", "The person who cracked"),
    # s05 lagrange
    turin="The person who cracked", y1755="seventeen fifty-five", lagr="Joseph-Louis Lagrange", euler="Leonhard Euler",
    dido_like="problems very much like", y1788="Thirty-three years later", machines="how machines balance",
    hold_back="hold each other back", extra="one extra unknown number",
    cut_everywhere=cut("unknown number.", "We call those numbers"),
    # s06 everywhere
    called="We call those numbers", every="they are everywhere", wings="In the design of wings", econ="In how economists",
    network="In how a network", learn="how machines learn", heat="the laws of heat",
    cut_nofig=cut("laws of heat.", "Lagrange was so confident"),
    # s07 no_figures
    confident="Lagrange was so confident", promise="a striking promise", nofig="no figures will be found", not_one="Not one picture",
    pity="Which is a pity", beautiful="most beautiful pictures",
    cut_preview=cut("in mathematics.", "So let's draw it"),
    # s08 preview
    draw="So let's draw it", pv_top="what happens at the highest", pv_arrow="why one arrow", pv_method="how that picture becomes",
    pv_solve="how the method solves", concrete="surprisingly concrete", measure="you can measure it",
    cut_ch1=cut("with a stick.", "Let's turn the mountain"),
    # s09 objective
    turn_math="Let's turn the mountain", give="Give every point", fxy="f of x and y", objective="We call it the objective",
    no_limit="With no limits", steepest="which way is steepest", grad_name="is the gradient of f", follow="Follow it and you climb",
    stop_="You stop only", grad_zero="when the gradient is zero", flat_again="That is Fermat's flat ground",
    cut_constraint=cut("flat ground.", "Now add the trail"),
    # s10 constraint
    add_trail="Now add the trail", rule="A trail is a rule", g_eq="some function g", on_path="Points that satisfy",
    forbid="Everything else is forbidden", look="Look at what that does", two_dir="You had two directions", one_dir="now you have one",
    formula="Sometimes you can write", tangled="But real constraints are tangled", unroll="without unrolling",
    cut_ch2=cut("unrolling the trail.", "So let's look at the mountain"),
    # s11 contours
    map_view="So let's look at the mountain", slice_="Slice it at equal heights", contour="a contour line", walk_c="Walk along one contour",
    tells="That tells us something", no_gain="Moving along a contour", perp="The gradient is always perpendicular",
    cut_walk=cut("beneath your feet.", "Now walk the trail"),
    # s12 walk
    walk="Now walk the trail", cross="the trail cuts across", keep="Keep going", spread="The crossings spread out", gentler="The climb is getting",
    special="at one special point", touches="It touches a contour", falls="falls away", is_top="That is the top", if_cross="If the trail crossed",
    cut_swell=cut("at the top.", "Here is another way"),
    # s13 swell
    another="Here is another way", high_c="Start with a high contour", lower="Now lower the height", swells="The loop swells",
    first_t="it first touches", that_touch="That first touch", insight="here is the quiet insight", itself="The trail is itself",
    level_g="one level curve of g", families="two families of curves", kiss="one curve from each",
    cut_ch3=cut("family just kiss.", "Two curves that kiss"),
    # s14 align
    share="Two curves that kiss", each="Each curve's gradient", both="both gradients are perpendicular", common="one common direction",
    multiple="One arrow must be", grad_eq="The gradient of f equals lambda", greek="That Greek letter", stretch="just a stretch factor",
    longer="how many times longer",
    cut_compass=cut("than the other.", "Let's feel why"),
    # s15 compass
    feel="Let's feel why", carry="Walk the trail carrying", split="split it into two parts", across="The part across the trail",
    along_p="The part along the trail", better="you can still do better", arrive="You arrive at the best", remains="all that remains",
    cut_proof=cut("across the path.", "Now the proof"),
    # s16 proof
    proof="Now the proof", path_r="your walk as a path", stay_on="You stay on the trail", g_dot="the gradient of g dot", at_top="At the top",
    f_dot="the gradient of f dot", both_p="Both gradients are perpendicular", as_long="as long as the gradient", count="Count what we have",
    two_eq="Two equations", one_con="one from the constraint", three="Three unknowns", algebra="The picture has become",
    cut_ch4=cut("become algebra.", "Lagrange packed"),
    # s17 lagrangian
    packed="Lagrange packed", subtract="subtract lambda", l_eq="L equals f minus", d_xy="Set its derivatives", arrow_eqs="you get the arrow equations",
    d_lam="Set its derivative with respect to lambda", out_con="out comes the constraint", restricted="A restricted problem", returned="flat ground has returned",
    cut_saddle=cut("higher dimension.", "But be careful"),
    # s18 saddle
    careful="But be careful", not_peak="not a peak of L", smallest="Take the smallest", forced="x forced to equal one", plot_l="Plot L over",
    on_saddle="sits on a saddle", rising="rising one way", cant_climb="You can't simply climb", solve_it="You have to solve",
    cut_ch5=cut("solve for it.", "Let's put this to work"),
    # s19 fence
    beach="Let's put this to work", forty="forty meters of rope", rect="a rectangular plot", sides_x="Two sides of length x", side_y="one side of length y",
    maximize="We want to maximize", grad_a="The gradient of the area", grad_r="The gradient of the rope", y_lam="So y equals two lambda", x_lam="x equals lambda",
    four="four lambda equals forty", lam10="Lambda is ten", plot10="The plot is ten meters", area200="two hundred square meters", hold="Hold on to that ten",
    cut_circle=cut("We will need it.", "Next, a case"),
    # s20 circle
    next_case="Next, a case", extremes="Find the extremes", the_circle="the circle x squared", arrow2="The arrow equations", splits="The first one splits",
    either="Either x is zero", if_lam="If lambda equals y", y1="y is plus or minus one", if_x="If x is zero", y3="y is plus or minus root three", six="That is six candidates",
    walk_around="Walk around", max2="The maximum is two", min2="The minimum is minus two", zeros="The two zeros", never="The equations never tell", compare="and you compare",
    cut_ch6=cut("you compare.", "Nothing here depends"),
    # s21 sphere
    flat_map="Nothing here depends", surfaces="level curves become level surfaces", the_plane="the plane x plus two y", spheres="The level surfaces of distance",
    inflate="Inflate a sphere", tangent_p="the two surfaces share", same_eq="the equation is exactly", pt122="The point is one",
    cut_ellipse=cut("distance of three.", "Now add a second"),
    # s22 ellipse
    second="Now add a second", cylinder="A cylinder and a tilted", top_e="we want its highest", back_on="We are back on", plane_dirs="a whole plane of directions",
    no_single="no longer has to line up", spanned="the plane spanned", eq_two="The gradient of f equals lambda", mu_t="mu times the gradient", own="Every constraint gets",
    cut_ch7=cut("its own multiplier.", "So what is this number"),
    # s23 price
    really="So what is this number", back_rope="Go back to the rope", was10="Lambda was ten", add_m="Now add one more meter", climbs="The best area climbs",
    ten_more="Ten more square meters", no_coin="That is no coincidence", loosens="As the constraint loosens", rate="at exactly rate lambda", exchange="The multiplier is the exchange",
    shadow="Economists call it", units="one more unit of budget", posted="nobody ever posted",
    cut_force=cut("posted that price.", "In physics"),
    # s24 force
    physics="In physics", bead="A bead rests", gravity="Gravity pulls it", push_back="the hoop pushes back", minimize="Minimize the bead's", that_push="is exactly that push",
    physically="A constraint, physically", lag_world="That is the world",
    cut_gas=cut("these numbers.", "And then the deepest"),
    # s25 boltzmann
    deepest="And then the deepest", gas="Take a box of gas", likely="the overwhelmingly likely", max_ent="So maximize", two_c="Two constraints", boltz="Out falls Boltzmann's",
    chance="the chance of a state", beta="Beta is the multiplier", price_e="It is the price of energy", name_it="physicists have a name", temp=end("one over that price", 0.4),
    cut_ch8=cut("temperature.", "The method does come"),
    # s26 cusp
    fine="The method does come", assumed="We assumed", the_cusp="The curve y squared", smallest_x="the smallest x", vanish="the gradient of g vanishes", no_mult="no multiple of zero",
    no_sol="The equations have no solution", check="always check the sharp",
    cut_ineq=cut("by hand.", "Also, tangency"),
    # s27 inequality
    tangency="Also, tangency", infinity="if the trail runs off", ineq="Real limits are often", at_most="spend at most", karush="William Karush", kt="Harold Kuhn",
    lovely="The idea is lovely", zero_price="A limit you aren't",
    cut_outro=cut("price of zero.", "Let's go back to the beach"),
    # s28 semicircle
    return_b="Let's go back to the beach", any_shape="let the rope take", whole="Apply the same idea", bend="must bend by the same", a_circle="That is a circle", semi="a semicircle",
    a255="Forty meters of rope now", quarter="more than a quarter", the_mult="And the multiplier", radius="It is the radius", each_m="Each extra meter", d127="about twelve point seven",
    lay="Lay a stick", hands="holding lambda", last1="At the best point", last2="Lagrange's number tells",
)
