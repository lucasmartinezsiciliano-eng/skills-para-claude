# Skills para Claude

Recetas que le enseñan a Claude a hacer un trabajo siempre igual de bien.
Las hice en el curso **PotenzIA** (noviembre de 2026). Úsalas, cópialas y cámbialas a tu gusto.

| Skill | Para qué sirve | Descargar |
|---|---|---|
| [**pre-mortem**](pre-mortem/) | Antes de gastar dinero en algo, Claude imagina que ya ha fracasado. Te da las 5 causas más probables y, para cada una, una prueba barata para esta semana. | [pre-mortem.zip](https://github.com/lucasmartinezsiciliano-eng/skills-para-claude/releases/latest/download/pre-mortem.zip) |

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

### En Claude Code
Copia la carpeta de la skill dentro de `.claude/skills` de tu usuario:
- Windows: `C:\Users\<tu usuario>\.claude\skills\pre-mortem\SKILL.md`
- Mac o Linux: `~/.claude/skills/pre-mortem/SKILL.md`

Con git:
```bash
git clone https://github.com/lucasmartinezsiciliano-eng/skills-para-claude.git
cp -r skills-para-claude/pre-mortem ~/.claude/skills/
```
Abre una conversación nueva y ya está.

## Antes de instalar una skill de otro
Consejo del profesor: pásasela a Claude con **«revisa la seguridad de esta skill»** antes de instalarla.

Las de este repositorio solo leen, buscan en internet para comprobar datos y escriben un informe. No ejecutan programas, no piden claves y no envían nada a ningún sitio.

## Licencia
MIT: puedes usarlas, cambiarlas y compartirlas. Ver [LICENSE](LICENSE).
