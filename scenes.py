"""Deterministic original landscape illustrations, not destination photographs."""
import random
from pathlib import Path

PALETTES = {
 'forest':('#c8d6b2','#f4d9a0','#9fae73','#64816a','#284a3e','#142e29'),
 'river':('#b9d8cf','#efd5a1','#a6ba91','#70957e','#385f4d','#193b32'),
 'mountain':('#c9ddd6','#e7d6ad','#a7b6a1','#718d83','#425f54','#243f38'),
 'road':('#e4d5b2','#e9b578','#b7b083','#858f6a','#536c4f','#273f32'),
 'departure':('#bdcfd1','#e8bf8d','#a7b5a4','#7f9387','#4f7062','#244b41'),
 'dusk':('#d3bba5','#efb675','#aea285','#8e907b','#576f5e','#2c483c')}

def scene(name):
 rng=random.Random(name)
 sky,sun,far,mid,near,front=PALETTES[name]
 p=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900"><defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="{sky}"/><stop offset="1" stop-color="#f2e8ce"/></linearGradient><linearGradient id="water" x2="0" y2="1"><stop stop-color="#cbded0"/><stop offset="1" stop-color="#6e9c90"/></linearGradient><linearGradient id="mist" x2="0" y2="1"><stop stop-color="#faf0d6" stop-opacity=".35"/><stop offset="1" stop-color="#faf0d6" stop-opacity="0"/></linearGradient></defs><rect width="1600" height="900" fill="url(#sky)"/><circle cx="1160" cy="210" r="92" fill="{sun}" opacity=".8"/>']
 if name=='mountain':
  p+=[f'<path d="M-100 580L260 195 422 361 733 85 1170 470 1400 205 1730 575Z" fill="{far}"/>','<path d="M544 282L733 85 929 259 814 219 761 239 711 178 664 249 616 221Z" fill="#eceddb" opacity=".85"/>']
 else:
  p+=[f'<path d="M-60 453Q167 231 420 360T921 325T1620 346V900H-60Z" fill="{far}"/>']
 p += [f'<path d="M-50 553Q220 347 483 457T1030 418T1690 409V920H-50Z" fill="{mid}"/>',f'<path d="M-40 664Q204 441 520 551T1040 512T1670 559V920H-40Z" fill="{near}"/>']
 # middle-distance conifers, each deterministic and a different silhouette
 for band,count,y0,colour,scale in [(0,50,540,mid,.65),(1,44,640,near,1.0)]:
  for i in range(count):
   x=i*1600/(count-1)+rng.uniform(-18,18);y=y0+rng.uniform(-38,48);h=rng.uniform(70,155)*scale;w=h*.23
   p.append(f'<path d="M{x:.1f} {y-h:.1f}l{-w*.6:.1f} {h*.32:.1f}h{w*.3:.1f}l{-w*.68:.1f} {h*.29:.1f}h{w*.31:.1f}l{-w*.54:.1f} {h*.31:.1f}h{w*2.42:.1f}l{-w*.54:.1f} {-h*.31:.1f}h{w*.31:.1f}l{-w*.68:.1f} {-h*.29:.1f}h{w*.3:.1f}Z" fill="{colour}"/>')
 p.append('<path d="M0 458Q390 577 801 484T1600 450V650Q1030 522 649 598T0 555Z" fill="url(#mist)"/>')
 if name in ['river','departure','dusk']:
  p.append('<path d="M877 525Q1000 622 799 680T958 780Q1099 852 1070 900H516Q831 793 668 743T713 630Q914 563 837 525Z" fill="url(#water)"/>')
  for i in range(12):
   y=655+i*17;x=800+rng.uniform(-100,100)
   p.append(f'<path d="M{x:.1f} {y}h{rng.randrange(35,130)}" stroke="#eee3bf" stroke-opacity=".36" fill="none"/>')
 else:
  p.append('<path d="M872 570Q843 652 755 702T826 792L995 900H585Q517 810 654 745T825 620Z" fill="#d5b982" opacity=".85"/>')
 # canopy and tall foreground pines frame the path
 for side in [0,1]:
  for i in range(11):
   x=rng.uniform(-100,450) if side==0 else rng.uniform(1150,1700);y=rng.uniform(820,1020);h=rng.uniform(220,490);w=h*.23
   colour=rng.choice([front,near,'#3f5840','#596c42','#9d9557'])
   p.append(f'<path d="M{x:.1f} {y:.1f}l3 {-h*.8:.1f}" stroke="{front}" stroke-width="{h/44:.1f}"/>')
   if i%3:
    p.append(f'<path d="M{x:.1f} {y-h:.1f}l{-w*.65:.1f} {h*.31:.1f}h{w*.25:.1f}l{-w*.55:.1f} {h*.3:.1f}h{w*.3:.1f}l{-w*.7:.1f} {h*.3:.1f}q{w*1.35:.1f} {-h*.06:.1f} {w*2.7:.1f} 0l{-w*.7:.1f} {-h*.3:.1f}h{w*.3:.1f}l{-w*.55:.1f} {-h*.3:.1f}h{w*.25:.1f}Z" fill="{colour}"/>')
   else:
    for j in range(7):
     cx=x+rng.uniform(-w,w);cy=y-h*.65+rng.uniform(-h*.22,h*.17)
     p.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{w*.65:.1f}" ry="{h*.15:.1f}" fill="{colour}" opacity=".94"/>')
 p.append(f'<path d="M0 850Q241 794 412 877T825 900T1600 822V900H0Z" fill="{front}"/>')
 # quiet bird shapes, no misleading human infrastructure
 p.append(f'<path d="M943 225q10-10 20 0q10-10 20 0M1000 191q7-7 14 0q7-7 14 0" stroke="{near}" stroke-width="2" fill="none" opacity=".5"/>')
 p.append('</svg>')
 return ''.join(p)

if __name__=='__main__':
 root=Path(__file__).resolve().parent/'assets';root.mkdir(exist_ok=True)
 for name in PALETTES:(root/f'{name}.svg').write_text(scene(name))
