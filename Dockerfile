FROM python:3.10

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    --no-install-recommends

# Install Google Chrome
RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver version 129.0.6668.70
RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.70/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver-linux64/chromedriver && \
    ln -s /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# set display port to avoid crash
ENV DISPLAY=:99

# install selenium
RUN pip install selenium==4.3.0


ADD . /home/coxa_checkin/
WORKDIR /home/coxa_checkin/

ARG COXA_CPF
ARG COXA_PASSWORD
ARG COXA_SECTOR
ARG EMAIL
ARG GMAIL_PASSWORD
ARG CHECKIN_TYPE

# install requirements.txt
RUN pip install -r requirements.txt 

CMD ["python3", "main.py"]