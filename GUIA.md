# Guía para crear agentes

La [especificación](ESPECIFICACION.md) dice qué forma tiene un agente. Esta guía
dice cómo se escribe uno que sirva, y cómo se arma un equipo de agentes que no
se pisen.

## 1. ¿Agente o skill?

Antes de escribir, decide qué hace falta. La mayoría de las veces lo que falta
es una skill.

| Si lo que falta es… | Escribe… |
|---|---|
| Un procedimiento: cómo se hace algo, paso a paso | Una **skill** |
| Una regla que vale para todo el repositorio | Una línea en **`AGENTS.md`** |
| Alguien que haga un trabajo con criterio propio, sepa hasta dónde llega y a quién entrega | Un **agente** |
| Un segundo par de ojos con un criterio distinto al del que produjo | Un **agente** revisor, separado del productor |

La señal de que hace falta un agente es que el trabajo tiene **dueño y
frontera**: alguien lo hace, alguien más lo recibe, y lo que uno hace no lo
debe hacer el otro.

Un agente sin skill suele ser un prompt largo. Un agente que repite su skill
diverge de ella en la primera edición.

## 2. La frontera

Lo primero que se escribe de un agente es lo que **no** hace.

- **Una frase de papel, con su negación.** "Escribes las historias. No
  dictaminas si están listas, no las planeas y no diseñas la solución." La
  negación nombra a quién le toca: `—eso es de @revisor-de-historias—`.
- **Un solo escritor por artefacto.** Si dos agentes pueden escribir en el mismo
  documento, en algún momento lo escriben distinto. Decide quién es el dueño de
  cada cosa (un directorio, un tipo de documento, una tabla) y que los demás se
  lo pidan.
- **El revisor solo lee.** Si el revisor corrige, deja de haber revisión: queda
  un segundo redactor sin criterio propio.
- **Nadie decide lo que no es suyo.** Un agente no aprueba el gate de una
  persona, no decide prioridad si no es el dueño del plan, y no cierra una
  decisión técnica si no es el arquitecto. Lo señala y se lo pasa a quien sí.

## 3. El nombre y la descripción

**El nombre** es el rol, no la persona ni la herramienta: `revisor-de-historias`,
no `revisor-gpt` ni `ana`. Va en `kebab-case` ASCII y en el idioma del equipo.

**La descripción** dice cuándo se le encarga algo. Tiene tres partes:

1. Qué hace, en una frase.
2. Cuándo usarlo: las frases con que la gente lo pide y los relevos que lo
   activan ("…y cuando `@redactor-de-historias` entrega una historia").
3. Qué no hace, si se confunde con otro ("Solo lee.", "No redacta historias.").

```yaml
description: Facilita la entrega por sprints —kick-off, planeación, daily, refinamiento, review y retro— con registro de impedimentos y riesgos. Úsalo cuando pidan planear o cerrar un sprint, preparar una ceremonia o saber si algo está terminado, y cuando @revisor-de-historias aprueba una historia. No redacta ni revisa historias.
```

## 4. El cuerpo, parte por parte

### Con qué trabajas

Una tabla «Archivo · Para qué» con **rutas reales**. Cada fila dice para qué se
abre el archivo, no qué contiene.

```markdown
| Archivo | Para qué |
|---|---|
| `.agents/agents/redactor-de-historias/skills/historias-de-usuario/SKILL.md` | El método. Léelo completo antes de la primera historia de la sesión |
| `architecture/01-decisiones/` | El `estado:` de cada decisión. Una en `BLOQUEADO` deja bloqueadas las historias que dependen de ella |
```

Después, lo que **no** existe, dicho como tal: "No hay un registro de
impedimentos en el repositorio: se acuerda en el kick-off. Mientras tanto, los
entregas en la conversación." Un agente que no sabe que algo falta lo inventa.

Cita tus skills por ruta aunque el harness te las anuncie: así el agente las
encuentra en cualquier CLI.

### Cómo trabajas

Pasos numerados, cada uno con su criterio. Lo que distingue a un buen agente es
el criterio, no la lista:

- Mal: "Revisa la historia con cuidado."
- Bien: "Empieza por el índice del paquete, no por la primera historia. Compara
  el inventario contra las páginas antes de leer el detalle: una historia del
  índice sin página ya es un hallazgo."

