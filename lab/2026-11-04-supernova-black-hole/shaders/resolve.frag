// SSAA resolve: box-average u_ss × u_ss tonemapped linear samples, then display gamma
uniform sampler2D tex; uniform int u_ss; out vec4 o;
void main() {
    ivec2 b = ivec2(gl_FragCoord.xy) * u_ss;
    vec3 c = vec3(0.0);
    for (int y = 0; y < u_ss; y++) for (int x = 0; x < u_ss; x++) c += texelFetch(tex, b + ivec2(x, y), 0).rgb;
    o = vec4(pow(c / float(u_ss * u_ss), vec3(1.0 / 2.2)), 1.0);
}
