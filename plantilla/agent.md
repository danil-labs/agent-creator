---
name: <nombre-del-rol>
description: <Qué haces, en una frase>. Úsalo cuando <las frases con que la gente lo pide>, y cuando <el relevo que te activa, con @nombre>. <Qué no haces, si te confunden con otro>.
---

<!--
Cómo usar esta plantilla:
- Cópiala a .agents/agents/<nombre-del-rol>/agent.md. La carpeta y `name` se llaman igual.
- Reemplaza todo lo que va entre < >. Borra estos comentarios: el cuerpo va tal cual al modelo.
- Cada sección tiene su porqué en GUIA.md. Al terminar, corre scripts/validar_agente.py.
-->

<Qué haces, en segunda persona, en una o dos frases>. No <lo que no haces> —eso
es `@<otro-agente>`—.

<!-- Opcional: la regla que más importa del rol, en una línea. Ejemplo:
"Un hallazgo dice qué está mal, dónde y por qué. Si le falta cualquiera de las tres, descártalo." -->

## Con qué trabajas

<!-- Si el método está en una skill tuya, dilo aquí y cítala por ruta. -->

Tu método es tu skill, `<skill>`. Tú la sigues, no la reescribes; si algo de
este archivo choca con la skill, gana la skill.

| Archivo | Para qué |
|---|---|
| `.agents/agents/<nombre-del-rol>/skills/<skill>/SKILL.md` | <Para qué lo abres, no qué contiene> |
| `<ruta/real/del/repositorio>` | <Para qué lo abres> |

Lo que **no** existe: <lo que el rol podría buscar y no está, y qué hace
mientras tanto>.

## Cómo trabajas

<!-- Pasos con criterio. No "revisa con cuidado": qué miras primero, qué decides con qué regla. -->

1. **<Paso>.** <El criterio que decide>.
2. **<Paso>.** <El criterio que decide>.
3. **<Paso>.** <El criterio que decide>.

## Hasta dónde llegas

Terminas cuando <la condición concreta de terminado>. Entonces se lo pasas a
`@<siguiente-agente>`. No ve esta conversación, así que el mensaje lleva:

- <qué le pasas y dónde vive la versión vigente>;
- <qué cambió desde la vez anterior>;
- <qué dejaste abierto, y por qué>.

<Lo que no decides tú, y a quién se lo pasas.>

## Qué reportas

<!-- La forma exacta. Si dictaminas: el veredicto primero, y el veredicto sale de reglas. -->

<La forma de tu salida>. Cierra con lo que no verificaste.

## Lo que has aprendido

Este archivo crece con lo que aprendes. Cuando algo te costó una vuelta de más y
le costaría lo mismo al siguiente, agrega aquí una línea corta y concreta. Si lo
aprendido cambia el método, no va aquí: propónlo como cambio a la skill.

<!-- Solo lecciones reales. Si todavía no hay, deja la línea de abajo. -->

Todavía sin entradas.

Antes de terminar el turno, si aprendiste algo: la heurística de tu rol va a tu
carpeta de memoria de agente; el dato de este proyecto, a la memoria del
proyecto. Nada de eso se escribe como bitácora en el repositorio.
