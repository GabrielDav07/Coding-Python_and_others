# Repositório de Códigos & Projetos — Cybersecurity, DevSecOps & Web

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5/CSS3](https://img.shields.io/badge/HTML5%20%2F%20CSS3-E34F26?style=for-the-badge&logo=html5&logoColor=white)

<br/>

> **Hub central de projetos práticos e acadêmicos**, reunindo implementações em **Cibersegurança**, **Defesa e Mitigação OWASP**, **Detecção de Ameaças com Machine Learning**, **Engenharia de Dados Relacional & NoSQL** e **Experimentos Criativos de Frontend**.

[Sobre o Repositório](#-sobre) • [Estrutura](#-estrutura-de-pastas) • [Módulos em Destaque](#-módulos-em-destaque) • [Como Executar](#-como-executar) • [Tecnologias](#-tecnologias-e-ferramentas)

</div>

---

## 📌 Sobre

Este repositório consolida a evolução prática em **Engenharia de Software Segura (Coding for Security)**, projetos acadêmicos desenvolvidos na **FIAP** e protótipos autorais de desenvolvimento web e computação visual.

O foco central é a aplicação de princípios de **Security by Design**, conformidade com os padrões da **OWASP Top 10**, automação de resposta a incidentes (SIEM), esteiras de dados híbridas e modelos de IA para detecção precoce de anomalias em redes e aplicações.

---

## 📂 Estrutura de Pastas

```plaintext
├── 📁 Codes_FIAP_2026/
│   ├── 📁 CP1_coding/               # Motor de Detecção e Correlação de Ameaças (SIEM)
│   │   ├── detector.py              # Algoritmos de detecção de Brute Force, Port Scan e IOCs
│   │   ├── regras.py                # Mecanismo de parsing de regras e classificação de severidade
│   │   ├── demonstracao.py          # Script de testes e simulação de ataques
│   │   └── config/                  # Regras dinâmicas (JSON) e listas de reputação
│   │
│   ├── 📁 CP2_Coding/               # Coding for Security & DevSecOps Avançado
│   │   ├── ex1.py                   # Matriz de Decisão CAP vs ACID mapeada ao OWASP Top 10
│   │   ├── ex2.py                   # Pipeline ETL: Migração Relacional (MySQL) para NoSQL (MongoDB)
│   │   ├── ex3.py                   # Gestão de Telemetria com Índices TTL e Janelas Deslizantes
│   │   ├── ex4.py                   # Arquitetura Híbrida: Transações ACID com Auditoria Imutável
│   │   ├── ex5.py                   # APIs Flask Seguras: Mitigação de SQL Injection via Whitelist
│   │   ├── ex6.py                   # Controle de Acesso e Mitigação de IDOR (OWASP A01)
│   │   ├── ex7.py                   # Proteção contra XSS, Auto-Escaping e Headers CSP
│   │   ├── ex8.py                   # Detecção de Ameaças com Machine Learning (Random Forest)
│   │   └── ex9.py                   # Detecção de Anomalias e Rate Limiting com Isolation Forest
│   │
│   └── 📁 2º SEMESTRE Coding/       # Fundamentos de Banco de Dados, SQL e Lógica
│       ├── Ex1_1.sql / Ex1_2.sql    # Modelagem relacional e consultas DDL/DML
│       ├── Ex1_3decisoes_cap.md     # Documentação de decisões arquiteturais e Teorema CAP
│       └── Ex2_1.py ... Ex8_3.py    # Exercícios práticos de algoritmos, dados e segurança
│
└── 📁 Personal_Projects/            # Experimentos de Interface e Computação Visual
    ├── Lampshade.html               # UI de Login interativa com física de luz pura em CSS/HTML
    └── Lizard.html                  # Simulação de Cinemática Inversa (IK) em Canvas HTML5
```

---

## 🚀 Módulos em Destaque

### 1. 🛡️ Motor de Detecção de Incidentes & SIEM (`CP1_coding`)
Desenvolvimento de uma engine em Python focada em triagem e análise comportamental de logs de segurança:
- **Detecção Temporal de Brute Force:** Algoritmo de janela deslizante (*sliding window*) que correlaciona picos de falhas de autenticação (`FAIL`) dentro de limiares de tempo customizáveis.
- **Detecção de Port Scanning:** Mapeamento de portas bloqueadas por firewall utilizando estruturas de `set` em memória para alta performance.
- **Cruzamento com Threat Intelligence:** Interseção de conjuntos para validação instantânea de IPs maliciosos contra listas negras (IOCs).
- **Consolidação Matricial de Severidade:** Cálculo composto de criticidade (`INFO`, `BAIXA`, `MÉDIA`, `ALTA`, `CRÍTICA`) com escalonamento dinâmico em caso de múltiplos vetores de ataque concomitantes.

---

### 2. 🔒 Defesa de Aplicações, OWASP & DevSecOps (`CP2_Coding`)
Implementações práticas para resolução e mitigação de vulnerabilidades críticas:

| Script | Tema Central | Vulnerabilidade / Conceito |
| :--- | :--- | :--- |
| **`ex1.py`** | Arquitetura de Dados & OWASP | Trade-offs do Teorema CAP (CP vs AP) e ACID vs BASE vinculados às vulnerabilidades OWASP A04, A07, A08 e A09. |
| **`ex2.py`** | Pipeline ETL & Migração de Dados | Migração automatizada entre MySQL e MongoDB com preservação de integridade referencial em documentos aninhados. |
| **`ex3.py`** | Retenção & Conformidade | Índices TTL (Time-To-Live) no MongoDB para expiração automática de telemetria após 7 dias e análise de picos de tráfego. |
| **`ex4.py`** | Arquitetura de Auditoria Híbrida | Transações relacionais com rollback automático no MySQL integradas a trilhas de auditoria imutáveis no MongoDB. |
| **`ex5.py`** | Segurança em APIs REST | Prevenção contra SQL Injection em ordenações dinâmicas (`ORDER BY`) através de validação estrita por lista branca. |
| **`ex6.py`** | Quebra de Controle de Acesso | Prevenção contra IDOR (*Insecure Direct Object Reference*) via autenticação por API-Key e validação de propriedade de registros (OWASP A01). |
| **`ex7.py`** | Mitigação de Injeção de Código | Proteção contra XSS Refletido e Armazenado em Jinja2 e aplicação de cabeçalhos restritivos de *Content-Security-Policy* (CSP). |
| **`ex8.py`** | IA Aplicada à Segurança | Classificador supervisionado com `RandomForestClassifier` (Scikit-Learn) para predição e pontuação de anomalias em tempo real. |
| **`ex9.py`** | Rate Limiting Inteligente | Modelo não supervisionado `IsolationForest` para detecção de anomalias comportamentais e bloqueio adaptativo (HTTP 429). |

---

### 3. 💾 Arquitetura de Dados & SQL (`2º SEMESTRE Coding`)
- Modelagem de esquemas relacionais normalizados em SQL.
- Queries analíticas e otimização de consultas com filtros e agregações.
- Registro formal de decisões arquiteturais com foco em tolerância a partição e disponibilidade.

---

### 4. 🎨 Projetos Pessoais & Computação Gráfica (`Personal_Projects`)
- **💡 Lamp Animated Login (`Lampshade.html`):** Interface de autenticação com estética dark moderna e física de iluminação simulada. Ao acionar o interruptor da luminária, a cena projeta reflexos dinâmicos e revela os inputs do formulário.
- **🦎 Inverse Kinematics Lizard (`Lizard.html`):** Algoritmo de cinemática inversa implementado no HTML5 Canvas, produzindo animação procedural fluida de membros e coluna que reagem dinamicamente à movimentação do cursor.

---

## 🛠️ Como Executar

### 📋 Pré-requisitos
- [Python 3.10+](https://www.python.org/)
- [Docker](https://www.docker.com/) & Docker Compose
- Navegador Web moderno

### 1. Clonar o Repositório
```bash
git clone https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git
cd NOME-DO-REPOSITORIO
```

### 2. Configurar o Ambiente Virtual
```bash
python -m venv .venv

# No Windows (PowerShell):
.venv\Scripts\Activate.ps1

# No Linux/macOS:
source .venv/bin/activate

# Instalar dependências
pip install flask mysql-connector-python pymongo scikit-learn numpy
```

### 3. Subir os Bancos de Dados com Docker
Para os exercícios práticos que utilizam MySQL e MongoDB:

```bash
# Iniciar container MySQL
docker run -d --name mysql-lab -p 3306:3306 -e MYSQL_ROOT_PASSWORD=senha -e MYSQL_DATABASE=seguranca mysql:8

# Iniciar container MongoDB
docker run -d --name mongo-lab -p 27017:27017 mongo:7
```

### 4. Executar os Scripts de Segurança
```bash
# Executar o motor de detecção (CP1)
python Codes_FIAP_2026/CP1_coding/demonstracao.py

# Testar migração e consultas seguras (CP2)
python Codes_FIAP_2026/CP2_Coding/ex2.py

# Iniciar API com detecção por Machine Learning
python Codes_FIAP_2026/CP2_Coding/ex8.py
```

### 5. Executar os Projetos de Frontend
Para visualizar os projetos de interface interativa:

```bash
cd Personal_Projects
python -m http.server 5000
```
Acesse no seu navegador:
- Luminária Interativa: [http://localhost:5000/Lampshade.html](http://localhost:5000/Lampshade.html)
- Simulação de Cinemática: [http://localhost:5000/Lizard.html](http://localhost:5000/Lizard.html)

---

## 🧰 Tecnologias e Ferramentas

| Domínio | Tecnologias |
| :--- | :--- |
| **Linguagens** | Python 3, SQL, JavaScript (ES6+), HTML5, CSS3 |
| **Frameworks Web** | Flask, Jinja2 |
| **Bancos de Dados** | MySQL 8, MongoDB 7, PyMongo, MySQL Connector |
| **Machine Learning** | Scikit-Learn (Random Forest, Isolation Forest), NumPy |
| **DevOps & Infra** | Docker, Containers, Git, GitHub, VS Code |
| **Segurança & Boas Práticas** | OWASP Top 10, SIEM Log Analysis, Rate Limiting, CSP Headers, Sanitização de Dados |

---

## 👨‍💻 Autor

Desenvolvido por **Gabriel Barros Davanço** 

Estudante de Cibersegurança na instituição **FIAP**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gabriel-barros-davan%C3%A7o-ba469b315/?isSelfProfile=true)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/GabrielDav07)


---

<div align="center">
  <sub>⭐️ Sinta-se à vontade para explorar os códigos, abrir issues ou sugerir melhorias!</sub>
</div>
