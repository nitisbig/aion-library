// zoom blur + chromatic aberration + bloom + flash + ACES + grade + vignette + grain + fade
in vec2 uv;
uniform sampler2D scene, bloom;
uniform float u_bloom, u_exposure, u_fade, u_vig, u_grain, u_frame, u_zoom, u_ca, u_flash;
uniform vec2 u_res;
out vec4 o;
float hash(vec2 p) { p = fract(p * vec2(443.897, 441.423)); p += dot(p, p.yx + 19.19); return fract((p.x + p.y) * p.x); }
vec3 aces(vec3 x) { return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }
vec3 samp(vec2 p) {
    vec2 d = p - 0.5;
    return vec3(texture(scene, 0.5 + d * (1.0 + u_ca)).r, texture(scene, p).g, texture(scene, 0.5 + d * (1.0 - u_ca)).b)
         + texture(bloom, p).rgb * u_bloom;
}
void main() {
    vec3 c = vec3(0.0);
    const int N = 14;
    float jit = hash(uv * u_res + u_frame);
    if (u_zoom > 0.002) {
        for (int i = 0; i < N; i++) {
            float k = (float(i) + jit) / float(N);
            c += samp(0.5 + (uv - 0.5) * (1.0 - u_zoom * k));
        }
        c /= float(N);
    } else c = samp(uv);
    c *= u_exposure * (1.0 + u_flash);
    c += u_flash * 0.05 * vec3(0.8, 0.9, 1.0) * texture(bloom, uv).rgb;
    c = aces(c);
    // grade: gentle S-curve, cool shadows / warm highlights, blacks stay black
    float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
    c = mix(c, c * vec3(0.94, 1.0, 1.08), (1.0 - l) * 0.5);
    c = mix(c, c * vec3(1.05, 1.0, 0.95), l * 0.4);
    c = c * c * (3.0 - 2.0 * c) * 0.35 + c * 0.65;
    vec2 d = uv - 0.5;
    c *= 1.0 - u_vig * smoothstep(0.3, 0.95, length(d * vec2(1.0, 0.72)));
    c *= u_fade;
    c += (hash(uv * u_res + u_frame * 17.13) - 0.5) * u_grain * (0.3 + 0.7 * smoothstep(0.0, 0.25, l)) * u_fade;
    o = vec4(pow(clamp(c, 0.0, 1.0), vec3(1.0 / 2.2)), 1.0);
}
