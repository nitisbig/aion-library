// gravitational-wave ring warp + bloom/streak + ACES tonemap + grade + vignette (+ grain)
in vec2 uv;
uniform sampler2D scene, bloom, streak;
uniform float u_bloom, u_streak, u_exposure, u_fade, u_grain, u_ca, u_vig, u_frame, u_linearOut, u_grade;
uniform vec2 u_res; uniform vec3 u_streakTint;
uniform float u_tanHalf, u_aspect;
uniform float u_gwR[2], u_gwA[2], u_gwW[2];
uniform float u_gwPsi;
out vec4 o;
float hash(vec2 p) { p = fract(p * vec2(443.897, 441.423)); p += dot(p, p.yx + 19.19); return fract((p.x + p.y) * p.x); }

// h₊ wave packet travelling outward from the centre: stretch along one axis, squeeze along the other
vec2 gwWarp(vec2 q, out float hsum) {
    hsum = 0.0;
    float rho = length(q);
    for (int k = 0; k < 2; k++) {
        if (u_gwA[k] <= 0.0) continue;
        float x = (rho - u_gwR[k]) / u_gwW[k];
        hsum += u_gwA[k] * exp(-0.5 * x * x) * sin(3.2 * x) / (1.0 + 1.5 * rho);
    }
    mat2 R = mat2(cos(u_gwPsi), sin(u_gwPsi), -sin(u_gwPsi), cos(u_gwPsi));
    vec2 qr = transpose(R) * q;
    return R * (0.5 * hsum * vec2(qr.x, -qr.y));
}

vec3 hdr(vec2 q) {
    return texture(scene, q).rgb + texture(bloom, q).rgb * u_bloom + texture(streak, q).rgb * u_streak * u_streakTint;
}
vec3 aces(vec3 x) {
    return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0);
}
void main() {
    vec2 scale = 2.0 * u_tanHalf * vec2(u_aspect, 1.0);
    vec2 q = (uv - 0.5) * scale;
    float h;
    vec2 dq = gwWarp(q, h);
    vec2 wuv = uv + dq / scale;
    vec2 d = wuv - 0.5;
    vec2 off = d * dot(d, d) * 0.012 * u_ca;
    vec3 c = vec3(hdr(wuv + off).r, hdr(wuv).g, hdr(wuv - off).b);
    c *= 1.0 + 2.5 * h;
    c = aces(c * u_exposure);
    if (u_grade > 0.0) {                               // teal shadows, warm highlights
        float lum = dot(c, vec3(0.2126, 0.7152, 0.0722));
        vec3 g = mix(vec3(0.90, 1.0, 1.08), vec3(1.07, 1.0, 0.90), smoothstep(0.02, 0.55, lum));
        c = mix(c, c * g, u_grade);
    }
    c *= 1.0 - u_vig * smoothstep(0.35, 0.95, length((uv - 0.5) * vec2(1.0, 0.75)));
    c *= u_fade;
    if (u_linearOut > 0.5) { o = vec4(c, 1.0); return; }
    c = pow(c, vec3(1.0 / 2.2));
    float lum = dot(c, vec3(0.299, 0.587, 0.114));
    c += (hash(uv * u_res + u_frame * 17.13) - 0.5) * u_grain * smoothstep(0.0, 0.25, lum) * (0.3 + lum);
    o = vec4(clamp(c, 0.0, 1.0), 1.0);
}
