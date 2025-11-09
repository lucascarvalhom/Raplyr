import time, logging, os, json, logging, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, WebDriverException
import tkinter as tk
from tkinter import messagebox

# ====================================================
# FUNÇÕES PADRÃO DE EXIBIÇÃO
# ====================================================
def exibir_mensagem(msg, tipo="I", titulo=None):
    """
    Exibe uma janela do tipo especificado:
      - tipo='E' → Erro
      - tipo='I' → Informação
      - tipo='W' → Aviso
    """
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal

    # Define título padrão conforme o tipo
    if not titulo:
        titulos = {"E": "Erro", "I": "Informação", "W": "Aviso"}
        titulo = titulos.get(tipo.upper(), "Mensagem")

    # Seleciona o tipo de messagebox
    tipo = tipo.upper()
    if tipo == "E":
        messagebox.showerror(titulo, msg)
    elif tipo == "W":
        messagebox.showwarning(titulo, msg)
    else:
        messagebox.showinfo(titulo, msg)

    root.destroy()
    
def exibir_input(titulo="Entrada de dados", mensagem="Informe o valor:"):
    """
    Exibe uma janela simples com campo de entrada e botões OK / Cancelar.
    Retorna o texto digitado ou None se o usuário cancelar.
    """
    root = tk.Tk()
    root.title(titulo)
    root.geometry("350x150")
    root.resizable(False, False)

    tk.Label(root, text=mensagem, pady=10).pack()

    entrada = tk.Entry(root, width=40)
    entrada.pack(pady=5)
    entrada.focus_set()

    valor = {"texto": None}

    def confirmar():
        valor["texto"] = entrada.get().strip()
        root.destroy()

    def cancelar():
        valor["texto"] = None
        root.destroy()

    botoes = tk.Frame(root)
    botoes.pack(pady=10)
    tk.Button(botoes, text="OK", width=10, command=confirmar).pack(side=tk.LEFT, padx=5)
    tk.Button(botoes, text="Cancelar", width=10, command=cancelar).pack(side=tk.LEFT, padx=5)

    root.mainloop()
    return valor["texto"]

# ====================================================
# FUNÇÕES DE PREENCHIMENTO
# ====================================================
def preencher_pergunta(driver, texto_pergunta, resposta):
    """
    Localiza uma pergunta pelo texto (ex: 'Nome completo') e preenche o campo correspondente.
    """
    try:
        # Localiza o bloco da pergunta que contém o texto desejado
        bloco = driver.find_element(
            By.XPATH,
            #f"//div[@data-automation-id='questionItem'][.//*[contains(text(), '{texto_pergunta}')]]"
            f"//div[@data-automation-id='questionItem'][.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{texto_pergunta.lower()}')]]"
        )
        
        # Rola até o bloco para evitar erro de preenchimento
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bloco)
        time.sleep(0.1)
                
        logging.info(f"Buscando '{texto_pergunta}' com '{resposta}'")
        # Tenta localizar campo de texto
        campos = bloco.find_elements(By.XPATH, ".//input | .//textarea")
        try:
            campo = campos[0]
            driver.execute_script("arguments[0].focus();", campo)
            campo.clear()
            campo.send_keys(resposta)
            print(f"Preencheu '{texto_pergunta}' com '{resposta}'")
            # Se não tiver campo de texto, encontrará erro nesse trecho.
        except Exception as eCampo:        
            # Se não for campo de texto, tenta localizar opções (múltipla escolha)
            try:
                opcoes = bloco.find_elements(By.XPATH, ".//input[@type='radio'] | .//input[@type='checkbox']")
                logging.info(f"Sucesso ao buscar inputs. {len(opcoes)} encontrados.")      
                
                for opcao in opcoes:
                    valor = (opcao.get_attribute("value") or "").strip().upper()
                    if resposta.strip().upper() in valor:
                        try:
                            #Tenta clicar direto no input
                            opcao.click()
                            print(f"Clicou diretamente em '{valor}'")
                            logging.info(f"Clicou diretamente em '{valor}'")     
                            return True
                        except ElementClickInterceptedException:
                            #Se falhar, tenta clicar no label pai
                            label = opcao.find_element(By.XPATH, "./ancestor::label[1]")
                            bloco.parent.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                            label.click()
                            logging.info(f"Clicou via label em '{valor}'")      
                            print(f"Clicou via label em '{valor}'")
                            return True
                        except Exception as e:
                            print(f"Erro ao clicar em '{valor}': {type(e).__name__} - {e}")
                            logging.error(f"Erro ao clicar em '{valor}': {type(e).__name__} - {e}")      
                            continue                       
                        
            except (StaleElementReferenceException, WebDriverException, Exception) as eT:
                print(f"Nenhum campo ou opção encontrado para '{texto_pergunta}'")
                logging.error(f"Erro ao buscar inputs dentro do bloco:", type(eT).__name__, "-", str(eT))                             
                # Tentativa de diagnóstico alternativo
                try:
                    logging.info(f"Tentando capturar HTML do bloco para análise:")
                    logging.info(bloco.get_attribute("outerHTML")[:1500])  # imprime só os 1500 primeiros caracteres
                except Exception as eG:
                    logging.error(f"Falha ao obter HTML do bloco:", type(eG).__name__, "-", str(eG))
                return
                 
    except NoSuchElementException:
        logging.warning("Pergunta '{texto_pergunta}' não encontrada no formulário.")
        print(f"Pergunta '{texto_pergunta}' não encontrada no formulário.")
                    
    except Exception as e:
        print(f"Nenhum campo ou opção encontrado para '{texto_pergunta}' - Erro ao preencher '{texto_pergunta}': {e}")
        logging.error(f"Nenhum campo ou opção encontrado para '{texto_pergunta}'. - Erro ao preencher '{texto_pergunta}': {e}'")
        logging.error(f"Erro ao buscar inputs dentro do bloco:", type(e).__name__, "-", str(e)) 
        
