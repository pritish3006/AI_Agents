# Use an official Python runtime as a parent image
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy environment file
COPY environment.yml .

# Create conda environment
RUN conda env create -f environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "genai_agents", "/bin/bash", "-c"]

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["conda", "run", "-n", "genai_agents", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 