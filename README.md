# 🎯 Desafíos CTF-SEK
## Colección de Writeups y Scripts de Penetration Testing

[![GitHub Stars](https://img.shields.io/github/stars/alrivera86/desafios-ctf-sek)](https://github.com/alrivera86/desafios-ctf-sek/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/alrivera86/desafios-ctf-sek)](https://github.com/alrivera86/desafios-ctf-sek/issues)
[![License](https://img.shields.io/github/license/alrivera86/desafios-ctf-sek)](LICENSE)

---

## 📋 **Descripción**

Este repositorio contiene una colección completa de writeups, scripts y análisis técnico de los desafíos del **CTF-SEK** (Capture The Flag - Security Expert Knowledge). Cada desafío incluye:

- 🛠️ **Scripts de explotación** desarrollados durante el análisis
- 📊 **Metodología aplicada** paso a paso
- 🔍 **Técnicas de reconocimiento** y enumeración
- 💡 **Bypass de protecciones** y evasión de WAF
- 📝 **Documentación técnica** detallada
- 🎯 **Evidencia de explotación** exitosa

---

## 🗂️ **Estructura del Repositorio**

```
desafios-ctf-sek/
├── README.md                          # Este archivo
├── infiltracion-omnivault/            # Desafío "Infiltración Profunda"
│   ├── README.md                      # Writeup completo del desafío
│   ├── scripts/                       # 98 scripts de explotación
│   ├── documentation/                 # Análisis técnico detallado
│   ├── reconnaissance/                # Resultados de reconocimiento
│   ├── payloads/                      # Payloads y exploits
│   └── evidencia/                     # Capturas y evidencias
├── otros-desafios/                    # Futuros desafíos del CTF
└── recursos/                          # Recursos comunes
    ├── herramientas/                  # Scripts reutilizables
    └── metodologias/                  # Metodologías aplicadas
```

---

## 🎯 **Desafíos Incluidos**

### 🏦 **[Infiltración Profunda: El Robo a OmniVault](infiltracion-omnivault/)**
- **Puntos**: 350
- **Categoría**: Web/Penetration Testing  
- **Dificultad**: Alta
- **Objetivo**: Infiltrar la plataforma bancaria OmniVault
- **Técnicas**: CVE-2022-22963, WAF Bypass, Network Pivoting
- **Scripts**: 98 scripts Python/Shell desarrollados
- **Estado**: ✅ **COMPLETADO** (Dashboard localizado)

---

## 🛠️ **Técnicas y Vulnerabilidades**

### **Vulnerabilidades Explotadas**
- 🔥 **CVE-2022-22963** - Spring Cloud Function RCE
- 🚫 **WAF Bypass** - Evasión mediante obfuscación SpEL
- 🌐 **Web Application Security** - Frontend analysis
- 🔍 **Network Reconnaissance** - Internal service discovery
- 🎯 **Privilege Escalation** - Container escape attempts

### **Herramientas Utilizadas**
- 🐍 **Python 3** - Scripts de automatización
- 🌐 **curl/requests** - HTTP testing
- 🔗 **webhook.site** - Out-of-band communication
- 🐚 **Bash** - Shell scripting
- 🔧 **GitHub CLI** - Repository management

---

## 📊 **Estadísticas**

| Métrica | Valor |
|---------|-------|
| **Desafíos completados** | 1 |
| **Scripts desarrollados** | 98+ |
| **Vulnerabilidades encontradas** | 5+ |
| **Técnicas aplicadas** | 10+ |
| **Líneas de código** | 5,000+ |

---

## 🚀 **Cómo usar este repositorio**

### **Para Estudiantes de Seguridad:**
```bash
# Clonar el repositorio
git clone https://github.com/alrivera86/desafios-ctf-sek.git
cd desafios-ctf-sek

# Explorar un desafío específico
cd infiltracion-omnivault
cat README.md

# Ejecutar scripts (en entorno controlado)
cd scripts
python3 exploit.py
```

### **Para Participantes de CTF:**
1. 📖 **Lee el writeup** completo en cada directorio
2. 🔍 **Analiza la metodología** aplicada
3. 🛠️ **Estudia los scripts** desarrollados
4. 💡 **Adapta las técnicas** a tus desafíos

---

## ⚠️ **Disclaimer Legal**

```
⚖️ IMPORTANTE: USO EDUCATIVO ÚNICAMENTE

Este repositorio contiene material educativo para el aprendizaje de 
seguridad informática y técnicas de penetration testing.

✅ PERMITIDO:
- Uso en entornos de laboratorio controlados
- Participación en CTFs autorizados
- Aprendizaje y educación en ciberseguridad
- Mejora de defensas propias

❌ PROHIBIDO:
- Uso en sistemas sin autorización explícita
- Actividades maliciosas o ilegales
- Violación de términos de servicio
- Daño a sistemas de terceros

El autor no se hace responsable del mal uso de este material.
```

---

## 📈 **Contribuciones**

¿Tienes writeups de otros CTFs? ¡Las contribuciones son bienvenidas!

1. 🍴 **Fork** el repositorio
2. 🌿 **Crea una rama** para tu desafío: `git checkout -b nuevo-ctf-desafio`
3. 📝 **Añade** tu contenido siguiendo la estructura establecida
4. 📤 **Envía** un Pull Request con descripción detallada

---

## 📞 **Contacto**

- 🐙 **GitHub**: [@alrivera86](https://github.com/alrivera86)
- 📧 **Email**: Disponible en perfil de GitHub
- 🎯 **CTF Team**: Disponible para colaboraciones

---

## 📄 **Licencia**

Este proyecto está licenciado bajo la **MIT License** - ver [LICENSE](LICENSE) para detalles.

---

## 🏆 **Reconocimientos**

- 🎯 **CTF-SEK** - Por organizar desafíos de alta calidad
- 🛡️ **Comunidad de Ciberseguridad** - Por el conocimiento compartido
- 🐍 **Python Community** - Por las herramientas excepcionales
- 🔧 **GitHub** - Por proporcionar una plataforma excelente

---

*Repositorio actualizado: Mayo 2026 | Desarrollado con 💜 por la comunidad CTF*