from PIL import Image
import moderngl

vertex_shader = '''
               #version 330 core
               in vec3 in_vert;
               void main() {
                   gl_Position = vec4(in_vert, 1.0);
               }
               '''
fragment_shader = '''
                #version 330 core

                uniform vec3 color;

                in vec3 out_normal;
                out vec4 f_color;

                const vec3 light1 = vec3(1, 1, -1);
                const vec3 light2 = vec3(0, 0, 1);

                const vec3 ambientLight = vec3(0.13, 0.13, 0.13);
                const float shininess = 16.0;
                void main() {
                    vec3 viewDir = vec3(0,0,1);
                    vec3 normal = normalize(out_normal);
                    float lambert1 = max(0, dot(normal, -normalize(light1)));
                    float lambert2 = max(0, dot(normal, -normalize(light2)));

                    vec3 halfDir = normalize(light2 + viewDir);
                    float specAngle = max(dot(halfDir, normal), 0.0);
                    float specular = pow(specAngle, shininess);


                    vec3 final_color = ambientLight + 
                                         0.8 * lambert1 * color + 
                                         1.0 * lambert2 * color;

                    f_color = vec4(final_color, 1.0);
                }
                '''
geometry_shader = '''
                #version 330 core

                layout(triangles) in;
                layout(triangle_strip, max_vertices = 3) out;

                out vec3 out_normal;

                void main() {
                    vec4 edge1 = gl_in[0].gl_Position - gl_in[1].gl_Position;
                    vec4 edge2 = gl_in[0].gl_Position - gl_in[2].gl_Position;
                    out_normal = cross(edge1.xyz, edge2.xyz);

                    for(int i = 0; i < 3; i++) {
                        gl_Position = gl_in[i].gl_Position;
                        EmitVertex();
                    }
                    EndPrimitive();
                }
                '''


class ModelRenderer:
    def __init__(self, num_vertices, faces, image_size=128, num_samples=8):
        """
        Class for rendering a model from vertices and face list

        :param num_vertices: number of vertices to render (-1 if flexible)
        :param faces: list of triangles, given in the index buffer format
        :param image_size: Size of the output image
        :param num_samples: Number of samples for super-sampling
        """
        self.image_size = image_size
        self.num_vertices = num_vertices
        self.faces = faces
        self.num_samples = num_samples

        # graphics
        self.ctx = moderngl.create_standalone_context()

        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        self.prog = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
            geometry_shader=geometry_shader
        )

        self.vboPos = self.ctx.buffer(reserve=num_vertices * 3 * 4, dynamic=True)

        self.ibo = self.ctx.buffer(self.faces.astype('i4').tobytes())

        vao_content = [
            # 3 floats are assigned to the 'in' variable named 'in_vert' in the shader code
            (self.vboPos, '3f', 'in_vert')
        ]

        self.vao = self.ctx.vertex_array(self.prog, vao_content, self.ibo)

        # Framebuffers
        self.fbo1 = self.ctx.framebuffer([self.ctx.renderbuffer((image_size, image_size), samples=self.num_samples)])
        self.fbo2 = self.ctx.framebuffer([self.ctx.renderbuffer((image_size, image_size))])

    def __del__(self):
        self.prog.release()
        self.vboPos.release()
        self.ibo.release()
        self.vao.release()
        self.fbo1.release()
        self.fbo2.release()

    def render(self, vertices, color=(1, 0, 0), background=(0.9, 0.9, 0.9)):
        """
        Render a model
        :param vertices: vertices of model render
        :param color: color of the model
        :param background: color of the background
        :return image of the hand
        """

        self.vboPos.write(vertices.astype('f4').tobytes())

        self.prog['color'].value = color

        # Rendering
        self.fbo1.use()
        self.ctx.clear(*background)
        self.vao.render()

        # Down-sampling and loading the image using Pillow
        self.ctx.copy_framebuffer(self.fbo2, self.fbo1)
        data = self.fbo2.read(components=3, alignment=1)
        img = Image.frombytes('RGB', self.fbo2.size, data).transpose(Image.FLIP_TOP_BOTTOM)

        return img
