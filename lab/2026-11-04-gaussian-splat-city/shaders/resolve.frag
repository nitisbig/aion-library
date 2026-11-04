// premultiplied splat buffer over black → colour + linear depth (alpha) for the DOF pass
in vec2 uv; uniform sampler2D acc, dep; out vec4 o;
void main() {
    vec4 c = texture(acc, uv);
    vec4 d = texture(dep, uv);
    o = vec4(c.rgb, d.a > 0.02 ? d.r / d.a : 1e4);
}
