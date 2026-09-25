# Ejemplos

Un equipo pequeño y completo para un proyecto de software: cuatro agentes que se
pasan el trabajo sin pisarse. Cada uno muestra un patrón.

| Agente | El patrón que muestra |
|---|---|
| [`lider-de-producto`](lider-de-producto/agent.md) | **La entrada.** Convierte un tema en un problema con dueño, decide qué no se construye y reparte |
| [`redactor-de-historias`](redactor-de-historias/agent.md) | **El productor.** Trabaja con su propia skill, entrega a revisión y corrige lo que le devuelven |
| [`revisor-de-historias`](revisor-de-historias/agent.md) | **El revisor.** Solo lee, mide con la skill del productor sin copiarla y deriva el veredicto de clases de hallazgo |
| [`arquitecto`](arquitecto/agent.md) | **El dueño único de un artefacto.** Es el único que escribe en la documentación técnica; los demás se lo piden |

## Cómo se pasan el trabajo

```
lider-de-producto ──enunciado──► redactor-de-historias ──historia──► revisor-de-historias
                                          ▲                                  │
                                          └────────── con cambios ───────────┤
                                                                             │ aprobada
                                                                             ▼
                                                                        arquitecto
```

## Qué es ilustrativo y qué no

Las rutas que citan (`docs/arquitectura/…`, las skills de cada agente) son las
de un proyecto hipotético: en tu repositorio van las tuyas, y tienen que
existir. Lo que sí vale tal cual es la forma: la frontera, las tablas de
archivos, los relevos, el reporte y la sección de lo aprendido.

Para validar los ejemplos sin revisar esas rutas:

```bash
python scripts/validar_agente.py --agentes ejemplos --sin-rutas
```

En los ejemplos, «Lo que has aprendido» empieza vacía a propósito: en un agente
real, esa sección arranca con lecciones reales del proyecto o no arranca.
