#!/usr/bin/env python
"""Valida los agentes de un repositorio contra ESPECIFICACION.md.

Uso:
    python scripts/validar_agente.py --raiz <repositorio>      # lee <repositorio>/.agents/agents/
    python scripts/validar_agente.py --agentes <carpeta>       # lee <carpeta>/<nombre>/agent.md
    python scripts/validar_agente.py ... --sin-rutas           # no revisa que existan las rutas citadas

Sale con 1 si hay algún ERROR. Los AVISO no cambian la salida.
Solo usa la librería estándar.
"""
import argparse
import os
import re
import sys

NOMBRE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
MAX_NOMBRE = 60
RESERVADOS = {'con', 'prn', 'aux', 'nul'} | {f'com{i}' for i in range(1, 10)} | {f'lpt{i}' for i in range(1, 10)}
CAMPOS = {'name', 'description'}
CAMPOS_TOLERADOS = {'tools', 'model'}

# Secciones que conviene tener. Cada una acepta varios encabezados, en español o en inglés.
SECCIONES = [
    ('Con qué trabajas', re.compile(r'^(con qu[eé]\b|what you work with|the contracts you check|files)', re.I)),
    ('Cómo trabajas', re.compile(r'^(c[oó]mo (?!reportas)\w+|how you (?!report)\w+|what you look for)', re.I)),
    ('Hasta dónde llegas', re.compile(r'^(hasta d[oó]nde llegas|how far you go|how you hand off)', re.I)),
    ('Qué reportas', re.compile(r'^(qu[eé] reportas|how you report|what you report)', re.I)),
    ('Lo que has aprendido', re.compile(r'^(lo que has aprendido|what you have learned)', re.I)),
]

RUTA = re.compile(r'`([^`\s]+)`')
MENCION = re.compile(r'(?<![\w.@])@([a-z0-9]+(?:-[a-z0-9]+)*)')


def leer(ruta):
    with open(ruta, encoding='utf-8-sig') as f:
        return f.read().replace('\r\n', '\n')


def frontmatter(texto):
    """Devuelve (campos, cuerpo) o (None, texto) si no hay frontmatter."""
    if not texto.startswith('---\n'):
        return None, texto
    fin = texto.find('\n---', 4)
    if fin == -1:
        return None, texto
    bloque, cuerpo = texto[4:fin], texto[fin + 4:].lstrip('\n')
    campos, clave = {}, None
    for linea in bloque.split('\n'):
        m = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', linea)
        if m:
            clave, valor = m.group(1), m.group(2).strip()
            campos[clave] = '' if valor in ('>', '|', '>-', '|-') else valor.strip('"\'')
        elif clave and (linea.startswith(' ') or linea.startswith('\t')):
            campos[clave] = (campos[clave] + ' ' + linea.strip()).strip()
    return campos, cuerpo


def parece_ruta(token):
    token = token.rstrip('.,:;)')
    if not token or token[0] in '@/' or token.startswith(('http', 'www.')):
        return None
    if any(c in token for c in '<>*{}…|') or '/' not in token:
        return None
    if not (token.endswith('/') or re.search(r'\.[A-Za-z0-9]+$', token) or token.startswith('.')):
        return None
    return token


def validar_nombre(nombre, carpeta, errores):
    if not nombre:
        errores.append('ERROR: falta `name` en el frontmatter')
        return
    if not NOMBRE.match(nombre):
        errores.append(f'ERROR: `name: {nombre}` no es kebab-case ASCII (minúsculas, dígitos y guiones sueltos)')
    if len(nombre) > MAX_NOMBRE:
        errores.append(f'ERROR: `name` tiene {len(nombre)} caracteres; el máximo es {MAX_NOMBRE}')
    if nombre in RESERVADOS:
        errores.append(f'ERROR: `{nombre}` es un nombre reservado en Windows')
    if nombre != carpeta:
        errores.append(f'ERROR: `name: {nombre}` no coincide con su carpeta `{carpeta}/`')


