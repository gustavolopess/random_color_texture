from OpenGL.raw.GLUT import glutBitmapCharacter

from OpenGL.raw.GLUT.constants import GLUT_RGB

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from background import run
from config import Settings
import dialog
from PyQt4 import QtGui
import argparse, sys, dialog, os.path


width, height = 800, 600

settings = Settings()

colors_to_randomize = {
    'R': False,
    'G': False,
    'B': False
}

random_factor = 0

window = None


PROMPT = ("ESC - EXIT","C - CHANGE OBJECT FILE")

def checkArgs():
    global colors_to_randomize, random_factor

    parser = argparse.ArgumentParser(description="random texture through coloring")
    parser.add_argument('random_factor', metavar='F', help='random factor (between 0 and 1)')
    parser.add_argument('--colors', metavar='C', default='RGB', help='type colors which must be randomized (e.g: RGB)')

    args = parser.parse_args()

    if not (0 <= float(args.random_factor) <= 1):
        print "Invalid arg %r (must be in [0, 1] interval)" % args.random_factor
        print "type python %s -h for informations." % sys.argv[0]
        sys.exit(1)

    for c in args.colors:
        if str(c).upper() not in ['R', 'G', 'B']:
            print "Invalid arg %r (option %r doesn't exist)" % (args.colors, c)
            print "type python %s -h for informations." % sys.argv[0]
            sys.exit(1)
        colors_to_randomize[str(c).upper()] = True

    random_factor = args.random_factor


def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glPointSize(2.0)
    glBegin(GL_POINTS)
    glColor3f(0.0, 1.0, 1.0)

    print '\nLoading new object, please wait.'
    sc = run(width, height, colors_to_randomize, float(random_factor), settings)
    print 'object successfully loaded\n'

    glEnd()
    glFlush()
    glutSwapBuffers()


def handleKeyboard(*args):
    global settings
    ESC = '\x1b'

    if args[0] == ESC:
        glutDestroyWindow(window)
    elif args[0] == 'c':
        path = raw_input('\n> enter the path to new object file: ')
        if os.path.isfile(path):
            settings.object_input = path
        else:
            print 'Sorry, the path you entered does not exist.\n'
            return
        camera_path = raw_input('> enter the path to correspondent camera file: ')
        if os.path.isfile(camera_path):
            settings.camera_input = camera_path
        else:
            print 'The camera path you entered does not exist. The actual will be used.\n'

        glutPostRedisplay()



def init():
    glClear(GL_COLOR_BUFFER_BIT)

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glOrtho(0.0, width, height, 0.0, -5.0, 5.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


if __name__ == '__main__':
    checkArgs()

    print "\nPress 'c' to change the object file.\nPress ESC to exit\n"
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow('Random Color Texture')

    glutDisplayFunc(render)
    glutKeyboardFunc(handleKeyboard)

    glClearColor(1,1,1,1)
    init()
    glutMainLoop()