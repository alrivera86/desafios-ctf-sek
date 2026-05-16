# Reconnaissance - Shadow Coordinator

## 📊 Archivos de Reconocimiento

### 🌐 Capturas de Tráfico PCAP
| Archivo | Descripción | Tamaño |
|---------|-------------|--------|
| `capture_20260514_114936.pcap` | Tráfico HTTP target IEEE 802.15.4 | 19KB |
| `capture_https_20260514_120136.pcap` | Tráfico HTTPS target IEEE 802.15.4 | 19KB |

**Frame Crítico Identificado:** Frame 307 (39 bytes únicos)
- Device: 0x7B9C
- IEEE Address: 00:15:8d:00:02:1a:2b:3c
- Capability: 0x8e, Sequence: 51

### 🔍 Resultados de Fuzzing
| Archivo | Herramienta | Resultados |
|---------|-------------|------------|
| `ffuf_shadow_coordinator_20260514_122454.json` | ffuf | 1.4MB endpoints |

**Comando utilizado:**
```bash
ffuf -u https://training.my-ctf.com:8812/FUZZ -w /usr/share/wordlists/dirb/common.txt
```

### 🏗️ Arquitectura del Sistema
| Archivo | Contenido |
|---------|-----------|
| `zigbee_topology_20260514_115125.json` | Topología red Zigbee completa |
| `states_api_20260514_115027.json` | Estados API del sistema |

### 🔐 Credenciales y Tokens
| Archivo | Descripción |
|---------|-------------|
| `api_token.txt` | Token Bearer para autenticación |
| `cookies_admin.txt` | Cookies de sesión admin |
| `operator_token.txt` | Token de operator |

### 📋 Información de Configuración
| Archivo | Contenido |
|---------|-----------|
| `config_files.txt` | Archivos de configuración encontrados |
| `api_exploration.txt` | Endpoints API descubiertos |
| `final_flag_search.txt` | Resultados búsqueda final |

## 🎯 Hallazgos Clave

### Red Zigbee Mapeada
```
Coordinator (0x0000) - BCH Facilities ZB-GW-03 [COMPROMETIDO]
├── Smart Lock (0x7B9C) - Yale YRD256 [COMPROMETIDO]
├── Sensor Temperatura (0x1A2B) - Valores anómalos
├── Sensor Movimiento (0x3C4D) - Normal  
└── Actuator Control (0x5E6F) - Normal
```

### Credenciales Válidas
```
admin:admin1234 (Owner role)
operator:operator123 (Limited role)
```

### Endpoints API Críticos
```
POST /api/v2/services/lock/unlock  ⭐ TARGET CRÍTICO
GET  /api/v2/states
GET  /api/v2/zigbee/topology  
WS   /api/websocket
```

### Evidencia de Compromiso
- **Coordinador:** Estado "unlocked" + admin override
- **Smart Lock:** Buffer overflow confirmado
- **Temperaturas:** Valores negativos anómalos (-3.8, -4.1)
- **Git Repo:** Código fuente `old_coordinator.py` expuesto

---

*Reconocimiento completado - Mayo 2026*