def validar_skills(dir_agente, errores):
    dir_skills = os.path.join(dir_agente, 'skills')
    if not os.path.isdir(dir_skills):
        return
    for skill in sorted(os.listdir(dir_skills)):
        dir_skill = os.path.join(dir_skills, skill)
        if not os.path.isdir(dir_skill):
            continue
        archivo = os.path.join(dir_skill, 'SKILL.md')
        if not os.path.isfile(archivo):
            errores.append(f'ERROR: la skill `skills/{skill}/` no tiene SKILL.md')
            continue
        campos, _ = frontmatter(leer(archivo))
        if campos is None:
            errores.append(f'ERROR: `skills/{skill}/SKILL.md` no tiene frontmatter')
            continue
        if campos.get('name') != skill:
            errores.append(f'ERROR: `skills/{skill}/SKILL.md` declara `name: {campos.get("name")}`, distinto de su carpeta')
        if not campos.get('description'):
            errores.append(f'ERROR: `skills/{skill}/SKILL.md` no tiene `description`')


def validar_agente(dir_agente, raiz, declarados, revisar_rutas):
    carpeta = os.path.basename(dir_agente)
    archivo = os.path.join(dir_agente, 'agent.md')
    errores = []
    if not os.path.isfile(archivo):
        return [f'ERROR: `{carpeta}/` no tiene agent.md']
    campos, cuerpo = frontmatter(leer(archivo))
    if campos is None:
        return ['ERROR: agent.md no empieza con frontmatter (---)']

    validar_nombre(campos.get('name', ''), carpeta, errores)
    descripcion = campos.get('description', '')
    if not descripcion:
        errores.append('ERROR: falta `description`: di cuándo se usa el agente y qué no hace')
    elif len(descripcion) > 1024:
        errores.append(f'AVISO: la descripción tiene {len(descripcion)} caracteres; más de 1024 suele ser el método, no el cuándo')
    for campo in campos:
        if campo in CAMPOS_TOLERADOS:
            errores.append(f'AVISO: `{campo}` ata el agente a un CLI; la especificación recomienda omitirlo')
        elif campo not in CAMPOS:
            errores.append(f'ERROR: `{campo}` no es un campo del frontmatter; solo `name` y `description`')

    if not cuerpo.strip():
        errores.append('ERROR: el cuerpo está vacío; sin instrucciones el agente es un nombre sin criterio')
        return errores

    encabezados = [l.lstrip('#').strip() for l in cuerpo.split('\n') if re.match(r'^#{2,3} ', l)]
    for nombre_seccion, patron in SECCIONES:
        if not any(patron.match(e) for e in encabezados):
            errores.append(f'AVISO: no hay sección «{nombre_seccion}»')

    primer = next((l for l in cuerpo.split('\n') if l.strip()), '')
    if primer.startswith('#'):
        errores.append('AVISO: el cuerpo no empieza con el papel: una o dos frases de qué haces y qué no')

    for mencion in sorted(set(MENCION.findall(cuerpo))):
        if mencion not in declarados:
            errores.append(f'ERROR: `@{mencion}` no es un agente declarado')

    if revisar_rutas:
        vistas = set()
        for token in RUTA.findall(cuerpo):
            ruta = parece_ruta(token)
            if not ruta or ruta in vistas:
                continue
            vistas.add(ruta)
            if not (os.path.exists(os.path.join(raiz, ruta)) or os.path.exists(os.path.join(dir_agente, ruta))):
                errores.append(f'ERROR: la ruta `{ruta}` no existe')

    validar_skills(dir_agente, errores)
    return errores


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description='Valida agentes contra ESPECIFICACION.md')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--raiz', help='raíz del repositorio; lee <raiz>/.agents/agents/')
    g.add_argument('--agentes', help='carpeta que contiene <nombre>/agent.md')
    p.add_argument('--sin-rutas', action='store_true', help='no revisa que existan las rutas citadas')
    a = p.parse_args()

    raiz = os.path.abspath(a.raiz or '.')
    dir_agentes = os.path.join(raiz, '.agents', 'agents') if a.raiz else os.path.abspath(a.agentes)
    if not os.path.isdir(dir_agentes):
        print(f'ERROR: no existe {dir_agentes}')
        return 1

    agentes = sorted(d for d in os.listdir(dir_agentes) if os.path.isdir(os.path.join(dir_agentes, d)))
    declarados = set(agentes)
    total_errores = 0
    for nombre in agentes:
        hallazgos = validar_agente(os.path.join(dir_agentes, nombre), raiz, declarados, not a.sin_rutas)
        errores = [h for h in hallazgos if h.startswith('ERROR')]
        total_errores += len(errores)
        print(f'{"OK   " if not errores else "FALLA"} {nombre}')
        for h in hallazgos:
            print(f'      {h}')
    print(f'\n{len(agentes)} agentes, {total_errores} errores')
    return 1 if total_errores else 0


if __name__ == '__main__':
    sys.exit(main())