Si el método ya está en una skill, no lo copies: di "con tu skill X" y escribe
aquí solo lo que es del rol y no del método.

### Hasta dónde llegas

Cuándo terminas y a quién entregas. Ver § 5.

### Qué reportas

La forma exacta de la salida. Ver § 6.

### Lo que has aprendido

Lo que el rol aprendió con el uso. Ver § 7.

## 5. Los relevos

- **Nombra al siguiente con `@`**, y di qué le pasas en cada caso:

  ```markdown
  - **Con cambios** o **rechazada** → a `@redactor-de-historias`, con los hallazgos tal cual.
  - **Aprobada** → a `@scrum-master`, con la historia, el veredicto y el semáforo.
  ```

- **El mensaje lleva todo.** El otro agente no ve tu conversación. Di qué le
  pasas, dónde vive la versión vigente, qué cambió desde la vez anterior y qué
  dejaste abierto.
- **Los ciclos son entre dos.** Si el revisor devuelve una historia, el ciclo es
  entre el redactor y el revisor. El que planea no se mete: la recibe cuando sale
  aprobada.
- **Nadie se salta un paso.** Si el redactor entregara directo al que planea, la
  revisión existiría en el papel y no en el flujo.
- **Lo que exige una decisión de una persona, se le pregunta a la persona.** Un
  agente no resuelve una duda de negocio "porque la respuesta parece obvia".

## 6. El reporte

- **El veredicto primero.** Quien lee el reporte decide con la primera línea.
- **Que el veredicto salga de reglas, no de una impresión.** Si el agente
  dictamina, define clases de hallazgo y deriva el veredicto de ellas:

  | Veredicto | Cuándo |
  |---|---|
  | rechazada | Hay al menos un hallazgo bloqueante |
  | con cambios | No hay bloqueantes, pero hay al menos una incoherencia o algo sin definir |
  | aprobada | Solo quedan hallazgos menores, que se listan igual |

- **Cada hallazgo dice qué está mal, dónde y por qué.** Un hallazgo sin ubicación
  no se puede corregir; uno sin razón es una opinión. Descártalo.
- **Di lo que no revisaste.** Páginas a las que no llegaste, versiones que no
  confirmaste. Un reporte que calla lo que no vio parece más completo de lo que
  es.
- **No inventes hallazgos para parecer exhaustivo.** Si está bien, dilo en una
  línea.

## 7. Lo que aprende

«Lo que has aprendido» es la sección que hace que un agente mejore con el uso.

- **Empieza con lecciones reales o vacía.** Una lección inventada para que la
  sección no se vea vacía enseña algo falso. Si el proyecto ya tuvo un tropiezo
  que el rol debe evitar, ese es el primer renglón.
- **Una línea por lección, con el porqué.** "Una plantilla llena no es una
  historia suficiente: las de la primera épica tenían todas las secciones y aun
  así no se podían construir."
- **Si la lección cambia el método, va a la skill.** Así la reciben todos los
  agentes que la usan.
- **Cierra con la regla de memoria:** la heurística del rol va a la memoria del
  agente, el dato del proyecto a la memoria del proyecto, y nada de eso se
  escribe como bitácora en el repositorio.

## 8. Un equipo de agentes

Un equipo funciona cuando cada trabajo tiene un dueño y cada relevo tiene un
receptor. Así se ve el equipo de los [ejemplos](ejemplos/):

```
lider-de-producto ──enunciado──► redactor-de-historias ──historia──► revisor-de-historias
                                          ▲                                  │
                                          └────────── con cambios ───────────┤
                                                                             │ aprobada
                                                                             ▼
                                                                        arquitecto

El arquitecto es el único que escribe en la documentación técnica. El redactor y
el revisor le señalan cuando una historia choca con un contrato.
```

Reglas para armarlo:

1. **Una tabla de dueños antes que los agentes.** Qué artefacto es de quién, y
   quién solo lee.
2. **El método compartido se lee por ruta, no se copia.** El revisor revisa con
   la skill del redactor: si el método cambia, cambia para los dos.
3. **Una skill que solo usa un agente vive dentro de él.** Una que usan varios,
   fuera. Antes de mudar una skill adentro, revisa quién más la usa (ver § 11).
4. **Ningún agente repite reglas de otro.** Si dos agentes dicen lo mismo, en la
   primera edición dicen cosas distintas.
