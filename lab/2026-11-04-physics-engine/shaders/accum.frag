in vec2 uv; uniform sampler2D tex; uniform float u_w; out vec4 o;
void main() { o = vec4(texture(tex, uv).rgb * u_w, 1.0); }
