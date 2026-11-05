---
name: ficha-inmueble
description: Úsala cuando den la dirección o la referencia catastral de un piso, casa, local o edificio en España: saca de los registros públicos todo lo que se sabe de él, con la fuente de cada dato.
---

# Ficha del inmueble: lo que dicen los registros públicos

Le dan a Claude una dirección y devuelve una ficha con todo lo que los registros oficiales y gratuitos dicen de ese inmueble. Cada dato lleva su fuente y la fecha de consulta.

El trabajo pesado lo hace `scripts/ficha.py`: consulta los registros en vivo y devuelve un JSON. Tú lo ejecutas, lo lees y escribes la ficha para una persona.

## 0. Los datos mínimos
Hace falta **una** de estas dos cosas:
- **La dirección:** municipio, calle y número. Si es un piso, también la planta y la puerta. Y la provincia, salvo que el municipio sea la capital: el script la necesita para encontrar el municipio. Si no la dicen y la sabes sin dudar (Reus → Tarragona), ponla tú; si no, pregunta.
- **La referencia catastral:** 14 caracteres es el edificio entero; 20 es un inmueble concreto.

Si solo te dan un barrio, una zona o un enlace de un portal de anuncios sin dirección, **pregunta la dirección**. No la adivines por la foto ni por el texto del anuncio.

## 1. Ejecutar el script
La ruta es relativa a la carpeta de esta skill. Python 3.8 o más; no hay que instalar nada.

```bash
python scripts/ficha.py --municipio "Tarragona" --calle "Plaça de la Font" --numero 1
python scripts/ficha.py --municipio "Madrid" --calle "Calle de Alcalá" --numero 20 --planta 3 --puerta B
python scripts/ficha.py --rc 3534212CF5533D
```

- La calle se escribe como la diga la persona, con «calle», «avenida», «carrer», «plaça»… delante. Si sabes el tipo de vía del Catastro, puedes pasarlo con `--sigla` (CL, AV, PZ, PS, RB…).
- Bajo, entresuelo y principal: pasa lo que diga la persona («bajo», «0», «BJ»); el script lo normaliza.

## 2. Si el script devuelve `error`
No rellenes el hueco de memoria. Según lo que traiga:

| Lo que trae | Qué haces |
|---|---|
| «no sé de qué provincia es» | Vuelve a ejecutar con `--provincia`. Si no la sabes seguro, pregunta. |
| `candidatos` | Enseña la lista y pregunta cuál es. Luego vuelve a ejecutar con el nombre exacto. |
| `numeros_cercanos` | Ese número no existe en el Catastro. Dilo y ofrece los números de al lado. Si es una esquina, puede estar con el número de la otra calle. |
| «País Vasco y Navarra…» | Tienen catastro propio (foral). Dile que lo consulte en el de su territorio: Álava, Bizkaia, Gipuzkoa o Navarra. |
| `sin conexión` | En claude.ai, la persona tiene que activar «Allow network egress» en *Settings → Capabilities*. En planes Team o Enterprise lo decide el administrador, que tiene que permitir `ovc.catastro.meh.es` y `analisi.transparenciacatalunya.cat`. Después, conversación nueva. Si no puede, dale el enlace de la Sede Electrónica del Catastro (www.sedecatastro.gob.es) para que lo mire a mano. **No te inventes la ficha.** |

## 3. Si en el portal hay varios inmuebles y no han dicho cuál
El script devuelve el edificio con la lista de inmuebles, pero `inmueble_pedido` vacío. Da los datos del edificio y pregunta la planta y la puerta, enseñando la lista en corto (cuántos hay de cada uso y qué plantas existen). Si hay avisos de escaleras, pregunta también la escalera o pide la referencia de 20.

## 4. La ficha
Escríbela en este orden. Frases cortas, sin jerga; si usas una palabra técnica, explícala en la misma línea.