5. **El `AGENTS.md` del repositorio lista los agentes en una tabla**, con qué
   hace cada uno y qué skills trae. No describe sus flujos: eso vive en cada
   `agent.md`.

## 9. Probarlo

1. **Corre el validador.** Revisa el frontmatter, el nombre, las secciones, que
   las rutas existan y que cada `@` sea un agente declarado:

   ```bash
   python scripts/validar_agente.py --raiz <tu-repositorio>
   ```

2. **Dale un caso real**, no uno inventado para que salga bien. Para un revisor:
   un paquete que ya revisó una persona, y compara hallazgos.
3. **Mira tres cosas en la respuesta:** si se quedó dentro de su frontera, si el
   relevo llevaba todo lo necesario y si el reporte tenía la forma que dice su
   `agent.md`.
4. **Lo que falló va a «Lo que has aprendido»**, o a la skill si es del método.

## 10. Lo que no va en un agente

- **Texto motivacional o personalidad inventada.** "Eres un experto apasionado…"
  no cambia ninguna decisión.
- **Listas genéricas.** "Sé claro, sé conciso, sé preciso" vale para todo y no
  guía nada.
- **Rutas o comandos que no existen.** El agente los va a buscar.
- **Instrucciones que se contradicen o se pisan con las de otro agente.**
- **Campos de frontmatter de más.** Cada uno ata el agente a un CLI.
- **El método completo.** Va en la skill.
- **Estado del proyecto que envejece:** "hoy hay 36 preguntas abiertas". Mañana
  es falso. Di dónde se consulta.

## 11. Por qué existe cada regla

Estas reglas salieron de lo que falló en un proyecto real.

| Regla | Lo que pasó |
|---|---|
| Revisa quién usa una skill antes de mudarla dentro de un agente | Las skills de especialista pasaron al agente redactor. Una sesión que redactaba historias sin correr como ese agente las perdió a la mitad del trabajo y ofreció seguir "en el rol, sin la skill". Eso es justo lo que el método prohíbe: una validación escrita sin cargar la skill del área sale inventada |
| Cita las skills por ruta | Por lo mismo: con la ruta, cualquier sesión puede abrir la skill, aunque el harness no se la anuncie |
| Las copias viejas siguen enseñando lo que ya se borró | Un checkout en una rama vieja seguía ofreciendo una skill eliminada por obsoleta. La fuente de agentes y skills es la rama vigente |
| Un solo escritor por artefacto | Después de que el cómputo cambió de un modelo a otro, cuatro documentos siguieron suponiendo el anterior, sin ningún aviso. Nadie era dueño de ponerlos al día |
| El revisor usa la skill del productor, sin copia | La revisión de una épica encontró huecos en historias escritas con la skill. Con dos copias del método nadie sabría cuál estaba mal |
| El veredicto sale de clases de hallazgo | Un veredicto por impresión cambia de un revisor a otro con la misma historia |
| El mensaje del relevo lleva todo | El agente que recibe no ve la conversación. Un "revisa la HU-06" sin dónde vive ni qué cambió obliga a preguntar |
| Lecciones reales o nada | Una lección inventada queda escrita como verdad y la siguiente sesión la aplica |
| El repositorio no es bitácora | Los registros de estado, de contradicciones y de aprendizajes envejecieron y se contradijeron con los documentos que resumían |

## Lista de verificación

- [ ] Es un agente, no una skill ni una regla de `AGENTS.md`.
- [ ] El nombre es el rol, en `kebab-case` ASCII, igual que su carpeta.
- [ ] La descripción dice qué hace, cuándo usarlo y qué no hace.
- [ ] El frontmatter tiene solo `name` y `description`.
- [ ] El papel cabe en una o dos frases y dice qué no hace.
- [ ] Cada ruta citada existe, o el texto dice que no existe.
- [ ] El método está en una skill, citada por ruta, y no copiado en el cuerpo.
- [ ] Cada relevo nombra al receptor con `@` y dice qué lleva el mensaje.
- [ ] Ningún otro agente escribe en lo que este escribe.
- [ ] El reporte tiene forma fija, y el veredicto sale de reglas.
- [ ] «Lo que has aprendido» tiene solo lecciones reales, y la regla de memoria.
- [ ] El validador pasa.
- [ ] Se probó con un caso real.
