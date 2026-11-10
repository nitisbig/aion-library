#version 330
// Unit quad [-1,1]^2 (triangle strip, 4 vertices) mapped to clip space by u_mvp.
uniform mat3 u_mvp;
out vec2 v_uv;
void main() {
    vec2 c = vec2(gl_VertexID & 1, (gl_VertexID >> 1) & 1);
    v_uv = c;
    vec3 p = u_mvp * vec3(c * 2.0 - 1.0, 1.0);
    gl_Position = vec4(p.xy, 0.0, 1.0);
}
