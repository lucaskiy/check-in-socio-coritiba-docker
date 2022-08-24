#!/bin/bash

# type your cpf, digits only
export cpf=12345678900

# type your password
export coxa_password=password

# select which sector to sit, 1 for 'ARQUIBANCADA', 2 for 'MAUA'
export stadium_sector=1


docker run -ti --env cpf=$cpf --env password=$password --env stadium_sector=$stadium_sector coxa_check_in