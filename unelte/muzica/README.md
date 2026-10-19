# Muzica invitațiilor

Melodiile din `templates/<model>/muzica.mp3` sunt compoziții originale, generate de la zero de `compose.py` cu sintetizatorul din `synth.py`. Nu folosesc sample-uri sau melodii existente, deci nu au drepturi de autor ale altcuiva.

| Model | Piesă | Stil |
|---|---|---|
| Arcada Aurie | Vals în aur | vals elegant, pian și cutie muzicală, Re major |
| Apus Toscan | Seară în Toscana | chitară arpegiată și flaut, 6/8, La major |
| Constelația Lebedei | Lumina stelei | celestă, pian și pad visător, Mi major |
| Micul Astronaut | Cântec de leagăn printre stele | cutie muzicală, sclipiri, Fa major (botez) |

Regenerare: `pip install numpy scipy`, apoi `python3 compose.py` (sau `python3 compose.py arcada`) și conversie în mp3:
`ffmpeg -i arcada-aurie.wav -b:a 128k muzica.mp3`

Pentru o invitație de client se copiază și `muzica.mp3` în folderul ei. Muzica pornește la deschiderea plicului; invitatul o poate opri din butonul rotund din colțul de jos.
