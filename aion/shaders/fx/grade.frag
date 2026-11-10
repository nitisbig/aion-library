#version 330
#include "common/color.glsl"
// Primary grade in linear light: exposure, white balance, lift/gamma/gain, contrast (log pivot), saturation, LUT.
uniform sampler2D u_src; uniform float u_exposure; uniform float u_contrast; uniform float u_saturation;
uniform vec3 u_lift; uniform vec3 u_gamma; uniform vec3 u_gain; uniform vec3 u_tint;
uniform sampler3D u_lut; uniform float u_lut_mix; uniform float u_lut_size;
in vec2 v_uv; out vec4 frag;
void main() {
    vec4 c = texture(u_src, v_uv);
    vec3 col = c.a > 1e-6 ? c.rgb / c.a : vec3(0.0);
    col *= exp2(u_exposure) * u_tint;
    col = pow(max(col * u_gain + u_lift * (1.0 - col), 0.0), 1.0 / max(u_gamma, vec3(1e-3)));
    const float pivot = 0.18;
    col = pivot * pow(max(col, 0.0) / pivot, vec3(u_contrast));
    col = mix(vec3(luma(col)), col, u_saturation);
    if (u_lut_mix > 0.0) {
        vec3 s = clamp(lin2srgb(col), 0.0, 1.0);
        vec3 uvw = (s * (u_lut_size - 1.0) + 0.5) / u_lut_size;
        col = mix(col, srgb2lin(texture(u_lut, uvw).rgb), u_lut_mix);
    }
    frag = vec4(col * c.a, c.a);
}
