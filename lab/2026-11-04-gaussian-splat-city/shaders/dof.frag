// Scatter-as-gather depth of field (golden-angle disc). Input a = linear depth.
in vec2 uv; uniform sampler2D tex; uniform vec2 u_res; uniform float u_focus, u_k, u_max;
out vec4 o;
float coc(float z) { return clamp(u_k * abs(1.0 - u_focus / max(z, 1e-6)) * u_res.y, 0.0, u_max); }
void main() {
    vec4 c0 = texture(tex, uv);
    float r0 = coc(c0.a);
    vec3 acc = c0.rgb; float wsum = 1.0;
    const int N = 48;
    for (int i = 0; i < N; i++) {
        float fi = float(i) + 0.5;
        float r = sqrt(fi / float(N)) * u_max;
        float a = fi * 2.39996323;
        vec2 off = vec2(cos(a), sin(a)) * r;
        vec4 s = texture(tex, uv + off / u_res);
        float rs = coc(s.a);
        float rr = s.a < c0.a ? rs : min(rs, r0);       // background can't bleed over a sharp foreground
        float w = smoothstep(r - 1.5, r + 0.5, rr);
        acc += s.rgb * w; wsum += w;
    }
    o = vec4(acc / wsum, c0.a);
}
