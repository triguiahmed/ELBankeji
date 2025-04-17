FROM ollama/ollama:latest

CMD [ "ls","-al" ]
# Copy the start script and .env file
COPY . .

RUN chmod +x ./start.sh

# Set environment variables for Ollama
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_ORIGINS=*

# Set the entrypoint
ENTRYPOINT [ "./start.sh"]