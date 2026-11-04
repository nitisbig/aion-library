// analytic-AA signed-distance primitives. Colours are linear HDR; output is premultiplied,
// and `add` (k.w) turns a primitive additive by zeroing its alpha.
in vec2 f_w;
flat in vec4 f_k, f_ab, f_c, f_col, f_p;
uniform float u_wpp; uniform sampler2D u_atlas;
out vec4 o;

float cov(float d, float soft) { return 1.0 - smoothstep(-0.5 * u_wpp - soft, 0.5 * u_wpp + soft, d); }

float sdTri(vec2 p, vec2 p0, vec2 p1, vec2 p2) {
    vec2 e0 = p1 - p0, e1 = p2 - p1, e2 = p0 - p2;
    vec2 v0 = p - p0, v1 = p - p1, v2 = p - p2;
    vec2 q0 = v0 - e0 * clamp(dot(v0, e0) / dot(e0, e0), 0.0, 1.0);
    vec2 q1 = v1 - e1 * clamp(dot(v1, e1) / dot(e1, e1), 0.0, 1.0);
    vec2 q2 = v2 - e2 * clamp(dot(v2, e2) / dot(e2, e2), 0.0, 1.0);
    float s = sign(e0.x * e2.y - e0.y * e2.x);
    vec2 d = min(min(vec2(dot(q0, q0), s * (v0.x * e0.y - v0.y * e0.x)),
                     vec2(dot(q1, q1), s * (v1.x * e1.y - v1.y * e1.x))),
                     vec2(dot(q2, q2), s * (v2.x * e2.y - v2.y * e2.x)));
    return -sqrt(d.x) * sign(d.y);
}

void main() {
    int kind = int(f_k.x + 0.5);
    float r = f_k.y, alpha = f_k.z, add = f_k.w;
    vec2 a = f_ab.xy, b = f_ab.zw;
    vec3 col = f_col.rgb;
    vec3 c = vec3(0.0); float A = 0.0;

    if (kind == 0) {                                   // capsule a→b
        vec2 pa = f_w - a, ba = b - a;
        float l2 = dot(ba, ba);
        float h = l2 > 1e-12 ? clamp(dot(pa, ba) / l2, 0.0, 1.0) : 0.0;
        float d = length(pa - ba * h) - r;
        float cv = cov(d, f_c.z);
        cv *= mix(1.0, f_c.w, h);                      // alpha fades along the segment
        float period = f_col.w;
        if (period > 0.0) {
            float s = fract(h * sqrt(l2) / period + f_p.y);
            float duty = f_p.x;
            float e = u_wpp / period;
            cv *= smoothstep(0.0, e, s) * (1.0 - smoothstep(duty, duty + e, s));
        }
        c = col * cv; A = cv;
    } else if (kind == 1) {                            // lit disc with rim, spin meridian and halo
        vec2 q = f_w - a;
        float d = length(q) - r;
        float fill = f_c.z, rimw = f_c.w, spin = f_col.w;
        float haloR = f_p.x, haloK = f_p.y, lit = f_p.z, mer = f_p.w;
        float inner = cov(d, 0.0);
        vec2 n = q / max(r, 1e-6);
        float shade = mix(1.0, clamp(1.15 - 0.55 * length(n - vec2(-0.32, 0.38)), 0.35, 1.2), lit);
        vec3 body = col * shade;
        vec2 sd = vec2(-sin(spin), cos(spin));
        float merl = cov(abs(dot(q, sd)) - 0.8 * u_wpp, 0.0) * inner * mer;
        body *= 1.0 - 0.45 * merl;
        float rim = rimw > 0.0 ? cov(abs(d + rimw) - rimw, 0.0) : 0.0;
        vec3 rimc = col * 1.35 + 0.08;
        float ab = inner * fill;
        c = rimc * rim + body * ab * (1.0 - rim);
        A = rim + ab * (1.0 - rim);
        if (haloR > 0.0) {
            float g = exp(-0.5 * pow(max(d, 0.0) / haloR, 2.0)) * haloK * (1.0 - inner);
            c += col * g * 0.6;
        }
    } else if (kind == 2) {                            // ring
        float d = abs(length(f_w - a) - r) - f_c.z;
        float cv = cov(d, f_c.w);
        c = col * cv; A = cv;
    } else if (kind == 3) {                            // triangle
        float d = sdTri(f_w, a, b, f_c.xy);
        float cv = cov(d, f_p.x);
        c = col * cv; A = cv;
    } else if (kind == 4) {                            // label from the atlas (premultiplied sRGB)
        vec2 uv = mix(f_c.xy, f_c.zw, (f_w - (a - b)) / (2.0 * b));
        vec4 tx = texture(u_atlas, uv);
        float ta = tx.a;
        vec3 rgb = ta > 1e-4 ? pow(tx.rgb / ta, vec3(2.2)) : vec3(0.0);
        c = rgb * col * ta; A = ta;
    } else if (kind == 5) {                            // rounded rect, fill and/or outline
        vec2 ctr = 0.5 * (a + b), hb = 0.5 * (b - a);
        float rad = f_c.z;
        vec2 q = abs(f_w - ctr) - hb + rad;
        float d = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - rad;
        float fl = cov(d, 0.0) * f_c.w;
        float ol = f_col.w > 0.0 ? cov(abs(d) - f_col.w, 0.0) : 0.0;
        float cv = max(fl, ol);
        c = col * cv; A = cv;
    } else {                                           // gaussian dot
        vec2 q = f_w - a;
        float g = exp(-dot(q, q) / (2.0 * r * r));
        c = col * g; A = g;
    }
    o = vec4(c * alpha, A * alpha * (1.0 - add));
}
