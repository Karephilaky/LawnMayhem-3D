from OpenGL.GL import *

def load_obj(filepath):
    vertices, faces = [], []
    with open(filepath) as f:
        for line in f:
            if line.startswith('v '):
                vertex = tuple(map(float, line.strip().split()[1:]))
                vertices.append(vertex)
            elif line.startswith('f '):
                face = [int(p.split('/')[0]) - 1 for p in line.strip().split()[1:]]
                faces.append(face)
    return vertices, faces

def draw_model(vertices, faces):
    glBegin(GL_QUADS)
    for face in faces:
        for vi in face:
            glVertex3fv(vertices[vi])
    glEnd()
