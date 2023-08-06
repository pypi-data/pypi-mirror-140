import numpy as np
import pygame

def distance(A:pygame.sprite.Sprite, B:pygame.sprite.Sprite) -> float:

	a = list(A.rect.center)
	b = list(B.rect.center)

	a = np.array(a)
	b = np.array(b)

	return np.linalg.norm(a-b)