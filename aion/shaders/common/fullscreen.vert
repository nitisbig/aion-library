#version 330
// Fullscreen triangle (no vertex buffer). v_uv in [0,1]; v_pos in Manim units
// after the inverse camera, so shaders draw in the same space as Manim mobjects.
uniform vec2 u_frame;       // Manim frame size in units (e.g. 14.222, 8)
uniform mat3 u_view_inv;    // screen(units) -> world(units)
out vec2 v_uv;
out vec2 v_pos;
void main() {
    vec2 p = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2);
    v_uv = p;
    vec2 screen = (p - 0.5) * u_frame;
    v_pos = (u_view_inv * vec3(screen, 1.0)).xy;
    gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
}
