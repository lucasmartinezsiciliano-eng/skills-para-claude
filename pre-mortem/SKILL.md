---
name: pre-mortem
description: "Úsala antes de lanzar, invertir o decidir algo caro, o si piden «pre-mortem» o «qué puede salir mal»: 5 agentes imaginan que fracasó y dan las 5 causas, cada una con una prueba barata."
---

# Pre-mortem: la autopsia antes de que pase

**Por qué funciona:** imaginar que algo *ya ha pasado* hace que la gente encuentre en torno a un 30 % más de causas que si solo se pregunta qué podría pasar (Mitchell, Russo y Pennington, 1989; el estudio contó cuántas causas salían, no si eran mejores). Gary Klein lo convirtió en este método en «Performing a Project Premortem», Harvard Business Review, sept. 2007. Que cada agente escriba solo y sin ver a los demás evita que todos repitan la primera idea.

El objetivo no es desanimar: es que salga bien. Cada causa sale con su prueba.

## 0. El plan en cinco líneas (sin esto no se empieza)
Sácalas de lo que te den: documentos, mensajes o la conversación. Si falta una, **pregunta en vez de suponer**:
1. Qué se va a hacer, en una frase.
2. Para quién (quién paga y quién lo usa).
3. Cuándo empieza y cuánto cuesta (dinero y horas).
4. **Qué es «salir bien»**: un número y una fecha (p. ej. «40 ventas antes del 30-jun»). Es lo único que no se salta: sin esto no se puede decir que ha fracasado.
5. Lo que ya se sabe que preocupa (para no gastar un agente en repetirlo).

Enséñale las cinco líneas al usuario y sigue sin esperar, salvo que falte la 4.

**Si no merece la pena:** si la decisión es pequeña y se deshace en un minuto, dilo y da solo tres riesgos en tres líneas.

## 1. La fecha de la autopsia
Fecha de hoy + 6 meses (o el plazo que diga el usuario). Frase para todos: «Es el [fecha]. El plan ha fracasado: no llegó a [la línea 4]. Escribe por qué pasó».

## 2. Cinco agentes, cinco lados, en paralelo
Lánzalos en el mismo mensaje y que ninguno vea a los demás. Cada uno recibe las cinco líneas, la frase de la autopsia y **solo su lado**:

| Lado | Cuenta el fracaso desde… |
|---|---|
| El cliente | por qué no compró, no volvió o no lo recomendó |
| La caja | costes que se dispararon, cobros que no llegaron, un precio que no daba margen |
| La ley y Hacienda | una norma, un permiso, el RGPD, un impuesto o un contrato que lo frenó |
| La competencia y el mercado | alguien lo hizo mejor o más barato, o cambió la plataforma de la que dependía |
| Tú y tu equipo | cansancio, falta de horas, todo dependía de una persona, se dejó a medias |

Si el plan es de código, los lados son otros: el usuario, los datos (pérdida o migración), la seguridad, el coste y el rendimiento, y quien lo mantiene.

Cada agente devuelve **como mucho 3 causas**, y cada una con:
- **La historia**, en 2-3 frases y en pasado, con algo concreto del plan: un número, una persona, una fecha o un documento. Prohibido lo genérico («faltó marketing», «hubo problemas»).
- **La señal temprana**: qué se habría visto y en qué semana.
- **Probabilidad e impacto** (alta, media o baja), con el porqué.
- **La prueba barata**: algo que se pueda hacer esta semana, en un día como mucho y casi sin dinero, que diga si esta causa es real.
- **De dónde saca cada dato** (ver abajo).

Sin subagentes (p. ej. en Claude.ai): escribe las cinco autopsias de una en una, sin releer las anteriores, y no resumas nada hasta tener las cinco.

## 3. El juez
Eso lo haces tú, al final:
- Junta las causas repetidas. Si dos lados llegan a la misma causa por caminos distintos, súbela.
- Ordénalas por probabilidad × impacto y quédate con 5.
- Aparte, guarda la que sería **fatal aunque sea poco probable**.
- Pon cada prueba en el orden en que conviene hacerlas: primero la más barata que más causas descarta.

## 4. El informe
1. **Una frase:** «Si esto fracasa, lo más probable es que sea por…».
2. **Tabla de 5:** causa · señal temprana · prueba de esta semana · lo que cuesta · qué hacer según salga («si pasa A, sigue; si pasa B, cambia esto»).
3. **La fatal aunque improbable**, en dos líneas, con lo que la frenaría.
4. **Lo que no se ha podido comprobar**: datos sin fuente y lo que habría que preguntar a alguien.
5. **Una pregunta:** «¿Te apunto las pruebas como tareas con fecha?».

Frases cortas y en el idioma del usuario. Nada de párrafos largos.

## De dónde sale cada dato (no se inventa ninguno)
- **Lo que dice el plan:** se cita tal cual y se marca «según el plan».
- **Datos de fuera** (una comisión, una ley, un precio, un plazo): se buscan y se citan con su enlace y su fecha. Si un agente no puede comprobarlo, lo marca «sin comprobar» y va al punto 4 del informe.
- **Estimaciones del agente:** se marcan «supuesto» y se dice de qué salen.

## Lo que no se salta
- **La línea 4 (qué es salir bien).** Sin ella, se pregunta y no se lanza nada.
- **Que los agentes no se vean entre ellos.** Se lanzan todos en el mismo mensaje.
- **Ningún número sin su origen.**

No hace falta un candado (un hook): la skill solo lee y escribe un informe, no hace nada que no se pueda deshacer. Si se usa antes de algo irreversible (pagar, firmar, publicar o desplegar), lo correcto es que esa acción tenga su propio candado.

## Ejemplo de una causa bien escrita
Plan: curso online de 197 €, 40 ventas antes del 30-jun, captación con anuncios en Instagram.
> **La caja.** En abril el coste por venta de los anuncios iba por 92 €; quitando también la comisión de la pasarela, cada venta dejaba unos 99 € y el presupuesto de 1.500 € se acabó en la venta 16 (supuesto: 2 % de conversión de la página). **Señal:** la primera semana de anuncios ya pasaba de 60 € por venta. **Prueba de esta semana:** 100 € de anuncios a la página con un botón de «reservar plaza» sin cobrar; si salen menos de 3 reservas, el precio o el anuncio no funcionan. **Si salen 3 o más, sigue; si no, prueba el anuncio con otra promesa antes de grabar el curso.**
