import numpy as np
import pygame
from plyfile import PlyData
pygame.init()

'''
EN: "What is the purpose of this?" you ask. Then I ask you:  How to see a 3D object in a 2D Screen?
     
    The objective of this script is to receive a .ply arquive (contains thousands of thousands of data) and
    make visible in a 2D screen. The problem is that isn't that easy to do this. a 3D object has 3 coordinates
    (x, y, z) and we need  to compress this in an image with 2 coordinates (x, y).

    The solution? Besides using homogeneous coordinates, we use Quaternions!
    This script implements manual transformations, perspective, projection matrixes and 3D rotations via
    quaternions from scratch using only numpy (for simple calculations) and pygame (for display visualization)

PTBR: "Qual o objetivo disso?" você pergunta, daí eu te pergunto: Como ver um objeto 3D em uma tela 2D?

    O objetivo deste script é receber um arquivo .ply (que contém milhares de milhares de dados) e torná-lo 
    visível em uma tela 2D. O problema é que não é tão fácil fazer isto. Um objeto 3D tem 3 coordenadas (x, y, z) 
    e precisamos comprimi-las em uma imagem com 2 coordenadas (x, y).

    A solução? Além de usar coordenadas homogêneas, usamos Quatérnios! Este script implementa transformações 
    manuais de matrizes de perspectiva e projeção, além de rotações 3D via quaternions do zero, usando apenas 
    numpy (para cálculos simples) e pygame (para visualização na tela).'''

# Variables for loading data and future functions applications
dados           = PlyData.read('bun_zipper.ply')
anguloRotacao   = 0

# If u want to make some chagens while testing the 3D projection, you can either change the (focoProjetivo) values
# or change the principal vector (vetorDiretor) with...
# [1, 1, 1] -> Rotates in all axis
# [1, 0, 0] -> Rotates only in Y and Z
# and so on...
vetorDiretor    = np.array([0, 1, 0], dtype = float)
focoProjetivo   = 2

# pygame purpose
largura, altura = 1280, 720
centroX = largura // 2
centroY = altura // 3
escala  = 3000

tela    = pygame.display.set_mode((largura, altura))
relogio = pygame.time.Clock()
aberto  = True

# To initiate, firstly we need to organize the .ply data we receive in a N X 3 matrix
# This function receive _arquivo_ that contains the .ply data
def OrganizarDados(arquivo):

    # This commands read the columns and make every coordinate have your own data. Then numpy array them
    X = arquivo['vertex']['x']
    Y = arquivo['vertex']['y']
    Z = arquivo['vertex']['z']
    v = np.column_stack((X, Y, Z))
    '''
    example of the matrix:
       [[-0.0378297   0.12794     0.00447467]
        [-0.0447794   0.128887    0.00190497]
        [-0.0680095   0.151244    0.0371953 ]
        ...
        [-0.0704544   0.150585   -0.0434585 ]
        [-0.0310262   0.153728   -0.00354608]
        [-0.0400442   0.15362    -0.00816685]]
    (this is the bunny matrix)'''
    # Use this if u want a bigger .ply arquive v = v[::10]
    return v
matrizOrganizada = OrganizarDados(dados)

# To use homogeneous coordinates and the others calculation, we need to add +1 columnin our data matrix
# In a little you will see the necessity of this
def QuartaColuna(matriz):

    # First we create a w matrix with matriz.shape[0] rows
    w = np.ones(matriz.shape[0])
    # Then we create a new matrix that has N x 3+1
    NovM = np.column_stack((matriz, w))
    '''
       [[-0.0378297   0.12794     0.00447467  1.        ]
        [-0.0447794   0.128887    0.00190497  1.        ]
        [-0.0680095   0.151244    0.0371953   1.        ]
        ...
        [-0.0704544   0.150585   -0.0434585   1.        ]
        [-0.0310262   0.15372799 -0.00354608  1.        ]
        [-0.0400442   0.15362    -0.00816685  1.        ]]'''
    
    return NovM
novaMatriz = QuartaColuna(matrizOrganizada)

