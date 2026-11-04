in float v_b; in float v_kind; in float v_param; in float v_px; in float v_coc; in vec3 v_col;
uniform sampler2D u_atlas;      // R: glyph mask, G: blurred glow; 10 cells side by side
uniform vec3 u_ink, u_hot;
uniform float u_glow;
out vec4 o;
void main() {
    vec2 pc = gl_PointCoord * 2.0 - 1.0;
    vec3 c;
    if (v_kind < 0.5) {
        float r = length(pc) * 2.5;                                   // sprite = 2.5 × particle radius
        float soft = (v_px + v_coc) / max(v_px, 0.3);
        c = u_ink * exp(-r * r / (0.35 * soft * soft)) * 1.4;
    } else if (v_kind < 1.5) {
        vec2 g = vec2((v_param + gl_PointCoord.x) / 10.0, 1.0 - gl_PointCoord.y);
        vec2 m = texture(u_atlas, g).rg;
        float edge = smoothstep(0.35, 0.65, m.r);                     // crisp glyph edge
        c = mix(v_col, u_hot, 0.25) * edge * 1.5 + v_col * m.g * u_glow;
    } else {
        float r = length(pc);
        float w = max(v_param, 1.2 / v_px);
        float ring = clamp(1.0 - abs(r - 0.9) / w, 0.0, 1.0);
        c = v_col * ring * (1.0 - smoothstep(0.97, 1.0, r));
    }
    o = vec4(c * v_b, 1.0);
}
