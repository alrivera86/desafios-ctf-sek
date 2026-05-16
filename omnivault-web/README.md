# 🏦 OmniVault Web Interface
## CTF-SEK Challenge Writeup

[![Difficulty](https://img.shields.io/badge/Difficulty-Easy-green)](https://github.com/alrivera86/desafios-ctf-sek)
[![Category](https://img.shields.io/badge/Category-Web-blue)](https://github.com/alrivera86/desafios-ctf-sek)
[![Files](https://img.shields.io/badge/Files-3-green)](https://github.com/alrivera86/desafios-ctf-sek)

---

## 📋 **Challenge Information**

- **Name**: OmniVault Web Interface
- **Category**: Web Application Security  
- **Difficulty**: Easy
- **Files**: 3 HTML files
- **Related**: Simplified version of [Infiltración Profunda](../infiltracion-omnivault/)

---

## 🎯 **Challenge Description**

Versión simplificada del sistema bancario OmniVault que se centra en el análisis del frontend web y vulnerabilidades básicas de aplicaciones web. Este desafío sirve como introducción antes del complejo desafío de "Infiltración Profunda".

---

## 📁 **Files Included**

### **Web Analysis**
- `index.html` - Página principal del banco (2.8KB)
- `login.html` - Portal de acceso (2.0KB)
- `abrir.html` - Funcionalidad de apertura (2.5KB)

---

## 🛠️ **Technologies**

- **Frontend**: HTML5, CSS, JavaScript
- **Theme**: Banking application interface
- **Focus**: Client-side security, authentication flows
- **Complexity**: Basic web application analysis

---

## 🔍 **Initial Analysis**

### **File Structure**
```bash
web-analysis/
├── index.html    # 2,808 bytes - Main banking interface
├── login.html    # 2,016 bytes - Authentication portal  
└── abrir.html    # 2,546 bytes - Account opening functionality
```

### **Banking Interface Components**
- **Main Portal** - Corporate banking interface
- **Login System** - User authentication flow
- **Account Management** - Account opening/management

---

## 🔒 **Security Assessment Areas**

### **Web Application Vulnerabilities**
1. **Authentication Bypass** - Login mechanism analysis
2. **Client-Side Validation** - JavaScript security controls
3. **Session Management** - Cookie and token handling
4. **Information Disclosure** - Hidden content or comments
5. **Business Logic Flaws** - Banking operation manipulation

### **Attack Vectors**
```bash
# Authentication Testing
├── login.html     # Authentication bypass attempts
├── index.html     # Session management analysis
└── abrir.html     # Business logic exploitation
```

---

## 🚀 **Recommended Testing Approach**

### **Phase 1: Interface Analysis**
```bash
1. Analyze index.html for navigation and functionality
2. Review login.html for authentication mechanisms  
3. Examine abrir.html for business logic flows
4. Check for hidden content, comments, or JavaScript
```

### **Phase 2: Security Testing**
```bash
1. Test login bypass techniques
2. Analyze client-side validation  
3. Look for hardcoded credentials
4. Check for information leakage in source
```

### **Phase 3: Exploitation**
```bash
1. Exploit identified vulnerabilities
2. Extract sensitive information
3. Bypass authentication if possible
4. Achieve unauthorized access to banking functions
```

---

## 🔍 **Common Web Vulnerabilities to Test**

### **Frontend Security Issues**
- **🔐 Weak Authentication** - Default or weak credentials
- **📝 Client-Side Validation** - Bypassable JavaScript checks
- **💾 Local Storage** - Sensitive data in browser storage
- **🕵️ Information Disclosure** - Comments, hidden fields
- **🔄 Session Issues** - Poor session management

### **Banking-Specific Tests**
- **💰 Transaction Manipulation** - Price/amount tampering
- **👤 Account Enumeration** - Valid account discovery
- **🔒 Access Control** - Unauthorized function access
- **📊 Business Logic** - Flow manipulation

---

## 📊 **Analysis Checklist**

### **Source Code Review**
```html
<!-- Look for: -->
- Hidden form fields with sensitive data
- JavaScript with hardcoded credentials  
- Comments with development information
- Exposed API endpoints or backend URLs
- Client-side authentication logic
```

### **Functionality Testing**
```bash
# Test each page for:
├── Authentication bypass
├── Parameter manipulation  
├── Hidden functionality
├── Error message leakage
└── Business logic flaws
```

---

## 🧪 **Testing Tools**

### **Browser-Based**
- **Developer Tools** - Source inspection, network analysis
- **Burp Suite** - Web application security testing
- **OWASP ZAP** - Automated vulnerability scanning

### **Manual Analysis**
- **View Source** - HTML/JavaScript review
- **Network Tab** - Request/response analysis  
- **Console** - JavaScript debugging
- **Storage** - Local/session storage inspection

---

## 📚 **Learning Outcomes**

- **Web Application Basics** - HTML/JS security analysis
- **Authentication Testing** - Login mechanism evaluation
- **Business Logic Review** - Banking application flows
- **Source Code Analysis** - Client-side security assessment
- **Browser Security Tools** - Developer tools proficiency

---

## 🔗 **Relationship to Other Challenges**

### **Progression Path**
```bash
1. OmniVault Web (This) → Basic web analysis skills
2. Infiltración Profunda   → Advanced exploitation (CVE-2022-22963)
```

This challenge serves as preparation for the more complex [Infiltración Profunda](../infiltracion-omnivault/) challenge which involves:
- Backend exploitation (Spring Cloud Function RCE)  
- Network pivoting and reconnaissance
- Advanced authentication bypass
- Full banking application compromise

---

## 💡 **Pro Tips**

1. **Progressive Complexity** - Start simple before advanced challenges
2. **Source Analysis** - Always view page source first
3. **JavaScript Focus** - Client-side logic often contains flaws
4. **Error Exploitation** - Error messages reveal information
5. **Business Context** - Understand banking workflow for logic flaws

---

## 📖 **Quick Start**

```bash
# Basic analysis workflow:
1. Open each HTML file in browser
2. View source code for hidden content
3. Test login functionality with common credentials
4. Analyze JavaScript for hardcoded values
5. Look for business logic manipulation opportunities
```

---

*Part of [desafios-ctf-sek](../) collection | Entry-level web security challenge*