# The GerarTranslacao() function have the simple purpose of translate the 3D Image in an vector direction
def GerarTranslacao():

    # We create a 4 x 4 matrix then add the translation factors on the last row
    Tx, Ty, Tz = 0, -0.1, 0
    matTrans = np.identity(4)
    matTrans[3, 0] = Tx
    matTrans[3, 1] = Ty
    matTrans[3, 2] = Tz
    '''
       [[ 1.   0.   0.   0. ]
        [ 0.   1.   0.   0. ]
        [ 0.   0.   1.   0. ]
        [ 0.  -0.1  0.   1. ]]'''
    
    return matTrans
matrizTranslacao = GerarTranslacao()

# This function is really important. He make the sense of depth of a 3D object!
def GerarPerspectiva(foco):

    matriz = np.identity(4)
    # The function places the 1 / focal_length into the perspective slot to divide W by Z later during projection
    matriz[2, 3] = 1 / foco
    return matriz 
matrizPerspectiva = GerarPerspectiva(focoProjetivo)

# THE FUNCTION THAT MADE ME CRAZY (Quaternion Rotation Matrix)
# The function converts an angle and a 3D vector into a unit quaternion, mapping it into a 4 x 4 matrix
def GerarRotacaoQuaternaria(angulo, vetor):

    # Convert angle to radians
    anguloRadiano = np.radians(angulo)

    # Then normalize the vector so its length equals 1
    norma   = np.sqrt((vetor[0]**2 + vetor[1]**2 + vetor[2]**2))
    vetorNormalizado = vetor/norma

    # Calculate (w) escalar and (x, y, z) components of the quaternion
    w   = np.cos(anguloRadiano)
    x   = np.sin(anguloRadiano) * vetorNormalizado[0]
    y   = np.sin(anguloRadiano) * vetorNormalizado[1]
    z   = np.sin(anguloRadiano) * vetorNormalizado[2]
    q = np.array([w, x, y, z])
    
    # Here we apply the quaternion matrix definiton (I couldn't remember this thing alone, so don't worry lol)
    matRot = np.identity(4)

    matRot[0, 0] = w**2 + x**2 - y**2 - z**2
    matRot[0, 1] = 2 * x * y + 2 * w * z
    matRot[0, 2] = 2 * x * z - 2 * w * y

    matRot[1, 0] = 2 * x * y - 2 * w * z
    matRot[1, 1] = w**2 - x**2 + y**2 - z**2
    matRot[1, 2] = 2 * y * z + 2 * w * x

    matRot[2, 0] = 2 * x * z + 2 * w * y
    matRot[2, 1] = 2 * y * z - 2 * w * x
    matRot[2, 2] = w**2 - x**2 - y**2 + z**2

    return matRot

# Main loop for real-time rendering and animation
while aberto:

    tela.fill((30, 30, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            aberto = False

    # Increment rotation angle continuously to create real-time animation
    anguloRotacao += 1
    if anguloRotacao >= 360:
        anguloRotacao = 0

    # All the functions we had is now used here
    # Compose transformation in chain:      ROtation -> Translation -> Perspective Projection
    matrizRotacao = GerarRotacaoQuaternaria(anguloRotacao, vetorDiretor)
    matrizTransformacao = matrizRotacao @ matrizTranslacao @ matrizPerspectiva
    matrizProjetada = novaMatriz @ matrizTransformacao

    # Homogeneous normalization
    # This is where we create the projection perspective
    # We divide (X) and (Y) by (W / Z) coordinates
    Z = matrizProjetada[:, 3]
    xFinal = matrizProjetada[:, 0] / Z
    yFinal = matrizProjetada[:, 1] / Z

    # (for) function that create the image pixels! :D
    for i in range(len(matrizProjetada)):
        pixelX = int(xFinal[i] * escala + centroX)
        pixelY = int(-yFinal[i] * escala + centroY)

        tela.set_at((pixelX, pixelY), (255, 255, 255))

    pygame.display.set_caption('3D Projection Perspective & Quaternions Rotations')
    pygame.display.flip()
    relogio.tick(30)