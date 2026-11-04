// dual-filter (Kawase) upsample
in vec2 uv; uniform sampler2D tex; uniform vec2 u_texel; out vec4 o;
void main() {
    vec2 h = u_texel * 0.5;
    vec3 c = texture(tex, uv + vec2(-h.x * 2.0, 0.0)).rgb;
    c += texture(tex, uv + vec2(-h.x, h.y)).rgb * 2.0;
    c += texture(tex, uv + vec2(0.0, h.y * 2.0)).rgb;
    c += texture(tex, uv + vec2(h.x, h.y)).rgb * 2.0;
    c += texture(tex, uv + vec2(h.x * 2.0, 0.0)).rgb;
    c += texture(tex, uv + vec2(h.x, -h.y)).rgb * 2.0;
    c += texture(tex, uv + vec2(0.0, -h.y * 2.0)).rgb;
    c += texture(tex, uv + vec2(-h.x, -h.y)).rgb * 2.0;
    o = vec4(c / 12.0, 1.0);
}
