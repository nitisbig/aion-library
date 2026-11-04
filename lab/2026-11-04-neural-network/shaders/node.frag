// Crisp lit sphere: solid layer-coloured body, sharp 1-px edge, light rim + specular, tight halo when active.
// Premultiplied output: blend ONE, ONE_MINUS_SRC_ALPHA.
in float v_rpx; in float v_coc; in float v_reveal; in float v_act; in float v_grad; in float v_kind; in vec3 v_col;
uniform vec3 u_hot;
uniform float u_margin, u_rim, u_body, u_core, u_idle, u_halo;
out vec4 o;
void main() {
    float spx = 2.0 * (v_rpx * u_margin + v_coc + 2.0);
    float scale = 0.5 * spx / max(v_rpx, 0.3);
    vec2 pc = (gl_PointCoord * 2.0 - 1.0) * vec2(1.0, -1.0) * scale;
    float r = length(pc);
    float aa = (0.7 + v_coc) / max(v_rpx, 0.3);
    float inside = 1.0 - smoothstep(1.0 - aa, 1.0 + aa, r);
    vec3 c = vec3(0.0);
    float alpha = 0.0;
    if (v_kind < 0.5) {
        float act = min(v_act + u_idle, 1.6);
        float nz = sqrt(max(1.0 - r * r, 0.0));
        float lamb = clamp(dot(vec3(pc, nz), normalize(vec3(-0.45, 0.55, 0.7))), 0.0, 1.0);
        vec3 lit = mix(v_col, u_hot, smoothstep(0.7, 1.5, act) * 0.6);
        vec3 body = v_col * (0.06 + 0.22 * lamb) + lit * act * u_core * (0.45 + 0.55 * lamb);
        float fres = pow(1.0 - nz, 3.0);
        vec3 rim = v_col * fres * u_rim;
        float spec = pow(clamp(dot(reflect(-normalize(vec3(-0.45, 0.55, 0.7)), vec3(pc, nz)), vec3(0, 0, 1)), 0.0, 1.0), 40.0) * 0.6;
        c = (body + rim + vec3(spec)) * inside;
        alpha = inside * u_body;
        float halo = exp(-max(r - 1.0, 0.0) * 7.0) * (1.0 - inside);
        c += lit * max(v_act, 0.0) * u_halo * halo;
    } else {
        c = u_hot * v_act * exp(-r * r * 6.0) * 2.0 + v_col * v_act * exp(-r * 3.0) * 0.3;   // the seed spark
    }
    float win = 1.0 - smoothstep(0.55 * scale, 0.98 * scale, r);
    o = vec4(c * v_reveal * win, alpha * v_reveal);
}
