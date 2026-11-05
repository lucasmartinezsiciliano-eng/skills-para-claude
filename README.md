# Skills para Claude

Recetas que le enseñan a Claude a hacer un trabajo siempre igual de bien.
Las hice en el curso **PotenzIA** (noviembre de 2026). Úsalas, cópialas y cámbialas a tu gusto.

| Skill | Para qué sirve | Descargar |
|---|---|---|
| [**pre-mortem**](pre-mortem/) | Antes de gastar dinero en algo, Claude imagina que ya ha fracasado. Te da las 5 causas más probables y, para cada una, una prueba barata para esta semana. | [pre-mortem.zip](https://github.com/lucasmartinezsiciliano-eng/skills-para-claude/releases/latest/download/pre-mortem.zip) |
| [**ficha-inmueble**](ficha-inmueble/) | Le das una dirección de España y te saca todo lo que dicen el Catastro y los registros públicos de ese piso, casa o local: metros, año, plantas, parcela, fachada y, en Cataluña, certificado energético y cédula. Gratis. | [ficha-inmueble.zip](https://github.com/lucasmartinezsiciliano-eng/skills-para-claude/releases/latest/download/ficha-inmueble.zip) |

## Qué es una skill
Es una carpeta con un fichero `SKILL.md` dentro.
- Arriba lleva una **descripción corta**. Claude la lee y decide solo cuándo usarla.
- Debajo va **la receta**: los pasos, lo que no se salta y de dónde salen los datos.

No tienes que acordarte de llamarla: si lo que pides encaja con la descripción, se activa sola.

## Cómo instalarla

### En claude.ai (web, escritorio o móvil)
Sirve también en el plan gratuito. Los menús salen en inglés.
1. **Settings → Capabilities** → activa «Code execution and file creation». Sin esto, las skills no funcionan.
2. Descarga el zip de la tabla de arriba. **No lo descomprimas.**
3. **Customize → Skills** → «+» → «Create skill» → «Upload a skill» → sube el zip.

**ficha-inmueble** necesita además internet: en **Settings → Capabilities** activa «Allow network egress». En los planes Team y Enterprise lo decide el administrador ([detalles](ficha-inmueble/README.md#cómo-instalarla)).

### En Claude Code
Copia la carpeta entera de la skill dentro de `.claude/skills` de tu usuario:
- Windows: `C:\Users\<tu usuario>\.claude\skills\pre-mortem\SKILL.md`
- Mac o Linux: `~/.claude/skills/pre-mortem/SKILL.md`

Con git:
```bash
git clone https://github.com/lucasmartinezsiciliano-eng/skills-para-claude.git
cp -r skills-para-claude/pre-mortem ~/.claude/skills/
cp -r skills-para-claude/ficha-inmueble ~/.claude/skills/
```
ficha-inmueble lleva dentro la carpeta `scripts` y necesita Python 3.8 o más.
Abre una conversación nueva y ya está.

## Antes de instalar una skill de otro
Consejo del profesor: pásasela a Claude con **«revisa la seguridad de esta skill»** antes de instalarla.

Lo que hace cada una de este repositorio:
- **pre-mortem:** solo lee, busca en internet para comprobar datos y escribe un informe. No ejecuta programas.
- **ficha-inmueble:** ejecuta un programa corto ([scripts/ficha.py](ficha-inmueble/scripts/ficha.py)) que solo lee registros públicos y gratuitos: el Catastro y los datos abiertos de la Generalitat. Solo les manda la dirección que buscas.

Ninguna pide claves, guarda tus datos ni los envía a ningún otro sitio.

## Licencia
MIT: puedes usarlas, cambiarlas y compartirlas. Ver [LICENSE](LICENSE).
