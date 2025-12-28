# 🚀 GUÍA RÁPIDA DE INSTALACIÓN - AGE NAUTILUS

**Versión:** 1.4.1 | **Seguridad:** Rate limiting + Path validation + mat2 auto-install

## ⚡ Instalación en 3 pasos

### 1️⃣ Descarga los archivos
Ya los tienes! Simplemente extrae el ZIP o clona el repo.

### 2️⃣ Ejecuta el instalador
```bash
cd age-nautilus-extension
chmod +x install-age-nautilus.sh
./install-age-nautilus.sh
```

### 3️⃣ ¡Listo!
Abre Nautilus y click derecho en cualquier archivo. Verás las nuevas opciones de encriptación.

---

## 🎯 Uso básico

### Encriptar un archivo
1. Click derecho en el archivo
2. Selecciona "🔒 Encrypt with age"
3. Ingresa contraseña (2 veces) **o usa el generador**
4. Listo! Se crea `archivo.ext.age`

### 🎲 Generar passphrase segura
1. En el diálogo de contraseña, click en **"🎲 Generate Passphrase"**
2. Se genera algo como: `tiger-ocean-mountain-castle`
3. La passphrase se copia automáticamente al clipboard
4. Click OK (no necesitas confirmar si fue generada)

### Desencriptar un archivo
1. Click derecho en `archivo.ext.age`
2. Selecciona "🔓 Decrypt with age"
3. Ingresa contraseña
4. Listo! Se recupera `archivo.ext`

### Encriptar una carpeta completa
1. Click derecho en la carpeta
2. Selecciona "📦 Encrypt folder with age"
3. Ingresa contraseña
4. Listo! Se crea `carpeta.tar.gz.age`

---

## 🛠️ Verificación

Para verificar que todo está instalado correctamente:
```bash
./test-age-nautilus.sh
```

---

## ❓ ¿Problemas?

### La extensión no aparece
```bash
nautilus -q
killall nautilus
nautilus &
```

### Falta alguna dependencia
```bash
sudo apt install python3-nautilus age zenity libnotify-bin mat2
```

---

## 📚 Más información

Lee el **README.md** completo para:
- Todas las características
- Ejemplos avanzados
- Troubleshooting detallado
- Configuración avanzada

---

## 🗑️ Desinstalar

```bash
./uninstall-age-nautilus.sh
```

---

## 🛡️ Seguridad (v1.2.0)

- **Rate limiting**: 3 intentos fallidos = 30s de bloqueo
- **Path validation**: Protección contra ataques de traversal
- **Logging**: Eventos de seguridad registrados
- **Semgrep audit**: 0 vulnerabilidades detectadas

---

**¡Disfruta de la encriptación segura con age! 🔐**

Para cualquier duda, abre un issue en GitHub o revisa la documentación completa.
