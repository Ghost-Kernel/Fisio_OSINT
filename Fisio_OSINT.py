from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
ascii_art = """
 _____ _     _        ___  ____ ___ _   _ _____ 
|  ___(_)___(_) ___  / _ \/ ___|_ _| \ | |_   _|
| |_  | / __| |/ _ \| | | \___ \| ||  \| | | |  
|  _| | \__ \ | (_) | |_| |___) | || |\  | | |  
|_|   |_|___/_|\___/ \___/|____/___|_| \_| |_|  


⠀"""

print(ascii_art)

# Inicializar o driver
driver = webdriver.Chrome()  # ou outro driver que você esteja usando

try:
    # Acesse o site do CREFITO 2
    driver.get('https://www.crefito2.com.br/spw/consultacadastral/TelaConsultaPublicaCompleta.aspx')

    # Esperar até que o campo de tipo de busca esteja presente
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'ContentPlaceHolder1_Callbackconsulta_cboTipoBusca_I'))
    )

    # Selecionar o tipo de busca (por exemplo, "Nome")
    tipo_busca = driver.find_element(By.ID, 'ContentPlaceHolder1_Callbackconsulta_cboTipoBusca_I')
    tipo_busca.click()
    time.sleep(1)  # Esperar o dropdown carregar

    # Selecionar "Nome"
    nome_option = driver.find_element(By.XPATH, "//td[contains(text(), 'Nome')]")
    nome_option.click()

    # Perguntar ao usuário qual cidade deseja buscar
    cidade = input("Digite o nome da cidade que deseja buscar: ").strip()

    # Preencher o campo de cidade
    campo_cidade = driver.find_element(By.ID, 'ContentPlaceHolder1_Callbackconsulta_cboCidade_I')

    # Aguardar que o campo de cidade esteja visível e clicável
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'ContentPlaceHolder1_Callbackconsulta_cboCidade_I'))
    )
    
    campo_cidade.clear()  # Limpar o campo, se necessário
    campo_cidade.send_keys(cidade)  # Inserir o nome da cidade

    # Simular pressionar Enter
    campo_cidade.send_keys(Keys.RETURN)

    # Aguardar os resultados carregarem
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'dxgvDataRow_MetropolisBlue'))  # espera até que a tabela tenha dados
    )

    # Coletar os dados
    registros = []

    # Criar ou abrir o arquivo para escrita
    with open('resultados.txt', 'w', encoding='utf-8') as file:
        while True:
            # Encontrar todas as linhas da tabela de resultados
            linhas = driver.find_elements(By.CSS_SELECTOR, 'tr.dxgvDataRow_MetropolisBlue')

            for linha in linhas:
                try:
                    # Extrair os dados necessários de cada linha
                    num_registro = linha.find_element(By.CSS_SELECTOR, 'span[id*="lblnumregistro"]').text
                    nome = linha.find_elements(By.CSS_SELECTOR, 'td.letrasistema.dxgv')[1].text  # Segundo <td> é o nome
                    categoria = linha.find_element(By.CSS_SELECTOR, 'span[id*="lblcategoria"]').text
                    status = linha.find_elements(By.CSS_SELECTOR, 'td.letrasistema.dxgv')[-1].text  # Último <td> é o status

                    # Formatar a string do registro
                    registro = f"Registro: {num_registro}, Nome: {nome}, Categoria: {categoria}, Status: {status}"

                    # Adicionar o registro à lista
                    registros.append(registro)

                    # Escrever o registro no arquivo em tempo real
                    file.write(registro + '\n')
                    file.flush()  # Garantir que os dados sejam escritos imediatamente

                except Exception as inner_e:
                    print("Erro ao extrair dados da linha:", inner_e)

            # Verificar o número da página atual e total
            try:
                pagina_atual = int(driver.find_element(By.CLASS_NAME, 'dxp-num.dxp-current').text)
                total_paginas = int(driver.find_element(By.CLASS_NAME, 'dxp-lead.dxp-summary').text.split()[-1])  # "Página X de Y"
                
                # Se estamos na última página, sair do loop
                if pagina_atual >= total_paginas:
                    print("Chegamos à última página.")
                    break
                
                # Tentar clicar no botão "Próxima Página"
                proxima_pagina = driver.find_element(By.XPATH, "//a[contains(@onclick, 'GVPagerOnClick') and contains(@onclick, 'PBN')]")
                proxima_pagina.click()

                # Aguardar um momento para a nova página carregar completamente
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'dxgvDataRow_MetropolisBlue'))  # Aguardar novas linhas de dados
                )
            except Exception as e:
                print("Não foi possível verificar o número da página ou ocorreu um erro:", str(e))
                break  # Sair do loop se houver algum problema

    print("Dados salvos em 'resultados.txt'.")

except Exception as e:
    print("Ocorreu um erro:", str(e))
finally:
    driver.quit()
