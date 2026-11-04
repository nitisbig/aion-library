layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;
in VS { float s; float p; vec3 col; float r; float kind; float phase; vec3 world; } gi[];
uniform vec2 u_res; uniform float u_width;
out float f_s; out float f_d; out float f_r; out vec3 f_world;
flat out float f_p; flat out float f_hw; flat out float f_thin; flat out vec3 f_col; flat out float f_kind; flat out float f_phase;
void emit(vec4 c, vec2 pix, float s, float d, float r, vec3 w) {
    gl_Position = vec4(pix / (0.5 * u_res) * c.w, 0.0, c.w);
    f_s = s; f_d = d; f_r = r; f_world = w; EmitVertex();
}
void main() {
    float p = gi[0].p, s0 = gi[0].s, s1 = gi[1].s;
    if (p <= s0 + 1e-5) return;
    float f = clamp((p - s0) / max(s1 - s0, 1e-6), 0.0, 1.0);
    vec4 a = gl_in[0].gl_Position, b = mix(gl_in[0].gl_Position, gl_in[1].gl_Position, f);
    if (a.w < 0.5 || b.w < 0.5) return;
    float sb = mix(s0, s1, f), rb = mix(gi[0].r, gi[1].r, f);
    vec3 wb = mix(gi[0].world, gi[1].world, f);
    vec2 pa = a.xy / a.w * 0.5 * u_res, pb = b.xy / b.w * 0.5 * u_res;
    vec2 dir = pb - pa; float L = length(dir);
    dir = L > 1e-4 ? dir / L : vec2(1.0, 0.0);
    vec2 n = vec2(-dir.y, dir.x);
    float k = gi[0].kind;
    float wpx = u_width * (k > 1.5 ? 2.0 : 1.0);
    float thin = min(wpx, 1.0), hw = 0.5 * max(wpx, 1.0), e = hw + 1.0;
    f_p = p; f_hw = hw; f_thin = thin; f_col = gi[0].col; f_kind = k; f_phase = gi[0].phase;
    emit(a, pa - dir * hw + n * e, s0, e, gi[0].r, gi[0].world);
    emit(a, pa - dir * hw - n * e, s0, -e, gi[0].r, gi[0].world);
    emit(b, pb + dir * hw + n * e, sb, e, rb, wb);
    emit(b, pb + dir * hw - n * e, sb, -e, rb, wb);
    EndPrimitive();
}
