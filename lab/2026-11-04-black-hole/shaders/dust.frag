in vec2 f_q; flat in vec3 f_col; flat in float f_len; flat in float f_hw;
out vec4 o;
void main() {
    float along = f_q.x < 0.0 ? -f_q.x : max(f_q.x - f_len, 0.0);   // distance past the segment ends
    float d = length(vec2(along, f_q.y));
    float sig = 0.45 * (f_hw - 1.0) + 0.35;
    float k = exp(-0.5 * d * d / (sig * sig));
    float head = mix(0.35, 1.0, clamp(f_q.x / max(f_len, 1e-3), 0.0, 1.0));   // brighter at the leading end
    o = vec4(f_col * k * head, 1.0);
}
