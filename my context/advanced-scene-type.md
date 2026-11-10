Here's the best fit for each scene type, with the runner-up in parentheses.

**Surfaces and geometry**
- Parametric surface: **Manim** (PyVista for heavy meshes)
- Height-field graph and tangent plane: **Manim**
- Implicit surface: **PyVista** (marching cubes), or **ModernGL** for SDF raymarching
- Tube or ribbon curves, knots: **PyVista**
- Riemann surface: **Manim**, or **ModernGL** for smooth coloring
- Geodesics on a manifold: **PyVista**

**Point-based**
- Point cloud: **PyVista** (ModernGL for millions of points)
- Gaussian splats: **ModernGL**, with sorted instanced quads and a custom shader (Taichi for the preprocessing)
- Particle systems: **Taichi** (ModernGL for rendering)
- Instanced glyphs: **PyVista**, or **ModernGL** for huge counts

**Fields and volumes**
- Vector field and streamlines: **Manim** in 2D, **PyVista** in 3D
- Isosurfaces: **PyVista**
- Volume rendering: **PyVista** (Taichi or ModernGL for custom transfer functions)
- Contour stack: **PyVista**
- Tensor field glyphs: **PyVista**
- Voxel grid: **PyVista**, or **Taichi** for large or dynamic grids
- Raymarched fractals: **ModernGL** shaders (Taichi works too)

**Complex analysis**
- Domain coloring: **ModernGL** fragment shader (Manim's ComplexPlane for light use)
- Conformal grid map: **Manim**
- Riemann sphere: **Manim**
- Möbius transformations: **Manim**

**Linear algebra**
- 2D/3D grid transforms: **Manim**
- Eigenvectors and SVD ellipsoid: **Manim**
- 4D projections: **Manim**, or **ModernGL** for smooth rotation

**Calculus and transforms**
- Solids of revolution and slicing: **Manim**
- Riemann sums in 3D: **Manim**
- Gradient descent on a loss surface: **Manim**
- Fourier epicycles: **Manim**
- Laplace s-plane surface: **Manim**
- 3D spectrogram or wavelet: **PyVista**

**Dynamics**
- Strange attractors: **Taichi** for the integration, with **ModernGL** or **PyVista** for rendering
- Phase portrait: **Manim**
- Bifurcation diagram: **Taichi**, because it needs millions of iterations
- Reaction-diffusion: **Taichi**
- Fluid simulation: **Taichi**
- N-body simulation: **Taichi**

**Topology and discrete**
- Graph layout: **Manim**
- Delaunay or Voronoi: **PyVista** in 3D, **Manim** in 2D
- Simplicial complex: **PyVista**
- Hyperbolic tiling: **Manim** (ModernGL for dense tilings)

**ML-flavored**
- NeRF or neural SDF: **Taichi** or **ModernGL**
- Embedding space: **PyVista**, or **ModernGL** for very large clouds

**How they fit together**
- **Manim** handles the scene, camera, labels, equations and animation timing.
- **Taichi** computes the heavy simulation and writes arrays.
- **ModernGL** renders custom shader effects such as splats, domain coloring and fractals.
- **PyVista** handles meshes and scientific visualization.

To combine them, render the Taichi, ModernGL or PyVista output off-screen as frames, then composite those frames into the Manim scene as an `ImageMobject` or video layer.