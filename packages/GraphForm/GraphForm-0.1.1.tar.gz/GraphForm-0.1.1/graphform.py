from logging import getLogger, basicConfig, INFO, DEBUG
import sys
from p5 import *
import itertools as it
import sys
import numpy as np
import networkx as nx
from attrdict import AttrDict
from PIL.ImageFont import truetype

__version__ = "0.1.1"

class Interaction:
    def __init__(self, forcefunc):
        self.func = forcefunc

    def force(self, pairs, vertices):
        for a, b in pairs:
            vertex0 = vertices[a]
            vertex1 = vertices[b]
            d = vertex0.position - vertex1.position
            r = np.linalg.norm(d)
            f = self.func(r) * d / r
            vertex0.force -= f
            vertex1.force += f


def debug(func):
    def wrapper(*args, **kwargs):
        logger = getLogger()
        logger.debug(func.__name__)
        func(*args, **kwargs)
    return wrapper


def Depth(pi, pj, pk):
    return pi[2] + pj[2] + pk[2]


def ArrangedColor(a, b, c, decay):
    logger = getLogger()
    ab = b - a
    ac = c - a
    # normal vector
    n = np.cross(ab, ac)
    n /= np.linalg.norm(n)
    hue = abs(np.sum(n)) / sqrt(3.0)
    #hue = hue + 0.5
    if hue > 1.0:
        hue -= 1.0
    # final opacity is A+B
    A = 0.3
    B = 0.4
    opacity = (1. - 0.99**decay) * A + B
    return Color(hue, 0.8, abs(n[2]) * 0.4 + 0.6, alpha=opacity)


def perspective(v, eyepos=None):
    if eyepos is None:
        return v[:2]
    zoom = eyepos / (eyepos - v[2])
    return v[:2] * zoom


class Vertex():
    """
    A vertex is a point mass with a label.
    """

    def __init__(self, label, pos=None):
        self.label = str(label)
        if pos is None:
            self.position = np.random.random(3) * 500
        else:
            self.position = pos
        self.velocity = np.zeros(3)
        self.force = np.zeros(3)

    def perspective(self, eyepos=None):
        return perspective(self.position, eyepos)

    def force2vel(self):
        self.velocity = self.force + 0

    def progress(self, deltatime):
        self.position += self.velocity * deltatime

    # def draw(self):
    #     ellipse(self.position[0] - 1, self.position[1] - 1, 2, 2)
    def resetf(self):
        self.force = np.zeros(3)


def drawfaces_(faces, vertices):
    logger = getLogger()
    stroke(0)
    stroke_weight(2)
    k = faces.keys()
    for face in sorted(k, key=lambda x: -faces[x].depth):
        # triangle = PShape()
        va, vb, vc = face
        a = vertices[va].perspective()
        b = vertices[vb].perspective()
        c = vertices[vc].perspective()
        fill(faces[face].color)
        triangle(a, b, c)


