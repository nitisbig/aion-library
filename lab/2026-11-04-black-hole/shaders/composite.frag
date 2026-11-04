// tonemap + chromatic aberration + vignette + grain
in vec2 uv;
uniform sampler2D scene, bloom, streak;
uniform float u_bloom, u_streak, u_exposure, u_fade, u_grain, u_ca, u_vig, u_frame, u_linearOut;
uniform vec2 u_res; uniform vec3 u_streakTint;
out vec4 o;
float hash(vec2 p) { p = fract(p * vec2(443.897, 441.423)); p += dot(p, p.yx + 19.19); return fract((p.x + p.y) * p.x); }
vec3 hdr(vec2 q) {
    return texture(scene, q).rgb + texture(bloom, q).rgb * u_bloom + texture(streak, q).rgb * u_streak * u_streakTint;
}
vec3 aces(vec3 x) {      // Narkowicz ACES fit
    return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0);
}
void main() {
    vec2 d = uv - 0.5;
    vec2 off = d * dot(d, d) * 0.012 * u_ca;
    vec3 c = vec3(hdr(uv + off).r, hdr(uv).g, hdr(uv - off).b);
    c = aces(c * u_exposure);
    c *= 1.0 - u_vig * smoothstep(0.35, 0.95, length(d * vec2(1.0, 0.75)));
    c *= u_fade;
    if (u_linearOut > 0.5) { o = vec4(c, 1.0); return; }   // supersampled: resolve applies gamma
    c = pow(c, vec3(1.0 / 2.2));
    float lum = dot(c, vec3(0.299, 0.587, 0.114));
    c += (hash(uv * u_res + u_frame * 17.13) - 0.5) * u_grain * smoothstep(0.0, 0.25, lum) * (0.3 + lum);
    o = vec4(clamp(c, 0.0, 1.0), 1.0);
}
