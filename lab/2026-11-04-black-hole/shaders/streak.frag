// anamorphic streak: wide horizontal gaussian of the bright parts (run with growing u_step)
in vec2 uv; uniform sampler2D tex; uniform vec2 u_texel; uniform float u_step; uniform float u_thresh; out vec4 o;
void main() {
    vec3 c = vec3(0.0); float wsum = 0.0;
    for (int i = -6; i <= 6; i++) {
        float w = exp(-float(i * i) / 18.0);
        vec3 s = texture(tex, uv + vec2(float(i) * u_step * u_texel.x, 0.0)).rgb;
        c += w * max(s - u_thresh, 0.0); wsum += w;
    }
    o = vec4(c / wsum, 1.0);
}
