in vec4 in_k; in vec4 in_ab; in vec4 in_c; in vec4 in_col; in vec4 in_p;
out VS { vec4 k; vec4 ab; vec4 c; vec4 col; vec4 p; } vo;
void main() { vo.k = in_k; vo.ab = in_ab; vo.c = in_c; vo.col = in_col; vo.p = in_p; gl_Position = vec4(0.0); }
