layout(points) in;
layout(triangle_strip, max_vertices = 4) out;
in VS { vec4 prev; vec3 col; float size; } gi[];
uniform vec2 u_res; uniform float u_wscale;
out vec2 f_q; flat out vec3 f_col; flat out float f_len; flat out float f_hw;
void main() {
    vec4 b = gl_in[0].gl_Position, a = gi[0].prev;
    if (a.w < 0.5 || b.w < 0.5) return;
    vec2 pa = a.xy / a.w * 0.5 * u_res, pb = b.xy / b.w * 0.5 * u_res;
    vec2 d = pb - pa; float L = length(d);
    vec2 dir = L > 1e-3 ? d / L : vec2(1.0, 0.0);
    vec2 n = vec2(-dir.y, dir.x);
    float hw = max(gi[0].size * u_wscale, 0.8) + 1.0;
    // energy is spread along the streak; very long streaks would only add noise
    float e = 1.0 / (1.0 + L / (2.0 * hw));
    if (L > 0.25 * u_res.x) return;
    f_col = gi[0].col * e; f_len = L; f_hw = hw;
    vec2 c0 = pa - dir * hw, c1 = pb + dir * hw;
    float z = b.w;
    gl_Position = vec4((c0 + n * hw) / (0.5 * u_res) * z, 0.0, z); f_q = vec2(-hw, hw);     EmitVertex();
    gl_Position = vec4((c0 - n * hw) / (0.5 * u_res) * z, 0.0, z); f_q = vec2(-hw, -hw);    EmitVertex();
    gl_Position = vec4((c1 + n * hw) / (0.5 * u_res) * z, 0.0, z); f_q = vec2(L + hw, hw);  EmitVertex();
    gl_Position = vec4((c1 - n * hw) / (0.5 * u_res) * z, 0.0, z); f_q = vec2(L + hw, -hw); EmitVertex();
    EndPrimitive();
}
