import random,pygame
class P:
 def __init__(self,x,y,c): self.x=x;self.y=y;self.vx=random.uniform(-2.5,2.5);self.vy=random.uniform(-3.5,-.5);self.life=random.randint(25,55);self.c=c;self.s=random.randint(3,7)
 def update(self): self.x+=self.vx;self.y+=self.vy;self.vy+=.08;self.life-=1
 def draw(self,s):
  if self.life>0: pygame.draw.circle(s,self.c,(int(self.x),int(self.y)),self.s)
class ParticleSystem:
 def __init__(self): self.items=[]
 def burst(self,x,y,c,n=18): self.items += [P(x,y,c) for _ in range(n)]
 def update(self):
  for p in self.items:p.update()
  self.items=[p for p in self.items if p.life>0]
 def draw(self,s):
  for p in self.items:p.draw(s)
