---
name: crear-agente
description: Guía para crear o corregir un agente declarado en un repositorio (.agents/agents/<nombre>/agent.md), de principio a fin: si debe ser agente o skill, su frontera, el nombre y la descripción, el cuerpo, los relevos con otros agentes, el reporte, lo que aprende, la validación y la prueba con un caso real. Úsala cuando pidan crear, escribir, revisar o arreglar un agente, un subagente o un rol; convertir un prompt que se repite en un agente; o armar un equipo de agentes que no se pisen.
---

# crear-agente

Lleva a un agente desde la idea hasta un `agent.md` validado y probado. El
formato está en `ESPECIFICACION.md` y el porqué de cada regla en `GUIA.md`, en
la raíz de este repositorio. Esta skill dice el orden.

## Entradas

- El trabajo que el agente va a hacer, con un ejemplo real.
- Los agentes que ya existen en el repositorio (`.agents/agents/`): sin ellos no
  se puede trazar la frontera.
- Las skills que ya existen, dentro y fuera de los agentes.

Si falta el ejemplo real, pídelo. Un agente diseñado sin caso real se diseña
para el caso imaginado.

## Pasos

1. **Decide si es un agente.** Con la tabla de `GUIA.md` § 1. Si lo que falta es
   un método, es una skill; si es una regla para todos, es una línea de
   `AGENTS.md`. Dilo y detente si no es un agente.
2. **Traza la frontera.** Escribe primero qué no hace y a quién le toca. Revisa
   los agentes existentes: nadie más debe escribir en lo que este escribe. Si
   choca con otro, propón la frontera y pregunta antes de seguir.
3. **Nombre y descripción.** El nombre es el rol, en `kebab-case` ASCII y en el
   idioma del equipo. La descripción dice qué hace, cuándo usarlo y qué no hace.
4. **El método.** Si ya existe una skill, cítala por ruta. Si no, escríbela aparte
   antes que el agente. Si solo la usa este agente, va en su carpeta `skills/`.
   Antes de mudar una skill existente dentro de un agente, busca quién más la usa.
5. **El cuerpo**, con la plantilla (`plantilla/agent.md`):
   - el papel en una o dos frases, con su negación;
   - «Con qué trabajas», con rutas reales y lo que no existe;
   - «Cómo trabajas», con pasos y criterios;
   - «Hasta dónde llegas», con cada relevo por `@nombre` y lo que lleva el mensaje;
   - «Qué reportas», con la forma exacta, y el veredicto derivado de reglas si
     dictamina;
   - «Lo que has aprendido», con lecciones reales o vacía, y la regla de memoria.
6. **Los otros agentes.** Si el nuevo recibe o entrega trabajo, actualiza el
   `agent.md` del otro lado del relevo, y la tabla de agentes del `AGENTS.md`
   del repositorio.
7. **Valida:**

   ```bash
   python scripts/validar_agente.py --raiz <repositorio>
   ```

   Corrige todo `ERROR`. Cada `AVISO` o se corrige, o se justifica.
8. **Prueba con el caso real.** Revisa tres cosas: si se quedó dentro de su
   frontera, si el relevo llevaba lo necesario y si el reporte tenía la forma
   declarada. Lo que falle va al agente, o a la skill si es del método.

## Salida

- `.agents/agents/<nombre>/agent.md`, validado.
- Las skills nuevas o movidas, si hicieron falta.
- Los `agent.md` del otro lado de cada relevo, actualizados.
- Una línea por decisión de frontera que tomaste, para que la persona la
  confirme.

**Está bien cuando** el validador pasa, el caso real salió dentro de la
frontera y ningún otro agente escribe en lo que este escribe.

## Qué no hacer

- **No escribir un agente para lo que es un método.** Eso es una skill.
- **No copiar el método dentro del agente.** Diverge en la primera edición.
- **No inventar rutas, comandos ni lecciones** para que el archivo se vea
  completo.
- **No agregar campos al frontmatter.** `tools` y `model` atan el agente a un CLI.
- **No dar personalidad ni texto motivacional.** No cambian ninguna decisión.
