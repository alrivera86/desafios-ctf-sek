# 🕶️ Enter the Matrix
## CTF-SEK Challenge Writeup

[![Difficulty](https://img.shields.io/badge/Difficulty-Easy-green)](https://github.com/alrivera86/desafios-ctf-sek)
[![Category](https://img.shields.io/badge/Category-Web%2FCrypto-purple)](https://github.com/alrivera86/desafios-ctf-sek)
[![Files](https://img.shields.io/badge/Files-5-green)](https://github.com/alrivera86/desafios-ctf-sek)

---

## 📋 **Challenge Information**

- **Name**: Enter the Matrix  
- **Category**: Web + Cryptography
- **Difficulty**: Easy
- **Files**: 5 (HTML, JavaScript, Hash)
- **Theme**: Matrix movie inspired challenge

---

## 🎯 **Challenge Description**

Desafío inspirado en "The Matrix" que combina análisis web con criptografía básica. Los participantes deben navegar a través de múltiples páginas web y descifrar información oculta para encontrar la flag.

---

## 📁 **Files Included**

### **Web Assets**
- `index.html` - Página principal (2.5KB)
- `url2.html` - Segunda página web (2.5KB) 
- `secret.html` - Página secreta (1.4KB)

### **JavaScript**
- `matrix.js` - Script de efectos Matrix (1.6KB)

### **Crypto**
- `hash.txt` - Hash o información codificada (65 bytes)

---

## 🛠️ **Technologies & Themes**

- **Frontend**: HTML5, JavaScript
- **Crypto**: Hash analysis/decoding
- **Theme**: The Matrix movie references
- **Challenges**: Web navigation + cryptographic puzzles

---

## 🔍 **Initial Analysis**

### **File Structure Overview**
```bash
web-assets/
├── index.html      # 2,538 bytes - Main entry point
├── url2.html       # 2,538 bytes - Secondary page
├── secret.html     # 1,364 bytes - Hidden content
├── matrix.js       # 1,558 bytes - Visual effects
crypto/
└── hash.txt        # 65 bytes - Cryptographic data
```

### **Matrix Theme Elements**
- **Visual Effects**: JavaScript Matrix rain effect
- **Hidden Navigation**: Multi-page puzzle structure
- **Cryptographic Elements**: Hash analysis required
- **References**: Matrix movie easter eggs

---

## 🔍 **Attack Surface & Strategy**

### **Web Application Analysis**
1. **Entry Point Investigation** - `index.html` analysis
2. **Navigation Flow** - Multi-page relationship mapping
3. **Hidden Content Discovery** - `secret.html` access methods
4. **JavaScript Analysis** - `matrix.js` functionality review

### **Cryptographic Analysis**
1. **Hash Identification** - `hash.txt` content analysis
2. **Decoding Attempts** - Multiple hash/encoding methods
3. **Context Clues** - Web content hints for decryption
4. **Flag Assembly** - Combining web + crypto results

---

## 🚀 **Recommended Approach**

### **Phase 1: Web Reconnaissance**
```bash
# Analyze main pages
1. Start with index.html - look for navigation clues
2. Follow links to url2.html - identify progression
3. Discover access method to secret.html
4. Analyze matrix.js for hidden functionality
```

### **Phase 2: Cryptographic Challenge**
```bash
# Hash analysis
1. Examine hash.txt content and format
2. Identify hash type (MD5, SHA1, Base64, etc.)
3. Use context from web pages as decryption hints
4. Apply appropriate decoding/cracking methods
```

### **Phase 3: Flag Extraction**
```bash
# Combine results
1. Correlate web navigation findings
2. Apply cryptographic solution
3. Extract final flag from combined solution
```

---

## 🧮 **Cryptographic Techniques**

### **Potential Hash Types**
- **MD5** - 32 character hexadecimal
- **SHA1** - 40 character hexadecimal  
- **Base64** - Encoded text strings
- **ROT13** - Simple Caesar cipher
- **Custom Encoding** - Theme-specific cipher

### **Tools & Methods**
- **Hash Identification**: `hashid`, online hash analyzers
- **Cracking**: `john`, `hashcat`, online tools
- **Decoding**: `base64`, `cyberchef`, manual methods

---

## 🎭 **Matrix References & Easter Eggs**

Expected references to look for:
- **Red/Blue Pill** symbolism
- **Neo/Morpheus** character references
- **"Follow the White Rabbit"** navigation hints
- **Matrix Digital Rain** visual effects
- **Zion/Matrix** world references

---

## 📚 **Learning Outcomes**

- **Multi-stage Challenge** navigation
- **Basic Cryptography** application  
- **Web Content Analysis** techniques
- **Context-based Decryption** methods
- **JavaScript Analysis** for hidden functionality

---

## 🔗 **Useful Resources**

- [CyberChef](https://gchq.github.io/CyberChef/) - Multi-tool for crypto
- [Hash Analyzer](https://www.tunnelsup.com/hash-analyzer/)
- [Matrix Digital Rain Tutorial](https://dev.to/javascriptacademy/create-the-matrix-raining-code-effect-using-javascript-4hep)

---

## 💡 **Pro Tips**

1. **Sequential Analysis** - Follow logical page progression
2. **Theme Integration** - Use Matrix references as clues
3. **Multi-discipline** - Combine web + crypto findings
4. **JavaScript Inspection** - Check for hidden variables/functions

---

*Part of [desafios-ctf-sek](../) collection | Easy-level introductory challenge*