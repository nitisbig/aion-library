// dual-filter (Kawase) downsample
in vec2 uv; uniform sampler2D tex; uniform vec2 u_texel; out vec4 o;
void main() {
    vec2 h = u_texel * 0.5;
    vec3 c = texture(tex, uv).rgb * 4.0;
    c += texture(tex, uv - h).rgb + texture(tex, uv + h).rgb;
    c += texture(tex, uv + vec2(h.x, -h.y)).rgb + texture(tex, uv - vec2(h.x, -h.y)).rgb;
    o = vec4(c / 8.0, 1.0);
}
