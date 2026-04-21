# Consulta Estruturada de Database - Cadastro de Contribuintes

O Software realiza consultas de Dados Cadastrais de Empresas (contribuintes do ICMS) utilizando o CNPJ ou a Inscrição Estadual, integrando os resultados de diversas APIs públicas.

---

## Interface

<img width="1052" height="982" alt="image" src="https://github.com/user-attachments/assets/45dead14-d839-463e-9e82-35e5214b99fa" />

---

## Funcionalidades Principais

- **Múltiplas APIs Integradas:** Suporte para BrasilAPI, ReceitaWS, CNPJ.ws e MinhaReceita.
- **Tipos de Busca:** Consulta por CNPJ ou Inscrição Estadual (focada em SP via BrasilAPI).
- **Interface Terminal:** Exibição dos dados brutos e tratados em uma interface escura inspirada em terminais de linha de comando, incluindo barra de progresso e efeito máquina de escrever.
- **Motor de Busca Interno:** Ferramenta de localização de texto (Ctrl+F) embutida no terminal de exibição com destaque de resultados e navegação.
- **Tratamento de Dados:** Achatamento automático de dicionários JSON complexos para visualização em lista.
- **Classificação Automática:** Identificação do perfil da empresa (Indústria, Comércio, ambos ou outros) baseada em palavras-chave da razão social e atividades.
- **Exportação em PDF:** Geração de relatórios PDF organizados por categorias (Empresa, Contato, Tributário, Sócios, etc.), salvos automaticamente na pasta Downloads.

## Pré-requisitos e Dependências

Para rodar o software, você precisa do Python 3 instalado em seu computador. As bibliotecas de terceiros necessárias são:

- `customtkinter`
- `requests`
- `pandas`
- `openpyxl` (utilizado como motor pelo pandas para lidar com tabelas temporárias)
- `fpdf2` (para a geração de PDFs modernos)

## Instalação

Abra o seu terminal ou prompt de comando e instale as dependências executando o código abaixo:

```bash
pip install customtkinter requests pandas openpyxl fpdf2
```
*Nota: Dependendo do sistema operacional (como distribuições Linux mais recentes), pode ser necessário usar um ambiente virtual (venv) ou adicionar a flag `--break-system-packages`.*

## Como Utilizar

1. Salve o código em um arquivo local, por exemplo `consulta_cadastral.py`.
2. Execute o script através do terminal:

```bash
python consulta_cadastral.py
```

3. Na interface gráfica:
   - Selecione no primeiro menu suspenso o tipo de chave: **CNPJ** ou **INSCRIÇÃO ESTADUAL**.
   - Selecione a API desejada no segundo menu.
   - Digite os números no campo de texto (pontos, barras e traços são removidos automaticamente pelo sistema).
   - Clique no botão **EXECUTAR** ou pressione a tecla `Enter`.
4. Aguarde a conclusão da requisição (acompanhe o status na barra inferior). Os dados aparecerão formatados na tela preta.
5. Quando a busca for concluída com sucesso, o botão **EXPORTAR PDF** ficará verde e habilitado. Clique nele para gerar e salvar o documento na sua pasta padrão de `Downloads`.

## Atalhos de Teclado

- `Enter` ou `Return`: Executa a consulta após digitar o documento.
- `Ctrl + F` (Windows/Linux) ou `Command + F` (macOS): Abre a barra de busca no terminal.
  - `Enter` na busca: Pula para o próximo resultado.
  - `Esc`: Fecha a barra de busca e limpa o texto destacado.

## Resolução de Problemas Comuns

- **Erro 429 (Muitas Requisições):** Algumas das APIs públicas limitam o número de consultas por minuto. Caso enfrente este erro, altere a API no menu suspenso (por exemplo, de BrasilAPI para ReceitaWS) e tente novamente.
- **Timeout (Tempo Esgotado):** A resposta do servidor demorou mais de 15 segundos. Verifique sua conexão com a internet ou altere a fonte de busca.

## Créditos

Desenvolvimento e interface por @Sanctus_LocalHost.
