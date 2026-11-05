# Pre-mortem: la autopsia antes de que pase

> Antes de gastar dinero en algo, le pido a Claude que se imagine que **ya ha fracasado**.
> Cinco agentes escriben la autopsia, cada uno desde un lado y sin verse entre ellos.
> Me devuelve las 5 causas más probables y, para cada una, **una prueba barata para esta semana**.

**Descargar:** [pre-mortem.zip](https://github.com/lucasmartinezsiciliano-eng/skills-para-claude/releases/latest/download/pre-mortem.zip) · **La receta:** [SKILL.md](SKILL.md) · **Instalarla:** [instrucciones](../README.md#cómo-instalarla)

## Cuándo salta sola
Antes de lanzar, invertir o decidir algo caro. También si dices «pre-mortem» o «qué puede salir mal».

| Salta | No salta |
|---|---|
| «Voy a subir mi tarifa de 50 a 70 € en enero. ¿Qué puede salir mal?» | «Escríbeme un correo para un cliente que me pide la factura.» |
| «Quiero gastar 2.000 € en anuncios para el curso. Hazme un pre-mortem.» | «Resúmeme este PDF.» |

Si la decisión es pequeña y se deshace en un minuto, no gasta cinco agentes: te da tres riesgos en tres líneas.

## Cómo trabaja
```
 Tu plan
   │
   ▼
 1. El plan en 5 líneas ── falta «qué es salir bien»? → te lo pregunta
   │
   ▼
 2. La autopsia: «Es el [hoy + 6 meses]. El plan ha fracasado. ¿Por qué?»
   │
   ├──► El cliente ──────────────┐
   ├──► La caja ─────────────────┤
   ├──► La ley y Hacienda ───────┤  5 agentes a la vez,
   ├──► La competencia ──────────┤  sin verse entre ellos
   └──► Tú y tu equipo ──────────┘
   │
   ▼
 3. El juez: junta las repetidas, ordena y se queda con 5
   │
   ▼
 4. El informe: 5 causas + 5 pruebas baratas + la fatal
```

1. **El plan en cinco líneas.** Qué, para quién, cuándo y cuánto, **qué es «salir bien»** (un número y una fecha) y lo que ya te preocupa. Si falta «salir bien», no arranca: te lo pregunta.
2. **La fecha de la autopsia.** Hoy más 6 meses, o el plazo que digas.
3. **Cinco agentes en paralelo.** Cada uno mira un lado y da como mucho 3 causas. Cada causa trae una historia concreta, la señal temprana, la probabilidad, la prueba barata y de dónde sale cada dato.
4. **El juez.** Si dos lados llegan a la misma causa por caminos distintos, la sube.
5. **El informe.** Una frase, la tabla de 5 causas, la fatal aunque sea improbable, lo que no se ha podido comprobar y una pregunta: «¿Te apunto las pruebas como tareas con fecha?».

Si el plan es de código, cambian los lados: el usuario, los datos, la seguridad, el coste y quien lo mantiene.

## Lo que te devuelve
| Causa | Señal temprana | Prueba de esta semana | Lo que cuesta | Qué hacer según salga |
|---|---|---|---|---|
| Lo que lo haría fracasar, con un dato concreto del plan | Qué verías y en qué semana | Algo de un día como mucho y casi gratis | Horas y euros | «Si pasa A, sigue. Si pasa B, cambia esto» |

## Un ejemplo real
La probé con mi plan de vender una marca propia en TikTok Shop España. Fueron 5 agentes, unos 11 minutos y unos 825.000 tokens.

**En una frase:** si fracasa, lo más probable es que sea porque **el precio de España no da**. Allí se paga una media de 16-19 € por unidad y mi filtro pedía 25-40 €. Lo dijeron **tres agentes sin verse**.

Las otras cuatro causas:
- El Año Nuevo chino (6-feb-2027) cierra las fábricas y me come la ventana.
- La sociedad llega tarde, o cuesta dinero cada mes antes de vender nada.
- Las horas de una sola persona no llegan.
- La mejora del producto trae un coste fijo (molde o preparación).

**La fatal aunque improbable:** abrir la tienda con el tipo de vendedor equivocado, porque después no se puede cambiar.

La primera prueba fue la más barata: apuntar el precio de los 10 primeros productos de 10 nichos. Una hora y 0 €. Si fallaba, cambiaban todas las demás.

## Lo que gasta
Cada agente busca en internet para comprobar datos. En mi ejemplo fueron unos 825.000 tokens. **Úsala antes de decisiones que cuestan dinero, no para todo.**

En claude.ai no hay agentes en paralelo: Claude escribe las cinco autopsias una detrás de otra, sin releer las anteriores. Tarda más, pero sale igual.

## Lo que no se salta
- **Qué es «salir bien».** Sin un número y una fecha no se puede decir que ha fracasado.
- **Que los agentes no se vean.** Así no se contagian la primera idea.
- **Ningún número sin su origen.** Cada dato lleva «según el plan», un enlace con su fecha, «supuesto» o «sin comprobar».

## Por qué funciona
- Imaginar que algo **ya ha pasado** hace salir alrededor de un **30 % más de causas**. Es el estudio de Mitchell, Russo y Pennington, «Back to the future: Temporal perspective in the explanation of events» (*Journal of Behavioral Decision Making*, 1989). Ojo: contaron **cuántas** causas salían, no si eran mejores.
- El método es de **Gary Klein**: [«Performing a Project Premortem»](https://hbr.org/2007/09/performing-a-project-premortem), *Harvard Business Review*, septiembre de 2007.

## Cámbiala a tu gusto
Todo está en [SKILL.md](SKILL.md), en castellano:
- **Los lados:** cambia la tabla del paso 2 por los de tu negocio.
- **El plazo:** «hoy + 6 meses» está en el paso 1.
- **Cuándo salta:** la línea `description` de arriba. En claude.ai no puede pasar de 200 caracteres.
