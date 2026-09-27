import pygame
from .settings import *
_cache={}
def font(n):
 if n not in _cache:_cache[n]=pygame.font.SysFont('arial',n,True)
 return _cache[n]
def text(s,t,p,n=24,c=INK,center=False):
 im=font(n).render(str(t),True,c);r=im.get_rect(center=p) if center else im.get_rect(topleft=p);s.blit(im,r);return r
def panel(s,r):pygame.draw.rect(s,PANEL,r,border_radius=24);pygame.draw.rect(s,(231,204,169),r,3,border_radius=24)
def button(s,r,t,m,enabled=True):
 hot=r.collidepoint(m) and enabled;pygame.draw.rect(s,ORANGE if hot else RED,r,border_radius=18);text(s,t,r.center,25,WHITE,True);return hot
