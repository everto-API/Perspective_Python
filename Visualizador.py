import numpy as np
import pygame
from plyfile import PlyData
pygame.init()

dados = PlyData.read('bun_zipper.ply')


# ==========
# Função para organizar as coordenadas do arquvio .ply
# ==========
def OrganizarDados(arquivo):

    X = arquivo['vertex']['x']
    Y = arquivo['vertex']['y']
    Z = arquivo['vertex']['z']
    v = np.column_stack((X, Y, Z))
    return v
v = OrganizarDados(dados)

# ==========
# Adicionar a quarta coordenada para a matriz para gerar os cálculos da geometria projetiva
# ==========
def QuartaColuna(matriz):

    w = np.ones(35947)
    NovM = np.column_stack((matriz, w))
    return NovM
novaMatriz = QuartaColuna(v)

# ==========
# 1ª Etapa: Matriz de translação
# ==========
def GerarTranslacao():

    Tx, Ty, Tz = 0, -0.11, -1.5
    matTrans = np.identity(4)
    matTrans[3, 0] = Tx
    matTrans[3, 1] = Ty
    matTrans[3, 2] = Tz
    return matTrans
matrizTranslacao = GerarTranslacao()

# ==========
# 2ª Etapa: Matriz de perspectiva
# ==========
def GerarPerspectiva():

    foco = 2
    matriz = np.identity(4)
    matriz[2, 3] = 1 / foco
    return matriz 
matrizPerspectiva = GerarPerspectiva()

# ==========
# 3ª Etapa: Multiplicação entre as matrizes
# ==========
matrizProjecao = matrizTranslacao @ matrizPerspectiva
matrizProjetada = novaMatriz @ matrizProjecao

# ==========
# 4ª Etapa: Normalização da coordenada Z + aplicação da divisão de Z em X e Y
# ==========
print(matrizProjecao)

Z = matrizProjetada[:, 3]
xFinal = matrizProjetada[:, 0] / Z
yFinal = matrizProjetada[:, 1] / Z



# ==========
# Visualizador do coelho doidão
# ==========
largura, altura = 1280, 720
centroX = largura // 2
centroY = altura // 2
escala  = 1000

tela    = pygame.display.set_mode((largura, altura))
relogio = pygame.time.Clock()
aberto  = True

while aberto:

    tela.fill((30, 30, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            aberto = False

    for i in range(len(matrizProjetada)):
        pixelX = int(xFinal[i] * escala + centroX)
        pixelY = int(-yFinal[i] * escala + centroY)

        tela.set_at((pixelX, pixelY), (255, 255, 255))

    pygame.display.flip()


