// particle → world position (blob hierarchy transform + jitter + falling rain)
layout(std430, binding = 0) readonly buffer Blobs { vec4 blob[]; };   // (centre, scale), quaternion
layout(std430, binding = 1) readonly buffer Parts { vec4 part[]; };   // (offset, weight), (blob, seed, kind, glint)
uniform vec3 u_rain;   // top, bottom, fall speed
vec3 qrot(vec4 q, vec3 v) { return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v); }
vec3 particlePos(int i, out vec4 a, out vec4 b) {
    a = part[2 * i]; b = part[2 * i + 1];
    int id = int(b.x + 0.5);
    vec4 cs = blob[2 * id], q = blob[2 * id + 1];
    vec3 p = cs.xyz + qrot(q, a.xyz * cs.w);
    float s = b.y * 6.2831853;
    if (b.z > 1.5) {
        float H = u_rain.x - u_rain.y;
        p.y = u_rain.x - mod(u_rain.x - a.y + u_tb * u_rain.z * (0.8 + 0.4 * b.y), H);
    } else {
        float amp = b.z > 0.5 ? 0.18 : 0.035;
        p += amp * vec3(sin(u_tb * 0.9 + s), sin(u_tb * 0.7 + s * 3.0), sin(u_tb * 0.8 + s * 5.0));
    }
    return p;
}
