in vec2 uv; uniform sampler2D tex; uniform float u_scale; out vec4 o;
void main() { o = vec4(texture(tex, uv).rgb * u_scale, 1.0); }
