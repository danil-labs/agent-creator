# Crear agentes

Cómo declarar agentes en un repositorio para que cualquier persona del equipo,
con el CLI que tenga, obtenga el mismo criterio de trabajo.

Un **agente** es un rol con nombre: quién hace qué trabajo, con qué archivos,
hasta dónde llega y a quién le pasa el resultado. Vive en un archivo versionado
y se revisa por pull request, como el código.

## Agente, skill y AGENTS.md no son lo mismo

| | Qué es | Dónde vive | Ejemplo |
|---|---|---|---|
| **`AGENTS.md`** | Las reglas del repositorio. Valen para todos | La raíz del repositorio | "Nada de datos reales de clientes" |
| **Skill** | Un método: cómo se hace una cosa, paso a paso | `skills/<nombre>/SKILL.md` | Cómo se escribe una historia de usuario |
| **Agente** | Un rol: quién la hace, con qué criterio y a quién entrega | `.agents/agents/<nombre>/agent.md` | El redactor, que escribe historias y se las pasa al revisor |

El agente no repite el método: carga la skill. Si el método cambia, cambia en la
skill y todos los agentes que la usan lo reciben.

## Estructura de este repositorio

```
README.md                      este archivo
ESPECIFICACION.md              el formato: carpeta, frontmatter, nombre, cuerpo, skills propias, memoria
GUIA.md                        cómo diseñar un agente y un equipo de agentes que no se pisen
plantilla/agent.md             la plantilla para empezar
ejemplos/                      un equipo pequeño y completo: productor, revisor y dueño de un artefacto
skills/crear-agente/SKILL.md   la skill que guía la creación de un agente, paso a paso
scripts/validar_agente.py      el validador: formato, nombre, secciones, rutas y relevos
```

## Inicio rápido

1. Lee [`GUIA.md`](GUIA.md) § 1 para decidir si lo que quieres es un agente o
   una skill.
2. Copia [`plantilla/agent.md`](plantilla/agent.md) a
   `.agents/agents/<nombre>/agent.md` en tu repositorio.
3. Llénalo siguiendo [`ESPECIFICACION.md`](ESPECIFICACION.md) y la guía.
4. Valídalo:

   ```bash
   python scripts/validar_agente.py --raiz <tu-repositorio>
   ```

5. Pruébalo con un caso real antes de darlo por bueno (`GUIA.md` § 9).

Si trabajas con un agente de código, dale la skill
[`skills/crear-agente/`](skills/crear-agente/SKILL.md) y pídele el agente: sigue
el mismo camino y corre el validador al final.

## De dónde sale

De un equipo que declaró seis agentes para un proyecto real: un líder de
producto, un redactor y un revisor de historias, un scrum master, un arquitecto
y un líder técnico. Las reglas de aquí salieron de lo que falló en el camino, y
cada una dice por qué existe.

El formato es el que lee Terminus, y es compatible con los subagentes de Claude
Code: Markdown con frontmatter YAML.
