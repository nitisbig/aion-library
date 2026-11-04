// one bounding quad per primitive, in world space
layout(points) in;
layout(triangle_strip, max_vertices = 4) out;
in VS { vec4 k; vec4 ab; vec4 c; vec4 col; vec4 p; } vi[];
uniform vec2 u_cam; uniform float u_ppu; uniform vec2 u_res;
out vec2 f_w;
flat out vec4 f_k, f_ab, f_c, f_col, f_p;
void emitw(vec2 w) {
    gl_Position = vec4((w - u_cam) * u_ppu / (0.5 * u_res), 0.0, 1.0);
    f_w = w; f_k = vi[0].k; f_ab = vi[0].ab; f_c = vi[0].c; f_col = vi[0].col; f_p = vi[0].p;
    EmitVertex();
}
void main() {
    int kind = int(vi[0].k.x + 0.5);
    float r = vi[0].k.y;
    vec2 a = vi[0].ab.xy, b = vi[0].ab.zw;
    float m = 2.0 / u_ppu;
    vec2 lo, hi;
    if (kind == 0) { float e = r + vi[0].c.z + m; lo = min(a, b) - e; hi = max(a, b) + e; }
    else if (kind == 1) { float e = r + max(vi[0].c.w, 3.0 * vi[0].p.x) + m; lo = a - e; hi = a + e; }
    else if (kind == 2) { float e = r + vi[0].c.z + vi[0].c.w + m; lo = a - e; hi = a + e; }
    else if (kind == 3) { vec2 c = vi[0].c.xy; float e = vi[0].p.x + m;
                          lo = min(min(a, b), c) - e; hi = max(max(a, b), c) + e; }
    else if (kind == 4) { lo = a - b; hi = a + b; }
    else if (kind == 5) { float e = vi[0].col.w + m; lo = a - e; hi = b + e; }
    else { float e = 3.2 * r + m; lo = a - e; hi = a + e; }
    emitw(vec2(lo.x, lo.y)); emitw(vec2(hi.x, lo.y)); emitw(vec2(lo.x, hi.y)); emitw(vec2(hi.x, hi.y));
    EndPrimitive();
}
