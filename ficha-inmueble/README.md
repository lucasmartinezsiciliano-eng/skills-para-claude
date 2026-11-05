# Ficha del inmueble: lo que dicen los registros públicos

> Le das a Claude una dirección de España.
> Te devuelve una ficha con todo lo que dicen el Catastro y los registros públicos de ese piso, casa o local.
> Cada dato lleva su fuente. Es gratis y no pide claves.

**Descargar:** [ficha-inmueble.zip](https://github.com/lucasmartinezsiciliano-eng/skills-para-claude/releases/latest/download/ficha-inmueble.zip) · **La receta:** [SKILL.md](SKILL.md) · **El programa:** [scripts/ficha.py](scripts/ficha.py) · **Instalarla:** [instrucciones](#cómo-instalarla)

## Cuándo salta sola
Cuando le das una dirección o una referencia catastral y quieres saber qué hay ahí.

| Salta | No salta |
|---|---|
| «¿Qué sabes del piso de la calle Mayor 12, 3.º B, de Reus?» | «¿Cuánto me costaría una hipoteca de 200.000 €?» |
| «Hazme la ficha de la referencia catastral 3534212CF5533D.» | «Escríbeme un anuncio para vender mi piso.» |

## Qué saca

| Dato | De dónde sale | Dónde funciona |
|---|---|---|
| Todos los inmuebles del portal: planta, puerta, uso y m² | Catastro | Toda España, salvo País Vasco y Navarra |
| Los m² construidos y su desglose: vivienda, trastero, garaje, parte de zonas comunes | Catastro | Ídem |
| El año de construcción | Catastro | Ídem |
| El porcentaje de participación en la comunidad | Catastro | Ídem |
| El suelo de la parcela y el mapa | Catastro | Ídem |
| La foto de la fachada, las coordenadas, Google Maps y Street View | Catastro | Ídem |
| Certificado energético: letra, consumo, si sigue vigente, para qué se hizo y cuánto aíslan la fachada y las ventanas | Registro de certificados energéticos (ICAEN) | Solo Cataluña |
| Cuántos certificados se hicieron en el edificio para vender o alquilar, año a año | Registro de certificados energéticos (ICAEN) | Solo Cataluña |
| Cédula de habitabilidad: si sigue vigente, superficie útil y cuántas personas pueden vivir ahí | Agència de l'Habitatge de Catalunya | Solo Cataluña |
| El precio de la zona (solo si lo pides) | Búsqueda en internet, con fuente y fecha | Toda España |

**Por qué hay más datos en Cataluña:** la Generalitat publica en abierto el registro de certificados energéticos y el de cédulas. Las demás comunidades, casi nunca.

## Lo que no saca (y dónde se consigue)
| Lo que buscas | Dónde está |
|---|---|
| Quién es el dueño, si hay hipoteca o deudas | Nota simple del Registro de la Propiedad (de pago, en registradores.org) |
| El valor catastral | Es un dato protegido: solo lo ve el titular |
| La inspección técnica del edificio, licencias y urbanismo | El ayuntamiento |
| El certificado energético fuera de Cataluña | Hay que pedírselo al propietario |
| País Vasco y Navarra | Su catastro propio (foral) |

## Un ejemplo: el Ayuntamiento de Tarragona
**Pregunta:** «Hazme la ficha de Plaça de la Font 1, Tarragona.»

**En una frase:** es un edificio de oficinas de la Administración de 7.939 m² construidos, sobre una parcela de 2.505 m², sin dividir en pisos.

| | |
|---|---|
| Dirección en el Catastro | PZ FONT 1, 43003 Tarragona |
| Referencia catastral | 3534212CF5533D0001UG |
| Uso | Oficinas de la Administración pública, según el desglose del Catastro |
| m² construidos | 7.939: planta baja 2.193, primera 2.160, segunda 1.730, tercera 1.052 y 804 en la planta que el Catastro llama «+1» |
| Año de construcción | 1900, según el Catastro (en edificios muy antiguos, esta fecha suele ser aproximada) |
| Suelo de la parcela | 2.505 m² |
| Enlaces | Mapa del Catastro, foto de la fachada y Street View |
| Certificado energético y cédula | No constan en los registros abiertos de Cataluña |

Fuentes: Catastro (servicios libres) y datos abiertos de la Generalitat, consultados el 5-nov-2026.

**Si fuera un piso de Cataluña, la ficha añadiría algo así** (números inventados):
- Certificado energético **E**, registrado en 2021 para venderlo. Vigente hasta 2031, más o menos.
- La fachada pierde calor 2,24; la norma de obra nueva pide 0,56 como mucho. Aísla unas 4 veces peor que un edificio nuevo.
- Cédula de habitabilidad vigente hasta 2038: 75 m² útiles, hasta 4 personas.
- Las superficies explicadas: 95 m² construidos con zonas comunes, 84 m² sin ellas y 75 m² útiles.
- En el edificio se hicieron 2 certificados para vender en 2024 y 1 para alquilar en 2025.

## Cómo trabaja
```
 Dirección o referencia catastral
   │
   ▼
 1. Busca la provincia, el municipio y la calle tal como los escribe el Catastro
   │   ── si hay dudas → te enseña las opciones y te pregunta
   ▼
 2. Catastro: los inmuebles del portal y el que has pedido
   │
   ▼
 3. ¿Está en Cataluña? → certificado energético + cédula de habitabilidad
   │
   ▼
 4. Claude escribe la ficha: dato a dato, con su fuente y su fecha
```

Las consultas las hace el programa [scripts/ficha.py](scripts/ficha.py), no Claude. Así los datos salen siempre del registro y nunca de la memoria de Claude.

## Lo que no se salta
- **Nada de propietarios ni de datos personales.** No busca quién es el dueño ni quién vive ahí. La vía legal es la nota simple.
- **«No consta» no es «no existe».** Si un registro no trae el piso, la ficha dice que no aparece, no que no tenga certificado.
- **Ningún dato sin fuente.** Y el precio siempre como un rango, separando lo que piden los anuncios de lo que se paga de verdad.

## Lo que gasta
**0 €.** Todos los registros son gratuitos y no piden claves. Tarda unos segundos y no usa agentes, así que gasta pocos tokens.

## Cómo instalarla

### En claude.ai (web, escritorio o móvil)
Los menús salen en inglés.
1. **Settings → Capabilities** → activa «Code execution and file creation».
2. En la misma pantalla, activa **«Allow network egress»**. Sin esto, el programa no llega al Catastro.
   En los planes Team y Enterprise lo decide el administrador: tiene que permitir `ovc.catastro.meh.es` y `analisi.transparenciacatalunya.cat`.
3. Descarga [ficha-inmueble.zip](https://github.com/lucasmartinezsiciliano-eng/skills-para-claude/releases/latest/download/ficha-inmueble.zip). **No lo descomprimas.**
4. **Customize → Skills** → «+» → «Create skill» → «Upload a skill» → sube el zip.
5. Abre una conversación nueva.

### En Claude Code
Hace falta Python 3.8 o más (no hay que instalar nada más). Copia la carpeta entera, con `scripts` dentro:
```bash
git clone https://github.com/lucasmartinezsiciliano-eng/skills-para-claude.git
cp -r skills-para-claude/ficha-inmueble ~/.claude/skills/
```
En Windows debe quedar `C:\Users\<tu usuario>\.claude\skills\ficha-inmueble\SKILL.md` y, al lado, la carpeta `scripts`.

## Es segura
- **Solo lee.** Consulta servicios oficiales y gratuitos: el Catastro y los datos abiertos de la Generalitat. Solo les manda la dirección que buscas.
- **No pide claves, no guarda nada y no instala nada.**
- **El programa es corto y está comentado en castellano.** Antes de instalarla, pásasela a Claude con «revisa la seguridad de esta skill».

## Cámbiala a tu gusto
- **El orden y el estilo de la ficha:** el paso 4 de [SKILL.md](SKILL.md).
- **Otro registro:** si tu comunidad publica algo en abierto, añade una función en [scripts/ficha.py](scripts/ficha.py).
- **Cuándo salta:** la línea `description` de arriba de SKILL.md. En claude.ai no puede pasar de 200 caracteres.
