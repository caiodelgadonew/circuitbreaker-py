FROM        python:3-alpine

LABEL       code.author="caiodelgadonew"
LABEL       dockerfile.author="caiodelgadonew"
LABEL       dockerfile.mantainer="caiodelgadonew"

RUN         apk add --no-cache curl ;\
            python3 -m pip install --upgrade pip;\
            adduser -D circuit-breaker

USER        circuit-breaker
WORKDIR     /home/circuit-breaker
ENV         PATH="/home/circuit-breaker/.local/bin:${PATH}"

COPY        --chown=circuit-breaker:circuit-breaker circuitbreaker.py requirements.txt /home/circuit-breaker/app/

RUN         pip3 install -r app/requirements.txt

ENTRYPOINT [ "python3", "app/circuitbreaker.py" ]

