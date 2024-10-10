# COXA DOIDO SÓCIO CHECK IN

Este é um projeto feito com o objetivo de realizar o Check-in para sócios do Coritiba de maneira rápida via Docker.

O projeto foi todo feito em python utilizando a bibilioteca `Selenium`.

Sua função é logar na página de sócios do Coritiba, e o check-in para o próximo jogo, podendo selecionar o setor no estádio (Arquibancada ou Mauá) e o formato do check-in (carteirinha ou qr code).

Caso tenha interesse, uma confirmação do Check-in é enviada via email com um screenshot com um comprovante, mais informações abaixo.

## Como executar o script

Caso não queira a notificação via email é necessário comentar o arquivo main.py das linhas 61 até 65.
Caso queira a notificação por email alguns passos são necessários antes de rodar o build, mais informações na próxima sessão.

Clone o repositório para sua máquina e crie uma imagem utilizando o Dockerfile.

```
docker build -t coxa_checkin .
```

Finalmente, para executar o script de check-in basta rodar o comando de docker run abaixo com os argumentos preenchidos com suas informações.
```
docker run -e EMAIL=$EMAIL -e COXA_CPF=$COXA_CPF -e COXA_PASSWORD=$COXA_PASSWORD -e COXA_SECTOR=$COXA_SECTOR -e CHECKIN_TYPE=$CHECKIN_TYPE -e GMAIL_PASSWORD=$GMAIL_PASSWORD coxa-checkin
```

Outra opção de execução é utilizando o shell script checkin.sh, basta preencher as variáveis com suas informações e executar o script

```
sh checkin.sh
```


## Como adicionar o email para notificação

Como prova de que o check-in foi realizado, o script tira um screenshot do check-in e o encaminha via email.

Para receber esse email, é necessário criar uma senha de aplicativo no Gmail para utilizar como senha, entre no link abaixo e gere sua senha.

https://myaccount.google.com/apppasswords

## O que são as variáveis necessárias para executar o script

- COXA_CPF: O seu CPF para logar na página de sócio do Coritiba
- COXA_PASSWORD: A sua senha para logar na página de sócio do Coritiba
- COXA_SECTOR: O setor do estádio para se fazer o check-in, as opções são arquibancada ou mauá
- CHECKIN_TYPE: Como gostaria de realizar seu check-in, as opções são fisica (carteirinha) or online (qr code)
- EMAIL: email para receber a notificação
- GMAIL_PASSWORD: senha do APP do google