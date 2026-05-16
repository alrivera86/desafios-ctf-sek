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
├── infiltracion-omnivault/            # Desafío "Infiltración Profunda" (350 pts)
│   ├── README.md                      # Writeup completo del desafío
│   ├── scripts/                       # 95+ scripts de explotación
│   ├── documentation/                 # Análisis técnico detallado
│   └── [reconnaissance, payloads, evidencia...]
├── shadow-coordinator-iot/            # Desafío IoT avanzado (55 archivos)
│   ├── README.md                      # IoT exploitation writeup
│   ├── scripts/                       # ZigBee, smart devices, coordinador
│   ├── iot-analysis/                  # Análisis de protocolos IoT
│   ├── network-captures/              # PCAP files para análisis
│   ├── zigbee-data/                   # Datos específicos de ZigBee
│   └── [documentation, evidence...]
├── agroindustrial-exploit/            # Explotación web agroindustrial
│   ├── README.md                      # Business logic exploitation
│   ├── scripts/                       # buy.py - transacciones
│   └── web-assets/                    # app.js, index.html
├── gitops-infiltration/               # Seguridad CI/CD y pipelines
│   ├── README.md                      # DevOps security writeup
│   └── ci-cd-analysis/                # Interfaces de build, jobs
├── enter-the-matrix/                  # Web + Crypto challenge
│   ├── README.md                      # Matrix-themed challenge
│   ├── web-assets/                    # HTML, JS, Matrix effects
│   └── crypto/                        # Hash analysis
├── omnivault-web/                     # Banking frontend simple
│   ├── README.md                      # Basic web security
│   └── web-analysis/                  # HTML interfaces
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
- **Dificultad**: ⚠️ **Alta**
- **Objetivo**: Infiltrar la plataforma bancaria OmniVault
- **Técnicas**: CVE-2022-22963, WAF Bypass, Network Pivoting
- **Scripts**: 95+ scripts Python/Shell desarrollados
- **Estado**: ✅ **COMPLETADO** (Dashboard localizado)

### 🏠 **[Shadow Coordinator - IoT Exploitation](shadow-coordinator-iot/)**
- **Categoría**: IoT/Network Security
- **Dificultad**: 🔥 **Muy Alta**
- **Objetivo**: Infiltración completa de red IoT doméstica
- **Técnicas**: ZigBee exploitation, Smart device buffer overflow, WebSocket attacks
- **Scripts**: 55+ archivos (Scripts, PCAP, análisis ZigBee)
- **Estado**: ✅ **COMPLETADO** (Coordinador comprometido)

### 🌾 **[Agroindustrial Exploit](agroindustrial-exploit/)**
- **Categoría**: Web Application Security
- **Dificultad**: 🟡 **Media**
- **Objetivo**: Manipulación de transacciones agroindustriales
- **Técnicas**: Business logic flaws, Price manipulation
- **Archivos**: 3 (buy.py, app.js, index.html)
- **Estado**: 🔄 **DISPONIBLE** para resolución

### 🔧 **[GitOps Infiltration](gitops-infiltration/)**
- **Categoría**: DevOps/CI-CD Security
- **Dificultad**: 🟡 **Media**
- **Objetivo**: Compromiso de pipelines de construcción
- **Técnicas**: Build injection, Pipeline tampering, Secret extraction
- **Archivos**: 9 interfaces de build y administración
- **Estado**: 🔄 **DISPONIBLE** para resolución

### 🕶️ **[Enter the Matrix](enter-the-matrix/)**
- **Categoría**: Web + Cryptography
- **Dificultad**: 🟢 **Fácil**
- **Objetivo**: Navegación web + descifrado hash
- **Técnicas**: Multi-stage web challenge, Hash cracking
- **Archivos**: 5 (HTML, JS, crypto hash)
- **Estado**: 🔄 **DISPONIBLE** para resolución

### 🏦 **[OmniVault Web Interface](omnivault-web/)**
- **Categoría**: Web Application Security
- **Dificultad**: 🟢 **Fácil**
- **Objetivo**: Análisis frontend de banca online
- **Técnicas**: Client-side security, Authentication analysis
- **Archivos**: 3 interfaces HTML
- **Estado**: 🔄 **DISPONIBLE** para resolución

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
| **Desafíos incluidos** | 6 |
| **Archivos totales** | 177+ |
| **Scripts desarrollados** | 140+ |
| **Vulnerabilidades cubiertas** | 15+ |
| **Categorías técnicas** | 8 |
| **Líneas de código** | 15,000+ |

### **Distribución por Categorías**
- 🏦 **Web Security**: 3 desafíos (OmniVault x2, Agroindustrial)
- 🏠 **IoT/Network**: 1 desafío (Shadow Coordinator)
- 🔧 **DevOps/CI-CD**: 1 desafío (GitOps)
- 🕶️ **Web+Crypto**: 1 desafío (Matrix)

### **Distribución por Dificultad**
- 🟢 **Fácil**: 2 desafíos (Matrix, OmniVault-Web)
- 🟡 **Media**: 2 desafíos (Agroindustrial, GitOps)  
- ⚠️ **Alta**: 1 desafío (Infiltración Profunda)
- 🔥 **Muy Alta**: 1 desafío (Shadow Coordinator IoT)

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