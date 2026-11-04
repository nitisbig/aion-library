// screen-space light shafts toward the brightest flash (radial blur of the highlights)
in vec2 uv;
uniform sampler2D tex;
uniform vec2 u_center;
uniform float u_frame;
out vec4 o;
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233)) + u_frame) * 43758.5453); }
void main() {
    vec2 d = (u_center - uv) / 48.0 * 0.85;
    vec2 p = uv + d * fract(52.9829189 * fract(dot(gl_FragCoord.xy, vec2(0.06711056, 0.00583715))));
    vec3 c = vec3(0.0);
    float w = 1.0;
    for (int i = 0; i < 48; i++) {
        c += max(texture(tex, p).rgb - 0.6, 0.0) * w;
        w *= 0.955;
        p += d;
    }
    o = vec4(c / 48.0, 1.0);
}
