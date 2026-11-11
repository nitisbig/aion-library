#version 330
// The spacetime map (r across, t up) around a mass, in ingoing Eddington–Finkelstein coordinates.
// Colour = how fast a hovering clock runs, sqrt(1 − r_s/r): fast far away, slow near the horizon.
// Dashes climb each world-line at that same rate, so slow time is visibly slow.
in vec2 v_uv; in vec2 v_pos; out vec4 frag;
uniform float u_time, u_amt, u_x0, u_k, u_flow;          // u_x0: screen x of r = 0; u_k: frame units per r_s
uniform vec2 u_lo, u_hi;                                 // the plot rectangle (frame units)
uniform vec3 u_fast, u_mid, u_slow;                      // linear RGB
void main() {
    float r = (v_pos.x - u_x0) / u_k;                    // in units of r_s
    float rate = sqrt(max(1.0 - 1.0 / max(r, 1e-3), 0.0));
    vec3 col = rate < 0.5 ? mix(u_slow, u_mid, rate / 0.5) : mix(u_mid, u_fast, (rate - 0.5) / 0.5);
    // "rain" of clock ticks: thin vertical world-lines, dashes climbing at the local clock rate.
    // Discrete columns, so differing speeds never shear into moiré.
    float cell = floor(r * 5.0);
    float rc = (cell + 0.5) / 5.0;
    float crate = sqrt(max(1.0 - 1.0 / max(rc, 1e-3), 0.0));
    float fx = abs(fract(r * 5.0) - 0.5);
    float line = 1.0 - smoothstep(0.02, 0.07, fx);
    float h = fract(sin(cell * 12.9898) * 43758.5453);
    float d = fract(v_pos.y * 0.55 - u_flow * crate * 0.42 + h);
    float dash = smoothstep(0.0, 0.06, d) * (1.0 - smoothstep(0.22, 0.34, d));
    col *= 0.16 + 0.05 * (1.0 - smoothstep(0.0, 0.5, fx)) + 0.75 * line * dash;
    if (r < 1.0) {                                       // inside the horizon: no clock can hover; streaks fall inward
        float s = 0.5 + 0.5 * cos(6.2831853 * ((v_pos.x + v_pos.y) * 1.4 + u_flow * 0.5));
        col = u_slow * (0.05 + 0.10 * smoothstep(0.7, 1.0, s)) * (0.4 + 0.6 * r);
    }
    vec2 e = smoothstep(u_lo - 0.02, u_lo + 0.25, v_pos) * (1.0 - smoothstep(u_hi - 0.25, u_hi + 0.02, v_pos));
    frag = vec4(col * u_amt * e.x * e.y, 1.0);
}
