FROM python:3.9-slim

RUN apt-get update && apt-get install -y git libgomp1 fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 file --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app/step3_requirement_input

COPY step3_requirement_input/ /app/step3_requirement_input/

RUN mkdir workspace && \
    pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV OPENAI_API_KEY=your_api_key_here

CMD ["/bin/bash"]