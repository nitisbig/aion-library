layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;
in VS { float s; float p; vec3 col; } gi[];
uniform vec2 u_res; uniform float u_width;
out float f_s; out float f_d; flat out float f_p; flat out float f_hw; flat out float f_thin; flat out vec3 f_col;
void emit(vec4 c, vec2 pix, float s, float d) {
    gl_Position = vec4(pix / (0.5 * u_res) * c.w, 0.0, c.w);
    f_s = s; f_d = d; EmitVertex();
}
void main() {
    float p = gi[0].p, s0 = gi[0].s, s1 = gi[1].s;
    if (p <= s0 + 1e-5) return;
    float f = clamp((p - s0) / max(s1 - s0, 1e-6), 0.0, 1.0);
    vec4 a = gl_in[0].gl_Position, b = mix(gl_in[0].gl_Position, gl_in[1].gl_Position, f);
    float sb = mix(s0, s1, f);
    vec2 pa = a.xy / a.w * 0.5 * u_res, pb = b.xy / b.w * 0.5 * u_res;
    vec2 dir = pb - pa; float L = length(dir);
    dir = L > 1e-4 ? dir / L : vec2(1.0, 0.0);
    vec2 n = vec2(-dir.y, dir.x);
    float thin = min(u_width, 1.0), hw = 0.5 * max(u_width, 1.0), e = hw + 1.0;
    f_p = p; f_hw = hw; f_thin = thin; f_col = gi[0].col;
    emit(a, pa - dir * hw + n * e, s0, e);
    emit(a, pa - dir * hw - n * e, s0, -e);
    emit(b, pb + dir * hw + n * e, sb, e);
    emit(b, pb + dir * hw - n * e, sb, -e);
    EndPrimitive();
}
