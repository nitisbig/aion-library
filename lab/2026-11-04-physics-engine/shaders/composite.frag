// bloom add + ACES + vignette + optional hologram scan + fade (+ grain when not supersampled)
in vec2 uv;
uniform sampler2D scene, bloom;
uniform float u_bloom, u_exposure, u_fade, u_vig, u_scan, u_grain, u_frame, u_linearOut;
uniform vec2 u_res; uniform vec3 u_bloomTint;
out vec4 o;
float hash(vec2 p) { p = fract(p * vec2(443.897, 441.423)); p += dot(p, p.yx + 19.19); return fract((p.x + p.y) * p.x); }
vec3 aces(vec3 x) { return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }
void main() {
    vec3 c = texture(scene, uv).rgb + texture(bloom, uv).rgb * u_bloom * u_bloomTint;
    if (u_scan > 0.0) {
        float y = uv.y * u_res.y;
        c *= 1.0 - u_scan * 0.12 * (0.5 + 0.5 * sin(y * 3.14159 / 3.0));
        c *= 1.0 + u_scan * 0.05 * sin(u_frame * 0.7 + uv.y * 40.0);
    }
    c = aces(c * u_exposure);
    vec2 d = uv - 0.5;
    c *= 1.0 - u_vig * smoothstep(0.35, 0.95, length(d * vec2(1.0, 0.75)));
    c *= u_fade;
    float lum = dot(c, vec3(0.299, 0.587, 0.114));
    c += (hash(uv * u_res + u_frame * 17.13) - 0.5) * u_grain * smoothstep(0.0, 0.2, lum) * 0.35;
    if (u_linearOut > 0.5) { o = vec4(max(c, 0.0), 1.0); return; }
    o = vec4(pow(clamp(c, 0.0, 1.0), vec3(1.0 / 2.2)), 1.0);
}
