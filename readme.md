# COXA DOIDO SÓCIO CHECK IN

Este é um projeto feito com o objetivo de realizar o Check-in para sócios do Coritiba de maneira rápida via Docker.

Há um potencial de escabilidade para realizar o Check-in de forma automática via Kubernetes ou Airflow, mas isso fica para outra hora.

## Forma de uso

```
Clone o repositório para sua máquina e crie uma imagem utilizando o Dockerfile.

exemplo: docker build -t coxa_checkin .

*** importante ***

Após a imagem ser criada é necessário dar um "run" de forma iterativa, 
pois é utilizado alguns comandos input do python que precisam ser preenchidos.

exemplo: docker run -it coxa_checkin bash

Dentro do bash é só digitar python3 main.py e realizar o check-in
```

## Como ter certeza que o check-in foi bem sucedido

Como prova de que o check-in foi realizado, o script tira um screenshot desta etapa e salve na pasta /check-in-screenshots/ , para acessar o arquivo basta rodar o seguinte comando no terminal linux.

```
docker cp <containerId>:/file/path/within/container /host/path/target

exemplo: docker cp d0c3435cd99b:/home/coxa_checkin/check-in-screenshots/ /home/lucas/Documents/proof-check-in
```

## Bonus

Adicionei uma função para notificar por email que o check-in foi realizado com sucesso.
Porém por algum motivo essa função só funciona quando o docker é rodado em bash.