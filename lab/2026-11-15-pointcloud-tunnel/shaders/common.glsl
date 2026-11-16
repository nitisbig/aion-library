// shared: camera projection, centerline twin of tunnel.py, corkscrew twist, lighting, fog, scan
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_fy, u_tanX, u_tanY, u_t;
uniform float u_twist, u_twS0;            // corkscrew: angle(s) = u_twist * max(s - u_twS0, 0)^2
uniform vec3 u_light; uniform float u_lightI, u_amb;
uniform vec3 u_green, u_lightCol;
uniform float u_fog, u_reveal, u_scanS, u_scanI, u_fade;
uniform vec3 u_revealO;

vec2 cl(float s) { return vec2(1.8 * sin(0.045 * s) + 0.6 * sin(0.13 * s + 1.0), 0.5 * sin(0.07 * s + 2.0)); }

float twistAngle(float s) { float k = max(s - u_twS0, 0.0); return u_twist * k * k; }
vec3 twistP(vec3 p, float a) {
    vec2 c = cl(-p.z), d = p.xy - c; float cs = cos(a), sn = sin(a);
    return vec3(c + vec2(cs * d.x - sn * d.y, sn * d.x + cs * d.y), p.z);
}
vec3 twistN(vec3 n, float a) { float cs = cos(a), sn = sin(a); return vec3(cs * n.x - sn * n.y, sn * n.x + cs * n.y, n.z); }

// view-space (x right, y up, z forward) and clip position with a real near plane so GL clips lines correctly
vec3 toView(vec3 p) { vec3 v = p - u_cam; return vec3(dot(v, u_right), dot(v, u_up), dot(v, u_fwd)); }
vec4 toClip(vec3 v) {
    const float n = 0.06, f = 400.0;
    return vec4(v.x / u_tanX, v.y / u_tanY, (v.z * (f + n) - 2.0 * f * n) / (f - n), v.z);
}

float fogK(float z) { return exp(-u_fog * z) * smoothstep(0.05, 0.5, z); }

// scan reveal (sphere growing from u_revealO) → visibility and a bright front
vec2 reveal(vec3 p) {
    float d = length(p - u_revealO);
    float vis = smoothstep(u_reveal + 0.2, u_reveal - 2.5, d);
    float front = exp(-pow((d - u_reveal) / 0.35, 2.0)) * step(u_reveal, 200.0);
    return vec2(vis, front);
}

float illum(vec3 p, vec3 n) {
    vec3 L = u_light - p; float d2 = dot(L, L);
    float ndl = 0.35 + 0.65 * max(dot(n, L * inversesqrt(d2)), 0.0);
    return u_amb + u_lightI * ndl / (1.0 + 0.09 * d2);
}
