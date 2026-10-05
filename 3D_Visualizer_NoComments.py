import numpy as np
import pygame
from plyfile import PlyData
pygame.init()

dados           = PlyData.read('bun_zipper.ply')
anguloRotacao   = 0
vetorDiretor    = np.array([1, 1, 1], dtype = float)
focoProjetivo   = 2

largura, altura = 1280, 720
centroX = largura // 2
centroY = altura // 3
escala  = 3000

tela    = pygame.display.set_mode((largura, altura))
relogio = pygame.time.Clock()
aberto  = True

def OrganizarDados(arquivo):

    X = arquivo['vertex']['x']
    Y = arquivo['vertex']['y']
    Z = arquivo['vertex']['z']
    v = np.column_stack((X, Y, Z))
    return v
matrizOrganizada = OrganizarDados(dados)

def QuartaColuna(matriz):

    w = np.ones(matriz.shape[0])    
    NovM = np.column_stack((matriz, w))
    return NovM
novaMatriz = QuartaColuna(matrizOrganizada)

def GerarTranslacao():

    Tx, Ty, Tz = 0, -0.1, 0
    matTrans = np.identity(4)
    matTrans[3, 0] = Tx
    matTrans[3, 1] = Ty
    matTrans[3, 2] = Tz
    return matTrans
matrizTranslacao = GerarTranslacao()

def GerarPerspectiva(foco):

    matriz = np.identity(4)
    matriz[2, 3] = 1 / foco
    return matriz 
matrizPerspectiva = GerarPerspectiva(focoProjetivo)

def GerarRotacaoQuaternaria(angulo, vetor):

    anguloRadiano = np.radians(angulo)
    norma   = np.sqrt((vetor[0]**2 + vetor[1]**2 + vetor[2]**2))
    vetorNormalizado = vetor/norma

    w   = np.cos(anguloRadiano)
    x   = np.sin(anguloRadiano) * vetorNormalizado[0]
    y   = np.sin(anguloRadiano) * vetorNormalizado[1]
    z   = np.sin(anguloRadiano) * vetorNormalizado[2]
    q = np.array([w, x, y, z])
    
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

while aberto:

    tela.fill((30, 30, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            aberto = False

    anguloRotacao += 1
    if anguloRotacao >= 360:
        anguloRotacao = 0

    matrizRotacao = GerarRotacaoQuaternaria(anguloRotacao, vetorDiretor)
    matrizTransformacao = matrizRotacao @ matrizTranslacao @ matrizPerspectiva
    matrizProjetada = novaMatriz @ matrizTransformacao

    Z = matrizProjetada[:, 3]
    xFinal = matrizProjetada[:, 0] / Z
    yFinal = matrizProjetada[:, 1] / Z

    for i in range(len(matrizProjetada)):
        pixelX = int(xFinal[i] * escala + centroX)
        pixelY = int(-yFinal[i] * escala + centroY)

        tela.set_at((pixelX, pixelY), (255, 255, 255))

    pygame.display.flip()
    relogio.tick(30)