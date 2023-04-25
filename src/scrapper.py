# Importación de librerias
from datetime import datetime
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import pandas as pd


# Función que crea el Web driver
def set_driver():
    global driver
    driver = uc.Chrome(use_subprocess=True)

# Función para exportar un diccionario a un CSV externo
def to_csv(dictionary, file_name):
    pd.DataFrame(dictionary).to_csv(file_name, index=False)

# Función para aceptar las cookies
def aceptar_cookies():
    driver.find_element(By.CSS_SELECTOR, 'button#didomi-notice-agree-button').click()

# Función para extraer todas los links de las provincias disponibles
def extraer_provincias(url):
    driver.get(url)
    aceptar_cookies()
    provinces_div = driver.find_element(By.CLASS_NAME, 'seolinks')
    # se excluyen los subitems para no repetir viviendas
    provinces = provinces_div.find_elements(By.CSS_SELECTOR, 'a.seolinks-zones-item:not(.seolinks-zones-subitem)')
    results = {}
    for province in provinces:
        results[province.text] = {
            "url": province.get_attribute('href'),
        }
    print(results)
    return results

# Función recursiva para extraer la información de cada vivienda de los enlaces de las provincias
def extraer_apartamentos(url, zona):
    driver.get(url)
    article_nodes = driver.find_elements(By.CSS_SELECTOR, 'div.ad-preview')
    apartments=[]
    for article in article_nodes:
        apartment={}
        try:
            apartment['titulo']=article.find_element(By.CSS_SELECTOR, 'a.ad-preview__title').text
            apartment['url']=article.find_element(By.CSS_SELECTOR, 'a.ad-preview__title').get_attribute('href')
            apartment['zona']=zona
            apartment['dirección']=article.find_element(By.CSS_SELECTOR, 'p.p-sm').text
            apartment['precio'] = article.find_element(By.CSS_SELECTOR, 'span.ad-preview__price').text
            detalles_nodes= article.find_elements(By.CSS_SELECTOR, 'p.ad-preview__char.p-sm')
            detalles=[]
            for detalle in detalles_nodes:
                detalles.append(detalle.text)
            apartment['detalles']= detalles
            apartment['descripcion'] = article.find_element(By.CSS_SELECTOR, 'p.ad-preview__description').text
            apartment['fecha extraccion']=datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            print(apartment)
        except:
            pass
        apartments.append(apartment)
    # Verifica si hay un botón de paginación y si lo hay lo recorre
    if driver.find_elements(By.CLASS_NAME, "pagination__next"):
        button = driver.find_element(By.CLASS_NAME, "pagination__next")
        url = button.find_element(By.TAG_NAME, "a").get_attribute("href")
        apartments += extraer_apartamentos(url, zona)
    return apartments

def main():
    set_driver()
    print(f'User agent used is :{driver.execute_script("return navigator.userAgent;")}')
    provincias =extraer_provincias("https://www.pisos.com/alquiler_viviendas/")
    result= []
    for provincia in provincias.keys():
        result+= extraer_apartamentos(provincias[provincia]['url'], provincia)
    to_csv(result,"../output/apartamentos.csv")

if __name__ == "__main__":
    main()
