import random
from .settings import RECIPES
class Customer:
 def __init__(self,count=0):
  self.name=random.choice(['Emma','Leo','Mia','Noah','Amina','Alex','Sofia','Daniel']);self.face=random.choice(['👩','👨','🧑','👵','👨‍🎨']);self.recipe_name=random.choice(list(RECIPES));self.recipe=RECIPES[self.recipe_name][:];self.max_patience=random.uniform(28,38);self.patience=self.max_patience;self.mystery=count>0 and count%7==0
 def update(self,dt):self.patience=max(0,self.patience-dt)
