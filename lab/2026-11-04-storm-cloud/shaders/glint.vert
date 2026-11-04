// every particle drawn as a droplet catching the lightning; out-of-focus droplets become bokeh discs;
// hidden when they sit behind the cloud's visible surface (depth from the ray march)
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanX, u_tanY, u_fy, u_px, u_focus, u_aper, u_glint, u_maxSize;
uniform vec3 u_lcol, u_amb, u_rainCol, u_rainLo, u_rainHi;
uniform sampler3D illum, sunVol;
uniform float u_sunOn, u_earthY;
uniform vec3 u_sunDir, u_sunCol;
uniform sampler2D depthTex;
out vec3 v_col;
out float v_edge, v_rim;
void main() {
    vec4 a, b;
    vec3 p = particlePos(gl_VertexID, a, b);
    gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
    gl_PointSize = 1.0;
    v_col = vec3(0.0);
    vec3 d = p - u_cam;
    float z = dot(d, u_fwd);
    if (z < 0.08) return;
    vec2 ndc = vec2(dot(d, u_right) / (z * u_tanX), dot(d, u_up) / (z * u_tanY));
    if (any(greaterThan(abs(ndc), vec2(1.15)))) return;
    float dist = length(d);
    float scene = texture(depthTex, ndc * 0.5 + 0.5).r;
    float occ = exp(-max(dist - scene, 0.0) / 0.3);
    if (occ < 0.01) return;
    vec3 rd = d / dist;
    vec4 I = texture(illum, boxUVW(p));
    float L = lightAt(p, rd, I);
    vec3 sunC = vec3(0.0);
    if (u_sunOn > 0.5)   // droplets sparkle most when looking toward the sun (forward scattering)
        sunC = u_sunCol * texture(sunVol, boxUVW(p)).r * min(phase(dot(rd, u_sunDir)), 2.5) * 0.5 * smoothstep(u_earthY - 0.8, u_earthY + 0.8, p.y);
    float kind = b.z;
    float e;
    vec3 base;
    if (kind > 1.5) {
        vec2 c = 0.5 * (u_rainLo.xz + u_rainHi.xz), hw = 0.5 * (u_rainHi.xz - u_rainLo.xz);
        float r = length((p.xz - c) / hw) + 0.3 * sin(p.y * 0.7 + b.y * 6.0);
        e = 0.3 * smoothstep(0.95, 0.35, r) * smoothstep(u_rainHi.y, u_rainHi.y - 0.6, p.y)
            * smoothstep(u_rainLo.y, u_rainLo.y + 3.0, p.y);
        base = L * u_rainCol;
    }
    else if (kind > 0.5) { e = u_sunOn > 0.5 ? 0.25 : 0.9; base = L * u_lcol + sunC + u_amb; }
    else { e = (0.08 + 4.0 * b.w) * (0.03 + 0.97 * carve(p)); base = L * u_lcol + sunC + u_amb * 0.5; }
    float energy = e * u_glint * occ * min((6.0 / z) * (6.0 / z), 40.0);
    float coc = u_aper * u_fy * abs(1.0 / u_focus - 1.0 / z);
    float bs = 1.15 * u_px;
    float size = clamp(max(bs, coc), bs, u_maxSize);
    energy *= (bs * bs) / (size * size);
    v_col = base * energy;
    if (max(v_col.r, max(v_col.g, v_col.b)) < 1e-4) return;
    v_edge = clamp(1.2 / size, 0.08, 1.0);
    v_rim = smoothstep(4.0, 14.0, size / u_px);
    gl_PointSize = size;
    gl_Position = vec4(ndc, 0.0, 1.0);
}