1. **En una frase.** Qué es y lo más importante: «Piso de 95 m² construidos en un edificio de 1975 con 24 inmuebles; certificado energético E, vigente hasta 2031».
2. **El edificio.** Dirección como la escribe el Catastro, código postal, año de construcción, cuántos inmuebles y de qué usos, suelo de la parcela, y los enlaces: mapa del Catastro, foto de fachada, Google Maps y Street View.
3. **El inmueble.** Referencia de 20, planta y puerta, uso, m² construidos, el desglose (vivienda, trastero, garaje, parte de zonas comunes…), el porcentaje de participación y el año. Si el uso sale como un código (por ejemplo «RDL 1/2004 8.2a»), no lo traduzcas de memoria: di lo que pone el desglose («OFICINA», «VIVIENDA»…).
4. **Las superficies, explicadas.** Casi nunca coinciden, y es normal:
   - **Construida con comunes** (la del Catastro, `m2_construidos`): incluye su parte de escalera, portal y demás zonas comunes. Es la más grande, y la que más se ve en los anuncios.
   - **Construida privada:** la línea «VIVIENDA» del desglose, sin comunes.
   - **Útil:** la que se pisa por dentro, sin paredes. En Cataluña sale de la cédula (`superficie_util_m2`).
   - **Registral:** la de la escritura y la nota simple. No está en estos registros.
   Si un anuncio da más metros que la construida con comunes, señálalo.
5. **Solo en Cataluña: certificado energético.**
   - La letra de consumo y la de emisiones (A es la mejor y G la peor), el consumo en kWh/m² al año, la fecha de registro y si sigue vigente. Dura 10 años; con letra G, 5 (Real Decreto 390/2021). La caducidad que da el script es aproximada: se cuenta desde el registro, no desde la firma.
   - El motivo. «Compraventa» quiere decir que se hizo para venderlo: **estuvo a la venta**, no que se vendiera. «Alquiler», igual.
   - La fachada y las ventanas frente al límite de la norma actual de obra nueva (CTE). Ejemplo: «La fachada pierde calor 2,24; la norma pide como mucho 0,56: aísla unas 4 veces peor que un edificio nuevo». Cuanto más bajo, mejor.
   - El edificio: cuántos certificados hay y de qué letras, y cuántos se hicieron cada año para vender o alquilar (`certificados_para_vender_o_alquilar_por_anyo`). Es **un mínimo** de movimiento en el edificio: un certificado vale 10 años y sirve para varias ventas.
6. **Solo en Cataluña: cédula de habitabilidad.** Si está vigente y hasta cuándo, la superficie útil y la ocupación máxima (cuántas personas pueden vivir ahí). En Cataluña hace falta para alquilar y para dar de alta el agua y la luz.
7. **Avisos.** Copia los del script con tus palabras (por ejemplo, «la calle se ha entendido como…»).
8. **Lo que esta ficha no puede saber,** y dónde se consigue:
   - **Quién es el dueño y si tiene deudas o hipoteca:** nota simple del Registro de la Propiedad (de pago, en registradores.org). Los metros de la escritura también salen ahí.
   - **El valor catastral:** es un dato protegido; solo lo ve el titular o quien él autorice.
   - **La inspección técnica del edificio, la licencia y el urbanismo:** el ayuntamiento.
   - **Fuera de Cataluña, el certificado energético y la cédula:** cada comunidad tiene su registro, casi nunca abierto. Hay que pedírselos al propietario.
   - **El precio:** no sale en ningún registro público. Mira el paso 5.
9. **Fuentes.** Las de `fuentes` del JSON y la fecha de `consultado`.

## 5. El precio (solo si lo piden)
Si piden precio o valor, busca en internet y separa dos cosas:
- **Precio de oferta:** lo que piden los anuncios (idealista, fotocasa…). Siempre sale más alto que lo que se paga.
- **Precio de venta:** lo que se ha pagado de verdad (estadísticas del Notariado, de los Registradores o del INE).

Cada cifra lleva su fuente, su fecha y la zona exacta a la que se refiere (provincia, ciudad o barrio). Multiplica el €/m² por los metros que toquen y da **un rango, nunca una cifra única**. Dilo claro: es una referencia, no una tasación.

## Lo que no se salta
- **Nada de propietarios ni de datos personales.** No busques quién vive ahí ni quién es el dueño, ni en internet. Si lo piden, la vía legal es la nota simple.
- **«No consta» no es «no existe».** Si un registro no trae el piso, di que no aparece en ese registro, no que no tenga certificado o cédula.
- **Ningún dato sin fuente.** Lo que sale del script lleva su registro y su fecha. Lo que busques tú, su enlace y su fecha. Si algo es una suposición, dilo.
- **El script manda.** Si un dato de un anuncio choca con el del Catastro, enseña los dos y di de dónde sale cada uno.
