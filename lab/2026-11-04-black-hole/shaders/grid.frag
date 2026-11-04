in float f_s; in float f_d; in float f_r; in vec3 f_world;
flat in float f_p; flat in float f_hw; flat in float f_thin; flat in vec3 f_col; flat in float f_kind; flat in float f_phase;
uniform vec3 u_cam, u_warm, u_hot;
uniform float u_time, u_sink, u_pulse, u_alpha, u_camDist, u_rmax;
out vec4 o;
void main() {
    float cov = clamp(f_hw + 0.5 - abs(f_d), 0.0, 1.0) * f_thin;
    if (cov <= 0.0) discard;
    vec3 c = f_col;
    if (f_kind < 1.5) {
        // as space curves, the deep part of the well warms: colour follows √(1 − 2M/r),
        // the gravitational time-dilation factor
        float g = sqrt(max(1.0 - 2.0 / f_r, 0.0));
        c = mix(c, u_warm * 1.3, u_sink * (1.0 - smoothstep(0.35, 0.92, g)));
        c *= 1.0 - 0.45 * smoothstep(0.6 * u_rmax, u_rmax, f_r);          // soft outer rim
    }
    if (f_kind > 1.5 && f_kind < 2.5) {                                     // photon sphere: light circling
        float ph = fract(f_s - u_time * 0.35);
        c *= 1.0 + 1.6 * pow(1.0 - ph, 10.0);
    }
    if (f_kind > 0.5 && f_kind < 1.5 && u_pulse > 0.0) {                    // matter falling in, accelerating
        float ph = fract(u_time * 0.16 + f_phase);
        float rp = 2.0 + (u_rmax - 2.0) * (1.0 - ph * ph);
        float w = 0.45 + 0.05 * rp;
        c += u_hot * 2.6 * u_pulse * exp(-pow((f_r - rp) / w, 2.0)) * smoothstep(1.0, 0.92, ph);
    }
    float head = exp(-max(f_p - f_s, 0.0) * 25.0) * (1.0 - smoothstep(0.97, 1.0, f_p));
    c *= 1.0 + 2.5 * head;
    float dist = length(f_world - u_cam) / u_camDist;
    c *= mix(1.0, 0.3, smoothstep(0.85, 1.6, dist));                       // depth fog
    o = vec4(c * cov * u_alpha, 1.0);
}
