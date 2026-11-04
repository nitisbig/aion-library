// Edge filaments: Bézier polylines; colour runs from the source layer's hue to the target layer's.
in vec3 in_pos; in float in_s; in float in_e; in float in_l;
uniform sampler2D u_edge;                 // (NE × 2) RGBA32F rows: A, B
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_focus, u_dof, u_H;
uniform float u_layerK[8];
uniform vec3 u_lc[8];
out VS { float s; vec4 a; vec4 b; float coc; float k; vec3 c0; vec3 c1; } vs;
void main() {
    vec3 rel = in_pos - u_cam;
    float z = dot(rel, u_fwd);
    gl_Position = vec4(dot(rel, u_right) / (u_tanHalf * u_aspect), dot(rel, u_up) / u_tanHalf, 0.0, z);
    int e = int(in_e + 0.5), l = int(in_l + 0.5);
    vs.a = texelFetch(u_edge, ivec2(e, 0), 0);
    vs.b = texelFetch(u_edge, ivec2(e, 1), 0);
    vs.coc = u_dof * u_H * 0.006 * abs(1.0 - u_focus / max(z, 0.05));
    vs.s = in_s;
    vs.k = u_layerK[l];
    vs.c0 = u_lc[l]; vs.c1 = u_lc[l + 1];
}
