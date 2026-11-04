// Lit sphere impostor: dark translucent-looking body, coloured fresnel rim (bioluminescent), soft spec, emission.
// Writes true sphere depth; alpha = linear view depth for the DOF pass.
in vec3 v_col; in float v_emit; in float v_rpx; in float v_z; in float v_r; in float v_vis; in float v_group;
uniform float u_near, u_far, u_focus, u_fog, u_rim, u_amb, u_time;
out vec4 o;
void main() {
    float spx = 2.0 * v_rpx + 2.0;
    vec2 pc = (gl_PointCoord * 2.0 - 1.0) * vec2(1.0, -1.0) * (spx / max(2.0 * v_rpx, 1e-3));
    float r2 = dot(pc, pc);
    // objects right in front of the lens dissolve (dithered; the DOF pass smooths it)
    float nearf = v_group > 1.5 ? smoothstep(0.1, 0.3, v_z / u_focus) : smoothstep(0.3, 0.65, v_z / u_focus);
    if (nearf < fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453)) discard;
    // sub-pixel spheres: draw as a soft dot instead of aliasing
    float cover = 1.0;
    if (v_rpx < 1.0) { cover = v_rpx * v_rpx; r2 = min(r2, 0.99); }
    if (r2 > 1.0) discard;
    float nz = sqrt(1.0 - r2);
    vec3 n = vec3(pc, nz);
    vec3 L = normalize(vec3(-0.45, 0.6, 0.65));
    float lamb = max(dot(n, L), 0.0);
    float back = max(dot(n, normalize(vec3(0.5, -0.3, 0.4))), 0.0);
    float fres = pow(1.0 - nz, 2.2);
    float spec = pow(max(dot(reflect(-L, n), vec3(0, 0, 1)), 0.0), 28.0);
    vec3 c = v_col * (u_amb + 0.55 * lamb + 0.12 * back) + v_col * fres * u_rim + vec3(spec) * 0.35 * (0.3 + 0.7 * v_col)
           + v_col * v_emit;
    float zs = v_z - v_r * nz;
    float fog = exp(-max(zs - u_focus, 0.0) / (u_fog * u_focus));
    o = vec4(c * fog * v_vis * cover, zs);
    gl_FragDepth = log(max(zs, u_near) / u_near) / log(u_far / u_near);
}
