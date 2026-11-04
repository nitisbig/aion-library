// half-res march → full res with a small tent filter (hides the per-pixel step jitter)
in vec2 uv; uniform sampler2D tex; out vec4 o;
void main() {
    vec2 t = 0.6 / vec2(textureSize(tex, 0));
    vec3 c = texture(tex, uv).rgb * 2.0 + texture(tex, uv + vec2(t.x, t.y)).rgb + texture(tex, uv + vec2(-t.x, t.y)).rgb
           + texture(tex, uv + vec2(t.x, -t.y)).rgb + texture(tex, uv - t).rgb;
    o = vec4(c / 6.0, 1.0);
}