class GraphForm():
    @debug
    def __init__(self, pairs):
        self.repulse = 0
        self.hold = None
        self.keyhold = None
        self.showface = True
        self.showlabel = True
        self.showtetrag = True
        self.decay = 0
        self.vertices = dict()
        self.triangles = dict()
        self.tetrahedra = set()
        self.tetrag = nx.Graph()  # adjacency graph of tetrahedra

        K = 2.5
        KR = 20
        R0 = 200
        #  立方体の一辺を1とすると面の対角線は√2、立方体の対角線は√3、隣接四面体間の距離は、√3/3
        # 面の対角線を1とするので、
        RT = R0 * (1 / 6)**0.5
        KT = 20

        self.attractive = Interaction(lambda r: K * (r - R0))

        def repel(r, K, rmin):
            """
            force function for replusive pairs
            """
            if r < rmin:
                return K * (r - rmin)
            return 0

        self.repulsive = Interaction(lambda r: repel(r, KR, R0 * 1.2))

        self.frames = 0

        labels = set()
        for i, j in pairs:
            labels.add(i)
            labels.add(j)
        labels = list(labels)

        self.g = nx.Graph(pairs)
        for i in labels:
            #position, velocity, force
            self.vertices[i] = Vertex(i)

        self.reps = [
            (i, j) for i, j in it.combinations(
                labels, 2) if not self.g.has_edge(
                i, j)]

        for i, j in self.g.edges():
            for v in self.g[j]:
                if v in self.g[i]:
                    s = tuple(sorted([i, j, v]))
                    self.triangles[s] = AttrDict(
                        {"depth": None, "color": None})

        for i, j, k in self.triangles:
            adj = tuple(set(self.g[i]) & set(self.g[j]) & set(self.g[k]))
            assert len(adj) <= 2
            pair = []
            for l in adj:
                s = tuple(sorted([i, j, k, l]))
                self.tetrahedra.add(s)
                pair.append(s)
            if len(pair) == 2:
                self.tetrag.add_edge(*pair)

        self.tetrepul = Interaction(lambda r: repel(r, KT, RT))

        # virtual vertices for tetrahedra
        self.vtet = dict()
        for t in self.tetrag:
            self.vtet[t] = Vertex(t)

    def drawtetranetwork(self):
        tpos = dict()
        for tetra in self.tetrag:
            com = np.zeros(3)
            for v in tetra:
                com += self.vertices[v].position
            tpos[tetra] = com / 4
        for edge in self.tetrag.edges:
            t1, t2 = edge
            p1 = perspective(tpos[t1])
            p2 = perspective(tpos[t2])
            stroke(1 / 6, 1, 0.8)  # yellow
            stroke_weight(4)
            line(p1, p2)

    def drawfaces(self):
        for i, j, k in self.triangles.keys():
            self.triangles[(i, j, k)].depth = Depth(
                self.vertices[i].position, self.vertices[j].position, self.vertices[k].position)
            self.triangles[(i,
                            j,
                            k)].color = ArrangedColor(self.vertices[i].position,
                                                      self.vertices[j].position,
                                                      self.vertices[k].position,
                                                      self.decay)
        drawfaces_(self.triangles, self.vertices)

    def drawedges(self):
        for a, b in self.g.edges():
            vertex0 = self.vertices[a].perspective()
            vertex1 = self.vertices[b].perspective()
            line(vertex0, vertex1)

    def drawlabels(self):
        for v in self.vertices.values():
            vv = v.perspective()
            fill(0)
            no_stroke()
            text(v.label, vv[0], vv[1])

    def draw(self):
        logger = getLogger()
        background(1, 0, 1)  # hsb
        self.frames += 1
        if self.frames == 100:
            self.repulse = 0
        self.decay += 1
        self.attractive.force(self.g.edges(), self.vertices)
        if self.repulse:
            fill(0)
            no_stroke()
            text("Repulsive", 40, 40)
            self.repulsive.force(self.reps, self.vertices)

        # 常に四面体同士は重ならないようにする。
         # if self.showtetrag:
        for vertex in self.vtet.values():
            vertex.resetf()
        for tetra, vertex in self.vtet.items():
            com = np.zeros(3)
            for v in tetra:
                com += self.vertices[v].position
            vertex.position = com / 4
        self.tetrepul.force(it.combinations(self.vtet, 2), self.vtet)
        # feedback the forces to its vertices
        for tetra, vertex in self.vtet.items():
            f = vertex.force
            for v in tetra:
                self.vertices[v].force += f

        for vertex in self.vertices.values():
            vertex.force2vel()
            vertex.progress(0.05)
            vertex.resetf()
        stroke(0)
        if self.showface:
            self.drawfaces()
        else:
            self.drawedges()
        if self.showlabel:
            self.drawlabels()
        if self.showtetrag:
            self.drawtetranetwork()
        # # マウスでノードをひっぱる。
        if mouse_is_pressed:
            decay = 0
            if self.hold is None:
                min = 100000.0
                nod = None
                for vertex in self.vertices.values():
                    pixel = vertex.perspective()
                    dx = mouse_x - pixel[0]
                    dy = mouse_y - pixel[1]
                    d = dx**2 + dy**2
                    if d < min:
                        min = d
                        self.hold = vertex
            pixel = self.hold.perspective()
            dx = mouse_x - pixel[0]
            dy = mouse_y - pixel[1]
            self.hold.position[0] += dx / 2
            self.hold.position[1] += dy / 2
        else:
            self.hold = None

        if key_is_pressed:
            if not self.keyhold:
                if key == "s":
                    save("graphform.png")
                    print ("Saved")
                if key == "r":
                    if not self.repulse:
                        self.repulse = 1
                    else:
                        self.repulse -= 1
                if key == "f":
                    self.showface = not self.showface
                if key == "l":
                    self.showlabel = not self.showlabel
                if key == "t":
                    self.showtetrag = not self.showtetrag
                if key == "q":
                    sys.exit(0)
            self.keyhold = True
        else:
            self.keyhold = None


    @debug
    def setup(self):
        size(512, 512)
        color_mode('HSB', 1, 1, 1, 1)
        font = truetype("Arial.ttf", size=16)
        text_font(font)


if __name__ == "__main__":
    # basicConfig(level=INFO, format="%(levelname)s %(message)s")
    basicConfig(level=DEBUG, format="%(levelname)s %(message)s")
    logger = getLogger()
    logger.debug("Debug mode.")

    pairs = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "F"), ("Z", "N"),
             ("A", "Z"), ("B", "Z"), ("C", "Z"), ("D", "Z"), ("E", "Z"), ("F", "Z"),
             ("A", "N"), ("B", "N"), ("C", "N"), ("D", "N"), ("E", "N"), ("F", "N"), ]
    gf = GraphForm(pairs)

    draw = gf.draw
    setup = gf.setup
    run()
