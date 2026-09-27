import math,pygame
from .settings import *
class Pizza:
 def __init__(self): self.reset()
 def reset(self): self.ingredients=[];self.cooking=False;self.cook_time=0;self.state='RAW'
 def add(self,n):
  if n not in self.ingredients:self.ingredients.append(n)
 def matches(self,r): return set(self.ingredients)==set(r)
 def start_cooking(self): self.cooking=True;self.cook_time=0;self.state='RAW'
 def update(self,dt):
  if self.cooking:
   self.cook_time+=dt
   self.state='RAW' if self.cook_time<4 else ('PERFECT' if self.cook_time<7 else 'BURNT')
 def draw(self,s,c,r=105):
  pygame.draw.circle(s,(190,145,92),c,r);pygame.draw.circle(s,(245,202,125),c,r-9)
  if 'Sauce' in self.ingredients:pygame.draw.circle(s,(194,58,43),c,r-18)
  if 'Cheese' in self.ingredients:pygame.draw.circle(s,(248,197,61),c,r-27)
  cols={'Pepperoni':(174,60,45),'Mushroom':(145,108,83),'Olive':(55,49,43),'Pepper':(82,158,86),'Onion':(226,180,204),'Basil':(57,139,75)}
  for i,n in enumerate(self.ingredients):
   if n in ('Sauce','Cheese'):continue
   for j in range(4):
    a=(i*1.7+j)*1.1;x=c[0]+math.cos(a)*(r-45);y=c[1]+math.sin(a)*(r-45);pygame.draw.circle(s,cols[n],(int(x),int(y)),12)
