# Leaderboard icons (512 x 512) for Play Games and Game Center: Daily and Rush.
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from icon_art import *
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
bg = '<rect width="1024" height="1024" fill="url(#water)"/>' + rays(512, 512, 20, .1) + waves()
cal = ('<rect x="212" y="250" width="600" height="560" rx="70" fill="#fff" filter="url(#sh)"/>'
       '<path d="M212,320 Q212,250 282,250 L742,250 Q812,250 812,320 L812,400 L212,400Z" fill="#ff5a5a"/>'
       '<rect x="330" y="200" width="44" height="110" rx="22" fill="#9e1230"/><rect x="650" y="200" width="44" height="110" rx="22" fill="#9e1230"/>')
daily = bg + cal + G(512, 620, 2.2, 0, puffer(True, (0, .3)))
bolt = '<path d="M590,90 L300,560 L480,560 L410,940 L740,420 L550,420 L640,90Z" fill="url(#gold)" stroke="#b07400" stroke-width="16" stroke-linejoin="round" filter="url(#sh)"/>'
rush = bg + bolt + G(330, 760, 2.4, 30, boat())
tmp = root / 'design' / 'out'
render({'board-daily': daily, 'board-rush': rush}, tmp)
out = root / 'store' / 'leaderboards'; out.mkdir(parents=True, exist_ok=True)
for k in ('daily', 'rush'):
    Image.open(tmp / f'board-{k}.png').convert('RGB').resize((512, 512), Image.LANCZOS).save(out / f'{k}-512.png')
print('done')