def enviar_formulario(driver, enviar_auto, enviar_botao):
    """
    Localiza e interage com o botão de envio do formulário conforme o parâmetro 'EnviarAoPreencher'.
    """
    try:
        # Busca por elementos que representem o botão "Enviar"
        botoes = driver.find_elements(
            By.XPATH,
            f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{enviar_botao.lower()}')]"
            f" | //input[@type='submit' and contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{enviar_botao.lower()}')]"
        )

        if not botoes:
            logging.warning(f"Nenhum botão '{enviar_botao}' encontrado.")
            exibir_mensagem(f"Nenhum botão '{enviar_botao}' encontrado. Envie manualmente.","W","Enviar formulario")
            return False

        botao = botoes[0]

        # Garante que o botão esteja visível
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
        time.sleep(0.1)

        if enviar_auto.strip().lower() == "sim":
            try:
                driver.execute_script("arguments[0].click();", botao)
                print("Formulário enviado automaticamente.")
                logging.info("Formulário enviado automaticamente.")
            except Exception as e_js:
                logging.warning(f"Falha ao clicar via JS: {e_js}. Tentando .click() nativo.")
                try:
                    print("Clique no botão.")
                    botao.click()
                except Exception as e_native:
                    logging.error(f"Falha ao clicar no botão '{enviar_botao}': {e_native}")
                    print(f"Falha ao clicar no botão '{enviar_botao}': {e_native}")
                    exibir_mensagem(f"Falha ao clicar no botão '{enviar_botao}'. Envie manualmente.","E","Enviar formulario")
                    return False            
            print("Formulário enviado automaticamente.")
            logging.info("Formulário enviado automaticamente.")
        else:
            try:
                # Foca o botão via JS (não usar botao.focus() diretamente)
                driver.execute_script("arguments[0].focus();", botao)
                # opcional: destacar visualmente (outline)
                driver.execute_script("arguments[0].style.boxShadow = '0 0 8px 3px rgba(0,123,255,0.6)';", botao)
                exibir_mensagem(f"Botão '{enviar_botao}' localizado. Pressione ENTER para enviar manualmente.","I","Enviar formulario")
                logging.info(f"Botão '{enviar_botao}' localizado. Aguardando confirmação manual.")
            except Exception as e:
                logging.error(f"Não foi possível focar o botão via JS: {e}")
        return True

    except Exception as e:
        logging.error(f"Erro ao tentar enviar o formulário: {type(e).__name__} - {e}")
        print(f"Erro ao tentar enviar o formulário: {type(e).__name__} - {e}")
        return False

# ====================================================
# FIM DE FUNÇÕES DE PREENCHIMENTO
# ====================================================
            
# ====================================================
# CONFIGURAÇÕES
# ====================================================
caminho_log="raplyr_log.log"

