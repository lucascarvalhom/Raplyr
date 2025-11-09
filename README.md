# Raplyr
Respository for Raplyr - Preenchimento automático de formulários Microsoft, rápido, simples e configurável.

---

██████╗ █████╗ ██████╗ ██╗ ██╗ ██╗██████╗
██╔══██╗██╔══██╗██╔══██╗██║ ██║ ██║██╔══██╗
██████╔╝███████║██████╔╝██║ ██║ ██║██████╔╝
██╔══██╗██╔══██║██╔══██╗██║ ██║ ██║██╔══██╗
██║ ██║██║ ██║██║ ██║███████╗╚██████╔╝██████╔╝
╚═╝ ╚═╝╚═╝ ╚═╝╚═╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝

---

# 🤖 Raplyr

**Raplyr** é uma aplicação em **Python** desenvolvida para **automação inteligente de formulários Microsoft**.
A ferramenta utiliza um **arquivo de configuração personalizável**, onde é possível definir:

* a **URL** do formulário,
* as **perguntas esperadas**, e
* as **respostas correspondentes**,

permitindo o **preenchimento automático, rápido e preciso** de qualquer formulário padronizado.

💡 **Ideal para:** equipes que buscam otimizar tempo em **cadastros, pesquisas, processos internos** ou **rotinas repetitivas**.
O **Raplyr** combina **praticidade, velocidade e flexibilidade**, garantindo **eficiência** e **confiabilidade dos dados** — tudo isso sem exigir configurações complexas nem dependências externas.

---

## 📦 Requisitos

Antes de executar o Raplyr, garanta que os seguintes componentes estejam instalados:

* [Python 3.10+](https://www.python.org/downloads/)
* [Google Chrome](https://www.google.com/chrome/) (navegador utilizado para automação)
* Pacotes Python listados em `requirements.txt`

Instale as dependências com:

```bash
pip install -r requirements.txt
```
---

## ⚙️ Configuração inicial

Ao executar o Raplyr pela primeira vez, ele criará automaticamente um arquivo chamado:

```
config_preencher_forms.txt
```

Esse arquivo contém os parâmetros de configuração necessários, por exemplo:

```ini
# Configuração do Raplyr
URL=https://forms.office.com/...
EnviarAoPreencher=sim

# Perguntas e respostas
Nome completo=Teste
Sexo=Masculino
Turno=T3 
```

📝 **Edite esse arquivo** de acordo com o formulário que deseja automatizar.

Se preferir que o formulário **não seja enviado automaticamente**, defina:

```ini
EnviarAoPreencher=nao
```

---

## ▶️ Execução

Para rodar a aplicação em modo desenvolvimento:

```bash
python Raplyr.py
```

O programa abrirá o navegador, acessará o formulário definido e preencherá automaticamente os campos conforme as configurações.

Caso algum campo não seja encontrado ou ocorra erro, mensagens detalhadas serão exibidas no console e salvas no log (`raplyr.log`).

---

## 🧱 Geração de executável

Para criar um executável independente (sem necessidade de Python instalado):

```bash
pyinstaller --onefile --clean --noconfirm --strip Raplyr.py
```

O executável será gerado dentro da pasta `dist/`:

```
dist/Raplyr.exe
```

💡
Você pode distribuir esse arquivo para qualquer usuário que tenha o **Google Chrome** instalado — o Raplyr detectará automaticamente o navegador do sistema.

---

## 🧰 Funcionalidades

✅ Leitura automática do arquivo de configuração
✅ Preenchimento inteligente de campos de texto, múltipla escolha e caixas de seleção
✅ Compatibilidade com formulários Microsoft Forms
✅ Rolagem automática até o campo antes do preenchimento
✅ Logs detalhados de execução
✅ Opção de envio automático ou manual
✅ Interface leve com notificações de erro via janela do sistema

---

## ⚖️ Licença

Este projeto é distribuído sob a licença **MIT**.
Sinta-se livre para usar, modificar e distribuir — apenas mantenha os créditos ao autor original.

---

## 👤 Autor

**Lucas Carvalho**
💼 Tech Lead | OutSystems Expert | Python Automation Enthusiast
📧 [lucas.miranda.ito@gmail.com](mailto:lucas.miranda.ito@gmail.com)
🌐 [GitHub Profile](https://github.com/lucascarvalhom) 
