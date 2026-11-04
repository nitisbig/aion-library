layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;
in VS { float s; vec4 a; vec4 b; float coc; float k; vec3 c0; vec3 c1; } gi[];
uniform vec2 u_res; uniform float u_width;
out float f_s; out float f_d;
flat out float f_hw; flat out float f_soft; flat out float f_gain; flat out vec4 f_a; flat out vec4 f_b;
flat out vec3 f_c0; flat out vec3 f_c1;
void emit(vec4 c, vec2 pix, float s, float d) {
    gl_Position = vec4(pix / (0.5 * u_res) * c.w, 0.0, c.w);
    f_s = s; f_d = d; EmitVertex();
}
void main() {
    vec4 A = gi[0].a;
    if (A.x <= gi[0].s) return;
    vec4 a = gl_in[0].gl_Position, b = gl_in[1].gl_Position;
    if (a.w < 0.05 || b.w < 0.05) return;
    vec2 pa = a.xy / a.w * 0.5 * u_res, pb = b.xy / b.w * 0.5 * u_res;
    vec2 dir = pb - pa; float L = length(dir);
    dir = L > 1e-4 ? dir / L : vec2(1.0, 0.0);
    vec2 n = vec2(-dir.y, dir.x);
    float mag = min(abs(A.y), 1.6);
    float w = u_width * (0.6 + 0.8 * mag);
    float coc = 0.5 * (gi[0].coc + gi[1].coc);
    float hw = 0.5 * max(w, 1.0), soft = coc;
    f_gain = gi[0].k * min(w, 1.0) * (w + 1.0) / (w + 1.0 + 2.0 * coc);
    f_hw = hw; f_soft = soft; f_a = A; f_b = gi[0].b; f_c0 = gi[0].c0; f_c1 = gi[0].c1;
    float e = hw + 1.0 + soft;
    emit(a, pa - dir * 0.5 + n * e, gi[0].s, e);
    emit(a, pa - dir * 0.5 - n * e, gi[0].s, -e);
    emit(b, pb + dir * 0.5 + n * e, gi[1].s, e);
    emit(b, pb + dir * 0.5 - n * e, gi[1].s, -e);
    EndPrimitive();
}
