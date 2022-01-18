Antes de mais nada, é necessário instalar o geckodriver:
https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu

É necessŕio também realizar a instalação das libs do python (versão 3), através do requirements.txt (pip3 install -r requirements.txt)

É recomendável não executar o projeto como root, parece que o selenium não roda bem com permissão de root.

É necessário dar permissão 777 para a pasta de log: /var/log/Crawler
É necessário dar permissao 777 para a pasta do projeto, por conta do arquivo de log
geckodriver.log e o cache.

Para executar a aplicação, apenas rode o comando "python3 Api.py"
Para acompanhar o log da aplicação, execute o comando "tail -f /var/log/Crawler/YYYY/MM/DD/Crawler.log