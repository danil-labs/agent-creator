# Especificación

El formato de un agente declarado en un repositorio. Lo que aquí dice **debe**
es lo que el validador revisa; lo que dice **conviene** es criterio, y la
[guía](GUIA.md) explica por qué.

## 1. Dónde vive

```
<repositorio>/
  .agents/agents/
    <nombre>/
      agent.md                  el agente: frontmatter + instrucciones
      skills/                   opcional: las skills que solo usa este agente
        <skill>/
          SKILL.md
          references/           lo que la skill abre cuando lo necesita
          templates/            las plantillas que llena
```

- Cada agente **debe** ser una carpeta con su nombre y, dentro, su `agent.md`.
- `.agents/agents/` es la carpeta neutral: no pertenece a ningún CLI. Terminus
  la lee para todos.
- Claude Code lee sus subagentes de `.claude/agents/<nombre>.md`, un archivo por
  agente, con el mismo formato. Si tu equipo también trabaja con Claude Code sin
  Terminus, publica ahí el mismo agente. Si mantienes dos copias, divergen:
  genera una de la otra o apunta una a la otra, nunca las edites por separado.

## 2. El nombre

- **Debe** estar en `kebab-case` ASCII: minúsculas, dígitos y guiones sueltos,
  sin guion al inicio ni al final, sin `--`, de 60 caracteres como máximo.
- **Debe** coincidir con el nombre de su carpeta.
- **Debe** ser único en el repositorio. Ante un nombre repetido, gana la carpeta
  neutral sobre la de un CLI.
- **Conviene** escribirlo en el idioma del equipo. `redactor-de-historias` pasa
  la validación igual que `story-writer`.
- Cambiar el nombre **no** renombra lo que el agente ya firmó: es un agente
  nuevo.

## 3. El frontmatter

```yaml
---
name: revisor-de-historias
description: Revisa historias ya escritas y dictamina si se pueden construir —aprobada, con cambios o rechazada—, con cada hallazgo ubicado y justificado. Úsalo cuando pidan revisar una historia o un paquete, o cuando @redactor-de-historias entrega una. Solo lee.
---
```

| Campo | | Qué decide |
|---|---|---|
| `name` | **debe** | El identificador estable. Es lo que se escribe al delegar (`@nombre`) y lo que queda firmado en lo que el agente produce |
| `description` | **debe** | Cuándo se le encarga algo, y qué no hace. La lee la persona que elige agente y la lee el CLI |
| `tools` | no conviene | Las herramientas permitidas, con los nombres de un CLI concreto. Ata el agente a ese CLI |
| `model` | no conviene | El modelo con que corre. Un id de modelo es de un proveedor, así que también ata el agente a un CLI |

- El frontmatter **debe** tener `name` y `description`. Cualquier otro campo es
  un error de la validación, salvo `tools` y `model`, que la validación acepta
  con advertencia.
- **Ningún campo dice con qué CLI corre.** Un agente que solo sirve con un CLI no
  es un agente del proyecto: es una configuración personal.
- **Nada del frontmatter es un permiso.** Un agente no puede darse lo que la
  tarea donde corre no tenga.

## 4. El cuerpo

El cuerpo son las instrucciones, y va tal cual al modelo. **Debe** existir: sin
cuerpo, un agente es un nombre sin criterio.

**Conviene** que tenga estas partes, en este orden. El validador revisa que
estén los encabezados; los nombres de sección pueden ir en español o en inglés.

| Parte | Encabezado | Qué lleva |
|---|---|---|
| Papel | *(sin encabezado, al inicio)* | Una o dos frases en segunda persona: qué haces y qué **no** haces |
| Con qué trabajas | `## Con qué trabajas` | Los archivos reales por ruta, en una tabla «Archivo · Para qué». Lo que no existe se dice como tal |
| Cómo trabajas | `## Cómo trabajas` (o `Cómo revisas`, `Cómo planeas`…) | Pasos concretos y criterios de decisión |
| Hasta dónde llegas | `## Hasta dónde llegas` | Cuándo terminas, a quién entregas con `@nombre` y qué lleva el mensaje |
| Qué reportas | `## Qué reportas` | La forma exacta de la salida |
| Lo que has aprendido | `## Lo que has aprendido` | Lecciones reales del rol, que crecen con el uso, y la regla de memoria |

- Toda ruta que el cuerpo cite **debe** existir en el repositorio, o decir que
  no existe.
- Todo `@nombre` que el cuerpo mencione **debe** ser un agente declarado.

## 5. Las skills del agente

- Una skill que **solo** usa un agente vive dentro de él, en
  `<nombre>/skills/<skill>/`. Una que usan varios vive fuera, en la carpeta de
  skills del repositorio.
- Cada skill **debe** tener su `SKILL.md` con `name` y `description` en el
  frontmatter, y su `name` **debe** coincidir con su carpeta.
- Terminus anuncia las skills propias de un agente **solo en los turnos que
  corren como ese agente**. Una sesión que no corre como el agente no las ve.
- Por eso el cuerpo **conviene** que cite sus skills por ruta en «Con qué
  trabajas». Así el agente las encuentra aunque el harness no se las anuncie, y
  cualquiera puede leerlas.
- Otro agente puede leer la skill de un agente por ruta, sin copiarla. Es lo
  correcto cuando dos agentes miden con la misma regla, como quien escribe y
  quien revisa.

## 6. Cómo se hablan

- Un agente le escribe a otro con `@nombre`. La respuesta vuelve a donde se le
  llamó.
- **El otro agente no ve la conversación.** El mensaje de un relevo **debe**
  llevar todo lo que el otro necesita: qué, dónde vive y qué se espera.
- Nadie enruta por la `description`. Un agente se nombra; no se adivina.
- No hay orquestador. Quien reparte trabajo es la persona o el agente que
  delega.

## 7. La memoria

Un agente aprende en tres lugares, y cada cosa va a uno solo:

| Lo que aprendió | Dónde va |
|---|---|
| Algo que cambia cómo hace su trabajo **en este repositorio** | Una línea en «Lo que has aprendido», dentro de su `agent.md`, por pull request |
| Una heurística de su rol que sirve en cualquier proyecto | Su carpeta de memoria de agente (en Terminus, `projects/<id>/agents/<nombre>/memory/`) |
| Un dato de este proyecto: una decisión, una convención, dónde vive algo | La memoria del proyecto |
| Algo que cambia el **método** | La skill, no el agente |

Nada de eso se escribe como nota o bitácora en los documentos del repositorio.
El repositorio es la fuente, no un cuaderno.

## 8. Límites conocidos

- **Las instrucciones de un agente entran una vez**, al empezar la tarea. En una
  tarea larga, una compactación del contexto puede hacer que el agente las
  pierda a mitad, y nada lo avisa. Un `agent.md` corto y concreto resiste mejor.
- **`tools` y `model` no se validan.** Cada CLI decide qué hace con un valor que
  no reconoce.
- **Dos tareas del mismo agente no se ven entre sí.** Lo que comparten es la
  memoria, no el estado.
