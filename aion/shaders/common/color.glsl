// Color helpers. aion composites in LINEAR light with PREMULTIPLIED alpha.
vec3 srgb2lin(vec3 c) {
    return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(0.04045, c));
}
vec3 lin2srgb(vec3 c) {
    c = max(c, 0.0);
    return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c));
}
vec4 premul(vec4 c) { return vec4(c.rgb * c.a, c.a); }
vec4 unpremul(vec4 c) { return c.a > 1e-6 ? vec4(c.rgb / c.a, c.a) : vec4(0.0); }
float luma(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }
vec3 hsv2rgb(vec3 c) {
    vec3 p = abs(fract(c.xxx + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
    return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}
// Interleaved gradient noise for dithering (deterministic per pixel + frame).
float ign(vec2 p, float frame) {
    p += 5.588238 * mod(frame, 64.0);
    return fract(52.9829189 * fract(dot(p, vec2(0.06711056, 0.00583715))));
}
