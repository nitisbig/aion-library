in vec2 uv; uniform sampler2D A, B; uniform float wA, wB; out vec4 o;
void main() { o = vec4(texture(A, uv).rgb * wA + texture(B, uv).rgb * wB, 1.0); }
