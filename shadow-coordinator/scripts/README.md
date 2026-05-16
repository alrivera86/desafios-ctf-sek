# Scripts - Shadow Coordinator CTF

## 📁 Descripción de Scripts

Este directorio contiene **20 scripts especializados** desarrollados durante el análisis del CTF Shadow Coordinator.

### 🎯 Scripts Principales

| Script | Función Principal | Líneas | Técnica |
|--------|------------------|--------|---------|
| [`shadow_coordinator_exploit.py`](shadow_coordinator_exploit.py) | Exploit principal con WebSocket monitoring | 400+ | Cluster ZHA 257 + Real-time |
| [`async_flag_monitor.py`](async_flag_monitor.py) | Monitor servicios asíncronos | 300+ | Context tracking |
| [`template_injection_exploit.py`](template_injection_exploit.py) | Jinja2 template injection | 250+ | Code injection |
| [`smart_lock_exploit_clean.py`](smart_lock_exploit_clean.py) | Buffer overflow Yale YRD256 | 200+ | Memory corruption |

### 🔬 Scripts de Análisis Avanzado

| Script | Especialización |
|--------|-----------------|
| [`system_coordinator_exploit.py`](system_coordinator_exploit.py) | Servicios específicos del coordinador |
| [`ieee_flag_decode.py`](ieee_flag_decode.py) | Decodificación IEEE addresses |
| [`firmware_static_analysis.py`](firmware_static_analysis.py) | Análisis estático de firmware |
| [`smart_lock_buffer_overflow.py`](smart_lock_buffer_overflow.py) | Análisis detallado buffer overflow |

### 📊 Scripts de Monitoring

| Script | Propósito |
|--------|-----------|
| [`extended_websocket_monitor.py`](extended_websocket_monitor.py) | Monitor WebSocket extendido |
| [`websocket_snapshot_analysis.py`](websocket_snapshot_analysis.py) | Análisis snapshots WebSocket |
| [`system_service_websocket_monitor.py`](system_service_websocket_monitor.py) | Monitor servicios + WebSocket |
| [`temperature_monitor.py`](temperature_monitor.py) | Monitor patrones temperatura |

### 🛠️ Scripts de Exploración

| Script | Función |
|--------|---------|
| [`cluster_exploration.py`](cluster_exploration.py) | Exploración clusters ZHA |
| [`state_analysis.py`](state_analysis.py) | Análisis estados del sistema |
| [`persistent_websocket.py`](persistent_websocket.py) | Conexión WebSocket persistente |
| [`shadow_websocket.py`](shadow_websocket.py) | WebSocket específico Shadow |

### 🔍 Scripts de Búsqueda Final

| Script | Objetivo |
|--------|----------|
| [`final_flag_hunt.py`](final_flag_hunt.py) | Búsqueda comprehensiva final |
| [`direct_flag_search.py`](direct_flag_search.py) | Búsqueda directa archivos comunes |
| [`flag_extraction_final.py`](flag_extraction_final.py) | Extracción final automatizada |
| [`complete_analysis.py`](complete_analysis.py) | Análisis completo automatizado |

## 🚀 Uso de Scripts

### Ejecución Básica
```bash
# Script principal
python3 shadow_coordinator_exploit.py

# Monitor asíncrono
python3 async_flag_monitor.py

# Búsqueda final
python3 final_flag_hunt.py
```

### Variables de Entorno
```bash
export TARGET_HTTP="http://training-pod2.ctfchile.com:32780"
export TARGET_HTTPS="https://training.my-ctf.com:8812"
export ADMIN_USER="admin"
export ADMIN_PASS="admin1234"
```

### Dependencias
```bash
pip install requests websocket-client scapy
```

## 📈 Estadísticas

- **Total scripts:** 20
- **Líneas de código total:** ~3,000+
- **Técnicas implementadas:** 15+
- **APIs exploradas:** 25+ endpoints
- **Context IDs generados:** 51+

## 🎯 Resultados Clave

### ✅ Éxitos Técnicos
- Buffer overflow confirmado en Yale YRD256
- Coordinador estado "unlocked" confirmado
- Frame 307 único identificado (39 bytes)
- Git repository extraído exitosamente
- SSRF a internal-api:8080 confirmado

### ❌ Limitaciones
- Token válido para unlock service no encontrado
- Servicios asíncronos con respuestas vacías
- Template injection sin código execution
- Flag final no extraída

## 📝 Notas de Desarrollo

1. **Todos los scripts usan authentication Bearer token**
2. **WebSocket monitoring requiere conexión persistente**
3. **PCAP analysis reveló Frame 307 como crítico**
4. **Mathematical correlations detectadas en temperaturas**
5. **Device 0x7B9C confirmado como target crítico**

---

*Scripts desarrollados durante análisis Shadow Coordinator CTF - Mayo 2026*