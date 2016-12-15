# -*- coding: utf-8 -*-
import numpy as np
from config import Settings
from operations import vector
from operations.escalonar import Escalona
from operator import itemgetter
from operations.triangle import Triangle, TriangleWithRef, PointP4
from operations.linha import Linha
from operations.rgb import RGB
from OpenGL.GLUT import *
from OpenGL.GL import *

settings = Settings()

class Scene(object):
    """docstring for Scene"""

    def __init__(self, calice_input, ilumination_input):
        super(Scene, self).__init__()
        
        self.debug = True

        self.r = 0
        self.t = 0

        self.points = []
        self.triangles = []
        self.triangles_view_objects = []
        self.triangles_screen_objects = []
        self.points_normal = []
        self.triangles_normal = []
        self.view_coordinates = []
        self.screen_coordinates = []

        self.random_factor = 0.0
        self.n_factor = 0.0
        self.pl = 0.0
        self.ka = 0.0
        self.ia = 0.0
        self.kd = 0.0
        self.od = 0.0
        self.ks = 0.0
        self.il = 0.0


        self.z_buffer = []
        self.load_vertices(calice_input)
        self.load_ilumination(ilumination_input)

    def init_zbuffer(self, height, width):
        self.z_buffer = np.array([[99999999]*height for i in range(0, width)])

    def load_vertices(self, calice_input):
        with open(calice_input) as calice_config:
            lines = calice_config.readlines()

        number_points = int(lines[0].split(" ")[0])
        triangles = int(lines[0].split(" ")[1])

        for x in range(1, number_points + 1):
            self.points.append(np.array([
                float(lines[x].splitlines()[0].split(" ")[0]),
                float(lines[x].splitlines()[0].split(" ")[1]),
                float(lines[x].splitlines()[0].split(" ")[2])
            ]))

            self.points_normal.append(np.array([0.0, 0.0, 0.0]))

        for x in range(number_points + 1, len(lines)):
            self.triangles.append(np.array([
                int(lines[x].splitlines()[0].split(" ")[0]),
                int(lines[x].splitlines()[0].split(" ")[1]),
                int(lines[x].splitlines()[0].split(" ")[2])
            ]))


    def load_ilumination(self, ilumination_input):
        '''Carrega os dados de illuminação'''
        with open(ilumination_input, 'r') as illumination:
            lines = illumination.readlines()
            self.n_factor = float(lines[-1])
            self.pl = np.array([float(lines[0].split(" ")[0]),
                                float(lines[0].split(" ")[1]),
                                float(lines[0].split(" ")[2])
                                ])
            self.ka = float(lines[1])

            # self.ia = np.array([float(lines[2].split(" ")[0]),
            #                     float(lines[2].split(" ")[1]),
            #                     float(lines[2].split(" ")[2])
            #                     ])

            self.ia = RGB(float(lines[2].split(" ")[0]),
                    float(lines[2].split(" ")[1]),
                    float(lines[2].split(" ")[2])
                    )
            self.kd = float(lines[3])

            # self.od = np.array([float(lines[4].split(" ")[0]),
            #                     float(lines[4].split(" ")[1]),
            #                     float(lines[4].split(" ")[2])
            #                     ])

            self.od = RGB(float(lines[4].split(" ")[0]),
                    float(lines[4].split(" ")[1]),
                    float(lines[4].split(" ")[2])
                    )
            self.ks = float(lines[5])

            # self.il = np.array([float(lines[6].split(" ")[0]),
            #                     float(lines[6].split(" ")[1]),
            #                     float(lines[6].split(" ")[2])
            #                     ])

            self.il = RGB(float(lines[6].split(" ")[0]),
                                float(lines[6].split(" ")[1]),
                                float(lines[6].split(" ")[2])
                                )

    '''a iluminação de phong é caracterizada pela junção dos vetores de iluminação
        de ambiente, difusa e especular'''
    '''
        | ; Pl - Posicao da luz em coordenadas de mundo
        | ; ka - reflexao ambiental
        | ; Ia - vetor cor ambiental
        | ; kd - constante difusa
        | ; Od - vetor difuso
        | ; ks - parte especular
        | ; Il - cor da fonte de luz
        | ; n  - constante de rugosidade
    '''
    '''
        final_color = ambient_component + diffuse_component + specular_component
    '''

    def pixel_phong_ilumination(self, ponto, N):

        ia = self.ia*self.ka
        l = (self.pl - ponto)
        l = vector.normalize(l)
        N = vector.normalize(N)
        id = RGB(0,0,0)
        ie = RGB(0,0,0)

        # id = np.array([0,0,0])
        # ie = np.array([0,0,0])

        if (np.dot(N, l) >= 0):
            id = (self.od%self.il) * self.kd * (np.dot(N,l))
            v = vector.normalize(-ponto)

            if (np.dot(N,v) < 0):
                N = -N
            r = vector.normalize((N * 2)*(np.dot(N,l)) - l)
            if (np.dot(v,r) >= 0):
                ie = (self.il) * self.ks * (pow(np.dot(r, v), self.n_factor))
        else:
            print "Não entrei"
        color = ia + id + ie
        # print color
        # final_color = np.array([int(color[0]%256), int(color[1]%256), int(color[2]%256) ])
        return color

        #         saturate = lambda x: max(0, min(1, x))

        # L = -vector.normalize(self.pl - focused_px)
        # N = vector.normalize(N)
        # NL = saturate(np.dot(N, L))
        # R = vector.normalize(2 * NL * N - L)
        # RV = saturate(np.dot(R, V))

        # ambient_component = self.ka * self.ia
        # diffuse_component = self.kd*NL
        # specular_component = self.ks*pow(RV, self.n_factor)

        # color = self.od*ambient_component + self.od*(self.il*(diffuse_component + specular_component))

        # final_color = np.array([ int(color[0]%255), int(color[1]%255), int(color[2]%255) ])
        # return final_color



    def illumination_values(self):
        '''função de depuração só pra checar se os valores recebidos estão corretos'''
        print self.pl, "pl"
        print self.ka, "ka"
        print self.ia, "ia"
        print self.kd, "kd"
        print self.od, "od"
        print self.ks, "ks"
        print self.il, "il"
        print self.n_factor, "n_factor"

    def equal(self, a, b):
        if (abs(a - b) < (10 ** -12)):
            return True
        return False

    def get_ab(self ,p1, p2, p3):
        if (self.equal(abs(p2[0] - p1[0]),0)):
            return (1,0)
        
        b = (p3[0] - p1[0])/(p2[0] - p1[0])
        a = 1 - b
        return (a, b)

    def create_triangle_screen_objects(self):
        for t in self.triangles:
            p1, p2, p3 = self.screen_coordinates[t[0] - 1], self.screen_coordinates[t[1] - 1], self.screen_coordinates[t[2] - 1]
            self.triangles_screen_objects.append(Triangle(p1, p2, p3))

    def call_triangle_rasterization(self):
        for t in self.triangles:
            self.draw_triangle_rasterization(t[0] - 1, t[1] - 1, t[2] - 1)


    def draw_triangle_rasterization(self, p1, p2, p3):
        ref_v1 = p1
        ref_v2 = p2
        ref_v3 = p3

        p1 = self.screen_coordinates[p1]
        p2 = self.screen_coordinates[p2]
        p3 = self.screen_coordinates[p3]

        auxTr = TriangleWithRef(p1, ref_v1, p2, ref_v2, p3, ref_v3)

        # Caso dos vertices serem colineares. (acho que nem deveria existir, mas sem ele nao funciona) 
        if auxTr.v1[1] == auxTr.v2[1] and auxTr.v1[1] == auxTr.v3[1]:
            auxTr.sort_asc_x()
            self.draw_line(auxTr.v1_ref, auxTr.v3_ref)
            self.r+=1
        else:
            auxTr.sort_asc_y()
            self.draw_dynamic(auxTr)

        # print self.r, self.t

    def draw_dynamic(self, auxTr):
        if auxTr.v2[1] == auxTr.v3[1]:
            newTr_bottom_flat = TriangleWithRef(auxTr.v1, auxTr.v1_ref, auxTr.v2, auxTr.v2_ref, auxTr.v3, auxTr.v3_ref)
            self.fill_bottom_flat_triangle(newTr_bottom_flat)
            self.t+=1
        elif auxTr.v1[1] == auxTr.v2[1]:
            newTr_top_flat = TriangleWithRef(auxTr.v1, auxTr.v1_ref, auxTr.v2, auxTr.v2_ref, auxTr.v3, auxTr.v3_ref)
            self.fill_top_flat_triangle(newTr_top_flat)
            self.t+=1
        else:
            p4 = np.array([int(auxTr.v1[0] + (float(auxTr.v2[1] - auxTr.v1[1]) / float(auxTr.v3[1] - auxTr.v1[1])) * (auxTr.v3[0] - auxTr.v1[0])), int(auxTr.v2[1])])
            self.t+=1

            line1 = Linha(auxTr.v1[0], auxTr.v2[0],
            auxTr.v3[0], p4[0])

            line2 = Linha(auxTr.v1[1], auxTr.v2[1],
            auxTr.v3[1], p4[1])

            line3 = Linha(1, 1, 1, 1)

            a, b, c = Escalona(line1, line2, line3).esc()

            p4_ponto_view = self.view_coordinates[auxTr.v1_ref] * a + self.view_coordinates[auxTr.v2_ref] * b + self.view_coordinates[auxTr.v3_ref] * c
            res1 = self.points_normal[auxTr.v1_ref] * a
            res2 = self.points_normal[auxTr.v2_ref] * b
            res3 =  self.points_normal[auxTr.v3_ref] * c
            p4_normal = res1 + res2 + res3

            self.screen_coordinates.append(p4)
            self.view_coordinates.append(p4_ponto_view)
            self.points_normal.append(p4_normal)

            newTr_bottom_flat = TriangleWithRef(auxTr.v1, auxTr.v1_ref, auxTr.v2, auxTr.v2_ref, p4, len(self.screen_coordinates) - 1)
            newTr_top_flat = TriangleWithRef(auxTr.v2, auxTr.v2_ref, p4, len(self.screen_coordinates) - 1, auxTr.v3, auxTr.v3_ref)

            self.fill_bottom_flat_triangle(newTr_bottom_flat)
            self.fill_top_flat_triangle(newTr_top_flat)

    def draw_line(self, p1, p2):
        x1 = self.screen_coordinates[p1][0]
        sline = self.screen_coordinates[p1][1]
        x2 = self.screen_coordinates[p2][0]

        while(x1 <= x2):
            a, b = self.get_ab(self.screen_coordinates[p1], self.screen_coordinates[p2], np.array([x1, sline]))
            ponto = self.view_coordinates[p1]*a + self.view_coordinates[p2] * b
            
            if (self.z_buffer[int(x1 + 0.5)][int(sline + 0.5)] > ponto[2]):
                self.z_buffer[int(x1 + 0.5)][int(sline + 0.5)] = ponto[2]
                normal = self.points_normal[p1] * a + self.points_normal[p2] * b

                color = self.pixel_phong_ilumination(ponto, normal)
                color = color/255.0
                # glColor3f(color[0],color[1],color[2])
                glColor3f(color.r,color.g,color.b)
                glVertex2f(x1, sline)
            x1 += 1

    def fill_bottom_flat_triangle(self, triang_bottom):
        invslope1 = float(triang_bottom.v2[0] - triang_bottom.v1[0]) / (triang_bottom.v2[1] - triang_bottom.v1[1])
        invslope2 = float(triang_bottom.v3[0] - triang_bottom.v1[0]) / (triang_bottom.v3[1] - triang_bottom.v1[1])

        curx1 = float(triang_bottom.v1[0])
        curx2 = float(triang_bottom.v1[0]) + 0.5

        if invslope1 > invslope2:
            aux = invslope1
            invslope1 = invslope2
            invslope2 = aux

        scanlineY_v1 = triang_bottom.v1[1]
        line3 = Linha(1, 1, 1, 1)

        while(scanlineY_v1 <= triang_bottom.v2[1]):
            x_auxiliar = curx1
            while(x_auxiliar <= curx2):
                line1 = Linha(triang_bottom.v1[0], triang_bottom.v2[0], triang_bottom.v3[0], 
                x_auxiliar)
                line2 = Linha(triang_bottom.v1[1], triang_bottom.v2[1], triang_bottom.v3[1],
                    scanlineY_v1)

                a, b, c = Escalona(line1, line2, line3).esc()

                ponto = self.view_coordinates[triang_bottom.v1_ref] * a + self.view_coordinates[triang_bottom.v2_ref] * b + self.view_coordinates[triang_bottom.v3_ref] * c
                if (self.z_buffer[int(x_auxiliar + 0.5)][int(scanlineY_v1 + 0.5)] > ponto[2]):
                    self.z_buffer[int(x_auxiliar + 0.5)][int(scanlineY_v1 + 0.5)] = ponto[2]
                    normal = self.points_normal[triang_bottom.v1_ref] * a + self.points_normal[triang_bottom.v2_ref] * b + self.points_normal[triang_bottom.v3_ref] * c
                    
                    # if self.debug:
                    #     print "Hello - Bottom"
                    #     self.debug = False
                    #     print a, b, c
                    #     print normal
                    #     print self.points_normal[triang_bottom.v1_ref]


                    color = self.pixel_phong_ilumination(ponto, normal)
                    color = color/255.0
                    # glColor3f(color[0], color[1],color[2])
                    glColor3f(color.r, color.g,color.b)
                    glVertex2i(int(x_auxiliar + 0.5), int(scanlineY_v1 + 0.5))
                x_auxiliar += 1
            scanlineY_v1 += 1
            curx1 += invslope1
            curx2 += invslope2

    def fill_top_flat_triangle(self, triang_top):
        invslope1 = float(triang_top.v3[0] - triang_top.v1[0]) / (triang_top.v3[1] - triang_top.v1[1])
        invslope2 = float(triang_top.v3[0] - triang_top.v2[0]) / (triang_top.v3[1] - triang_top.v2[1])

        curx1 = float(triang_top.v3[0])
        curx2 = float(triang_top.v3[0]) + 0.5
        
        if invslope1 < invslope2:
            aux = invslope1
            invslope1 = invslope2
            invslope2 = aux

        scanlineY_v1 = triang_top.v3[1]
        line3 = Linha(1, 1, 1, 1)

        while(scanlineY_v1 > triang_top.v1[1]):
            x_auxiliar = curx1
            while(x_auxiliar <= curx2):
                line1 = Linha(triang_top.v1[0], triang_top.v2[0], triang_top.v3[0], 
                x_auxiliar)
                line2 = Linha(triang_top.v1[1], triang_top.v2[1], triang_top.v3[1],
                    scanlineY_v1)

                a, b, c = Escalona(line1, line2, line3).esc()

                ponto = self.view_coordinates[triang_top.v1_ref] * a + self.view_coordinates[triang_top.v2_ref] * b + self.view_coordinates[triang_top.v3_ref] * c
                if (self.z_buffer[int(x_auxiliar + 0.5)][int(scanlineY_v1 + 0.5)] > ponto[2]):
                    self.z_buffer[int(x_auxiliar + 0.5)][int(scanlineY_v1 + 0.5)] = ponto[2]
                    normal = self.points_normal[triang_top.v1_ref] * a + self.points_normal[triang_top.v2_ref] * b + self.points_normal[triang_top.v3_ref] * c
                    color = self.pixel_phong_ilumination(ponto, normal)
                    color = color/255.0
                    # glColor3f(color[0], color[1], color[2])
                    glColor3f(color.r, color.g,color.b)
                    
                    glVertex2i(int(x_auxiliar + 0.5), int(scanlineY_v1 + 0.5))
                x_auxiliar += 1
            scanlineY_v1 -= 1
            curx1 -= invslope1
            curx2 -= invslope2