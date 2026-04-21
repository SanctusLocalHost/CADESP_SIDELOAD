# CADESP_SIDELOAD | OSINT Framework

![Status](https://img.shields.io/badge/Status-Project%20Alpha-green?style=for-the-badge)
![Language](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Focus](https://img.shields.io/badge/Focus-OSINT%20%26%20Recon-black?style=for-the-badge&logo=hackthebox&logoColor=green)

**CADESP_SIDELOAD** é uma ferramenta de **OSINT (Open Source Intelligence)** focada em reconhecimento corporativo e inteligência de dados cadastrais. Ela automatiza a coleta de dados de empresas brasileiras através de múltiplas camadas de APIs públicas, estruturando payloads brutos em relatórios de inteligência.

---

## Interface & Terminal

<div align="center">
  <img src="https://github.com/user-attachments/assets/e86b97ff-7293-4d0f-8c0d-e72d41e55c55" alt="Terminal UI" width="900px">
</div>

---

## Funcionalidade

Ferramenta desenhada para fluxos de trabalho de **Ethical Hacking** e **Investigação Digital**:

* **Agregação Multicamadas:** Consulta simultânea em diversos mirrors (BrasilAPI, ReceitaWS, CNPJ.ws, MinhaReceita).
* **Intelligence Classification:** Motor interno que analisa CNAEs e Razão Social para classificar automaticamente o perfil operacional do alvo (Indústria, Comércio, etc.).
* **Mapeamento de Superfície:** Identificação rápida de Sócios (QSA), Capital Social e endereços para construção de diagramas de relacionamento.
* **Exportação Forense:** Geração de relatórios PDF organizados por categorias (Tributário, Contato, Sócios) para documentação de evidências.

---

### Recursos da UI:
* **Terminal interativo:** Efeito de máquina de escrever para logs de processamento.
* **Motor de busca (Ctrl+F):** Localize strings específicas dentro do payload retornado com destaque em tempo real.
* **Barra de Status:** Acompanhamento visual de requisições e processamento de dados.

---

## Stack Técnica

| Componente | Tecnologia | Função |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.10+ | Core da aplicação |
| **Interface** | CustomTkinter | Interface |
| **Requisições** | Requests | Comunicação com APIs de OSINT |
| **Processamento** | Pandas | Tratamento e achatamento de dicionários JSON |
| **Relatórios** | fpdf2 | Geração de PDFs estruturados |

---

## Instalação

Clone o repositório e instale as dependências necessárias:

```bash
# Clone o projeto
git clone [https://github.com/SanctusLocalHost/CADESP_SIDELOAD.git](https://github.com/SanctusLocalHost/CADESP_SIDELOAD.git)

# Entre no diretório
cd CADESP_SIDELOAD

# Instale as dependências
pip install customtkinter requests pandas openpyxl fpdf2
