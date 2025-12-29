# Nautilus AGE Encryption Extension - Project Memory

> Memorias del proyecto para Claude Code

---

## Informacion del Proyecto

| Campo | Valor |
|-------|-------|
| **Nombre** | nautilus-age-extension |
| **Version Actual** | v1.7.0 |
| **Lenguaje** | Python 3.8+ |
| **Plataforma** | Linux (Debian/Ubuntu con GNOME/Nautilus) |
| **Repositorio** | https://github.com/vdirienzo/nautilus-age-extension.git |

---

## Arquitectura del Proyecto

```
nautilus-age-extension/
├── nautilus-age-extension.py   # Extension principal (~1700 lineas)
├── install.sh                  # Instalador con --with-pkcs11
├── uninstall.sh               # Desinstalador
├── test.sh                    # Suite de tests de verificacion
├── README.md                  # Documentacion completa
└── screenshots/               # Capturas de pantalla
```

### Componentes Principales

1. **AgeEncryptionExtension** - Clase principal que extiende `Nautilus.MenuProvider`
   - Metodos de menu contextual
   - Validacion de paths y rate limiting
   - Funciones de cifrado/descifrado con PTY

2. **Funciones Standalone** - Ejecutadas como subprocesos separados de Nautilus
   - `standalone_encrypt()` - Cifrado de archivos/carpetas
   - `standalone_decrypt()` - Descifrado de archivos .age
   - `standalone_hsm()` - Cifrado con PKCS#11/HSM

3. **Soporte PKCS#11** - Integracion opcional con SafeNet eToken
   - Auto-deteccion de libeToken.so
   - Generacion de passphrase con TRNG hardware

---

## Problemas Resueltos y Soluciones

### 1. Bug de Bash en test.sh (Exit Code 1)

**Problema:** El script test.sh fallaba despues del primer test con `set -e` activo.

**Causa:** En bash, `((PASSED++))` cuando `PASSED=0` retorna exit code 1 (el valor pre-incremento), lo cual con `set -e` mata el script.

**Solucion:** Cambiar todos los incrementos de `((PASSED++))` a `((++PASSED))` (pre-incremento retorna el nuevo valor, que es >= 1).

```bash
# MAL - retorna 0 (exit code 1 en bash)
((PASSED++))

# BIEN - retorna 1 (exit code 0)
((++PASSED))
```

### 2. Bloqueo de Nautilus Durante Cifrado

**Problema:** Nautilus mostraba "aplicacion lenta" durante operaciones de cifrado.

**Causa:** El cifrado bloqueaba el hilo principal de Nautilus (GLib main loop).

**Solucion:** Arquitectura de subprocesos separados:
```python
subprocess.Popen(
    [sys.executable, script_path, '--encrypt', paths_json],
    start_new_session=True,
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
# Retorna INMEDIATAMENTE - Nautilus queda 100% responsivo
```

### 3. Password Input con age

**Problema:** `age -p` requiere TTY interactivo para leer passwords.

**Solucion:** Usar PTY (pseudo-terminal) para simular terminal:
```python
import pty
master_fd, slave_fd = pty.openpty()
process = subprocess.Popen(['age', '-p', ...], stdin=slave_fd, ...)
os.write(master_fd, f"{password}\n".encode())
```

### 4. Zip-Slip en Extraccion de tar.gz

**Problema:** Archivos maliciosos con `../` en paths podrian escapar del directorio.

**Solucion:** Validar contenido del tar antes de extraer:
```python
list_result = subprocess.run(['tar', '-tzf', temp_decrypted], ...)
for member in list_result.stdout.splitlines():
    if member.startswith('/') or '..' in member:
        raise ValueError(f"Suspicious path: {member}")
```

### 5. TOCTOU Race Conditions

**Problema:** Verificar existencia de archivo y luego operar puede fallar si el archivo cambia.

**Solucion:** Usar try/except en lugar de verificar primero:
```python
# MAL - TOCTOU vulnerable
if os.path.exists(file):
    os.remove(file)

# BIEN - atomico
try:
    os.remove(file)
except FileNotFoundError:
    pass
```

### 6. Procesos Zombie

**Problema:** Procesos hijos terminados quedaban como zombies.

**Solucion:** Siempre llamar `wait()` despues de `kill()`:
```python
process.kill()
process.wait()  # Previene zombie
```

---

## Seguridad Implementada

### Auditoria Semgrep (Score: 9.5/10)

| Categoria | Estado |
|-----------|--------|
| Inyeccion de comandos | Protegido (sin shell=True) |
| Path traversal | Validado con `validate_path()` |
| Zip-slip | Validado antes de extraccion |
| TOCTOU | Corregido con try/except |
| Secrets hardcoded | Ninguno encontrado |
| Symlink attacks | Protegido en copytree |

### Rate Limiting
- 3 intentos por archivo
- 30 segundos de lockout
- Ventana de 5 minutos

### Archivos Temporales Seguros
```python
fd, path = tempfile.mkstemp(prefix='age_', suffix='.bin')
os.chmod(path, 0o600)
```

---

## Dependencias

### Requeridas
- `python3-nautilus` - Bindings de Python para Nautilus
- `age` - Herramienta de cifrado
- `zenity` - Dialogos graficos
- `libnotify-bin` - Notificaciones del sistema
- `mat2` - Limpieza de metadatos

### Opcionales (HSM)
- `opensc` - Herramientas PKCS#11 (pkcs11-tool)
- `libeToken.so` - Driver SafeNet eToken

---

## Comandos Utiles

```bash
# Ejecutar tests
./test.sh

# Instalar extension
./install.sh

# Instalar con soporte HSM
./install.sh --with-pkcs11

# Desinstalar
./uninstall.sh

# Reiniciar Nautilus
nautilus -q

# Ver logs de debug (si se habilitan)
tail -f /tmp/age_encrypt_debug.log
```

---

## Notas para Desarrollo Futuro

1. **No usar debug logging en produccion** - El codigo de debug fue removido en v1.7.0. Si se necesita debug, agregarlo temporalmente y remover antes de commit.

2. **Probar en multiples versiones de Nautilus** - El codigo soporta Nautilus 3.0, 4.0 y 4.1.

3. **PTY es critico** - age requiere PTY real para passwords. No usar pipes simples.

4. **Subprocesos separados** - Siempre lanzar operaciones largas como subprocesos con `start_new_session=True`.

5. **Validar paths** - Siempre usar `validate_path()` antes de operaciones de filesystem.

---

## Historial de Versiones

| Version | Fecha | Cambios Principales |
|---------|-------|---------------------|
| v1.7.0 | 2025-12-28 | Soporte HSM/PKCS#11, SafeNet eToken |
| v1.6.0 | 2025-12-28 | Auditoria Semgrep, zip-slip, TOCTOU |
| v1.5.0 | 2025-12-28 | Dialogo unificado de passphrase |
| v1.4.x | 2025-12-28 | Solo passphrases, mat2 auto-install |
| v1.3.0 | 2025-12-28 | Limpieza automatica de metadatos |
| v1.2.0 | 2025-12-28 | Rate limiting, path validation |
| v1.1.0 | 2025-12-28 | Generador de passphrase |
| v1.0.0 | 2025-12-27 | Release inicial |

---

## Contacto

- **Autor:** Homero Thompson del Lago del Terror
- **Repositorio:** https://github.com/vdirienzo/nautilus-age-extension