logging.basicConfig(
    filename=caminho_log,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def verificar_config():
    caminho_config = "raplyr_config.txt"
    
    # Se o arquivo não existir, cria com modelo padrão
    if not os.path.exists(caminho_config):
        config_exemplo = {
            "url_padrao":"https://forms.office.com/pages/responsepage.aspx?id=b0a_ZMGEpkqr5WXsX7GjJ4q-6KuAVY1CmKWdtiJ9xdxUODlPSjZIUkJDNE5KT0VPVzhKMUlKNUtEQy4u&route=shorturl",
            "respostas": {
                "Nome completo": "Testador da Silva",
                "CPF": "111111111111",
                "TELEFONE C/ DDD": "3499999999",
                "TURNO": "T3",
                "Os convocados serão informados no grupo": "Ciente",
                "Possui bota bico PVC": "NÃO POSSUO",
                "SEXO": "MASCULINO",
                "E-MAIL": "testedor@teste.com",
                "Após instruções no formulário, estou ciente que devo comparecer caso seja convocado": "CIENTE."
            },
            "EnviarAoPreencher":"nao",
            "EnviarAoPreencher_Botao":"Enviar"
        }
        with open(caminho_config, "w", encoding="utf-8") as f:
            json.dump(config_exemplo, f, ensure_ascii=False, indent=4)
        
        exibir_mensagem(f"Arquivo de configuração criado em '{caminho_config}'. Edite esse arquivo antes de executar novamente.", "I", "Primeira execução")
        print(f"Arquivo de configuração criado em '{caminho_config}'.")
        print("Edite esse arquivo antes de executar novamente.")
        logging.warning(f"Arquivo '{caminho_config}' criado. É necessário preencher as informações antes de continuar.")
        return None

    # Caso exista, lê o conteúdo
    try:
        with open(caminho_config, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"Erro ao ler o arquivo de configuração: {e}")
        logging.error(f"Erro ao ler o arquivo de configuração: {e}")
        return None
# ====================================================
# FIM CONFIGURAÇÕES
# ====================================================

# ====================================================
# INICIALIZAÇÃO
# ====================================================
print("=== AUTO-PREENCHIMENTO DE FORMULÁRIO ===\n")

# AVALIA ARQUIVO DE CONFIGURAÇÃO

config = verificar_config()
if not config:
    sys.exit(0)  # Encerra a execução se o arquivo for recém-criado ou inválido
    
try:
    url_padrao = config["url_padrao"]
    print("URL carregada:", url_padrao)

    #Mapeia as perguntas e respostas
    respostas = config["respostas"]    
    print("Respostas carregadas:", respostas)

    #Parâmetros de envio do formulário
    EnviarAoPreencher = config["EnviarAoPreencher"]  
    print("Enviar Automaticamente:", EnviarAoPreencher)
    EnviarAoPreencher_Botao = config["EnviarAoPreencher_Botao"]  
    print("Nome do botao para enviar:", EnviarAoPreencher_Botao)
except Exception as e:
    print(f"Erro ao carregar variáveis do arquivo de configuração: {e}.")
    logging.error(f"Erro ao carregar variáveis do arquivo de configuração: {e}.")
    exibir_mensagem(f"Erro ao carregar variáveis do arquivo de configuração: {e}. \nSalve o arquivo como backup, apague para reciar e atualize com suas informaçõe após recriação.", "E", "Arquivo de configuração")
    sys.exit(0)  # Encerra a execução se o arquivo for recém-criado ou inválido
      
# ====================================================
# FIM INICIALIZAÇÃO
# ====================================================

# ====================================================
# SOLICITA A URL
# ====================================================
# URL padrão do arquivo
url = exibir_input("AUTO-PREENCHIMENTO DE FORMULÁRIO", "Digite a URL do formulário (ou pressione Enter para usar a padrão)")
if url is None:
    sys.exit(0)  # Encerra a execução se o arquivo for recém-criado ou inválido
if not url:
    url = url_padrao
    print("Nenhuma URL informada. Usando URL padrão.")
    logging.warning("Nenhuma URL informada. Usando URL padrão.")

# ====================================================
# INICIALIZA O NAVEGADOR
# ====================================================
try:
    options = Options()
    options.add_experimental_option("detach", True)  # mantém o navegador aberto
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    print("\nFormulário aberto no navegador.")
    logging.info(f"Navegador iniciado com URL: {url}")
except Exception as e:
    print(f"\nErro ao abrir o navegador: {e}")
    logging.exception("Erro ao abrir o navegador.")
    input("Pressione Enter para sair...")
    exit()
    
# ====================================================
# CARREGAMENTO COMPLETO DA PAGINA
# ====================================================
# Faz scroll até o final da página

time.sleep(2)  # tempo para garantir que a página carregue

# ====================================================
# AGUARDA E EXECUTA AÇÕES DE PREENCHIMENTO
# ====================================================
try:
    print("\nTentando preencher campos...")
    
    #Preenche o formulário de acordo com mapeamento em repostas
    for pergunta, resposta in respostas.items():
        preencher_pergunta(driver, pergunta, resposta)
   
    #Finaliza o formulário de acordo com parâmetros
    enviar_formulario(driver, EnviarAoPreencher, EnviarAoPreencher_Botao)
    
except Exception as e:
    exibir_mensagem(f"\nOcorreu um erro durante o preenchimento. Verifique o log '{caminho_log}'.", "E", "Erro no preenchimento")
    logging.exception(f"Erro ao preencher ou enviar o formulário:'{e}'.")

# ====================================================
# ENCERRA AÇÕES
# ====================================================


# ====================================================
# ENCERRAMENTO CONTROLADO
# ====================================================
print("\nO navegador continuará aberto até você pressionar Enter.")
input("Pressione Enter para fechar o navegador e encerrar o script...")
driver.quit()
logging.info("Execução encerrada com sucesso.\n")