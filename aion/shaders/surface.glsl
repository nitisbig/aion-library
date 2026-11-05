// Shared height model for SurfacePlate (prepended to the vertex and fragment shaders).
// Mirrors aion/components/surface_gl.py::height() exactly. Keep the two in sync.
//
//   raw = wq * ½[x y]H[x y]ᵀ + wg * Σ gaussians + wc * (x³ − 3x + y²)
//       + w4 * (x⁴ + y⁴) + wm * (x³ − 3xy²) + offset
//   z   = zs * raw, softly clamped to ±zclip with tanh when zclip > 0

uniform vec3 u_H;            // (a, b, c): H = [[a, b], [b, c]]
uniform vec4 u_w;            // (wq, wg, wc, w4)
uniform float u_wm;          // monkey saddle weight
uniform float u_offset;
uniform vec4 u_gauss[16];    // (cx, cy, amp, sigma)
uniform int u_ngauss;
uniform float u_zs;
uniform float u_zclip;

float height_raw(vec2 p) {
    float x = p.x, y = p.y;
    float q = 0.5 * (u_H.x * x * x + 2.0 * u_H.y * x * y + u_H.z * y * y);
    float g = 0.0;
    for (int i = 0; i < 16; i++) {
        if (i >= u_ngauss) break;
        vec4 G = u_gauss[i];
        vec2 d = p - G.xy;
        g += G.z * exp(-dot(d, d) / (2.0 * G.w * G.w));
    }
    float cub = x * x * x - 3.0 * x + y * y;
    float qu = x * x * x * x + y * y * y * y;
    float mk = x * x * x - 3.0 * x * y * y;
    return u_w.x * q + u_w.y * g + u_w.z * cub + u_w.w * qu + u_wm * mk + u_offset;
}

float height(vec2 p) {
    float z = u_zs * height_raw(p);
    if (u_zclip > 0.0) z = u_zclip * tanh(z / u_zclip);
    return z;
}
