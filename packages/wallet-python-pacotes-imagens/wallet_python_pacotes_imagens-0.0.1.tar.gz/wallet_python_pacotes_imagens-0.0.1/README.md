<img src="https://user-images.githubusercontent.com/63436406/156398887-4b104218-95b0-494f-aca0-be81da5d14d8.png" align="left" height="150px" width="150px">
<h1>  🎲 Descomplicando a criação de pacotes de processamento de imagens em Python  </h1>
<p> Neste projeto você aprenderá a criar o seu primeiro pacote de processamento de imagens e disponibilizá-lo no repositório Pypi. Assim você pode reutilizá-lo e compartilhá-lo facilmente com outras pessoas. </p>
<br>

## Autora do Projeto: Karina Kato

### Aula: Descomplicando a criação de pacotes de processamento de imagens em Python

[(clique aqui para ver o meu perfil na plataforma)](https://web.dio.me/users/leo_albergaria)

#### Tecnologia: Python

#### Data: 02/03/2022

## Image_Processing

The package "image_processing-test" is used to:

-   Processing:
    -   Histogram matching;
    -   Structural similarity;
    -   Resize image;

-   Utils:
    -   Read image;
    -   Save image;
    -   Plot image;
    -   Plot result;
    -   Plot Histogram;

---

## Installation 

-   [x] Instalação das últimas versões de "setuptools" e "wheel"

```
py -m pip install --upgrade pip
py -m pip install --user setuptools wheel twine

py setup.py sdist bdist_wheel
```

-   [x] Tenha certeza que o diretório no terminal seja o mesmo do arquivo "setup.py"

```
py setup.py sdist bdist_wheel
```

-   [x] Após completar a instalação, verifique se as pastas abaixo foram adicionadas ao projeto:

    -   [x] build;
    -   [x] dist;
    -   [x] image_processing_test.egg-info.

-   [x] Basta subir os arquivos, usando o Twine, para o Test Pypi:

```
py -m twine upload --repository testpypi dist/*
```

-   [x] Após rodar o comando acima no terminal, será pedido para inserir o usuário e senha. Feito isso, o projeto estará hospedado no Test Pypi.hospedá-lo no Pypi diretamente.
        Use the package manager [pip](https://pip.pypa.io/en/stable/) to install package_name

```bash
pip install wallet_python_pacotes_imagens
```

## Local Installation

-   [x] Instalação de dependências

```
pip install -r requirements.txt
```

-   [x] Instalção do Pacote

Use o gerenciador de pacotes `pip install -i https://test.pypi.org/simple/ image-processing-test `para instalar image_processing-test

```bash
pip install image-processing-test
```

---
## Author
Léo Albergaria

## License
[MIT](https://choosealicense.com/licenses/mit/)

---

<p align="right">
# Hello <img src="https://acegif.com/wp-content/gifs/ola-47.gif" width="29px">
# Um pouco sobre mim #
</p>    
<p align="right">
    <a href="https://web.dio.me/users/leo_albergaria?tab=achievements">
        <img style="border-radius: 50px; height: 50px; width: 90px"
             src="https://user-images.githubusercontent.com/63436406/155859846-da9d78e9-c7c4-47ca-a95c-43fed103bd46.png"/>
    <a href="https://www.linkedin.com/in/adm-leo-albergaria/">
        <img style="border-radius: 50px; height: 50px; width: 90px"
             src="https://user-images.githubusercontent.com/63436406/155859988-26ceade2-4e04-473a-8a26-796b145a4224.png" />
    <a href="https://github.com/leo-albergaria">
        <img style="border-radius: 50px; height: 50px; width: 90px"
             src="https://user-images.githubusercontent.com/63436406/155860021-d9d51434-9fe1-4233-a70a-6b69d5f85792.png" /></a>
</p>
