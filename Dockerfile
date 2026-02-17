FROM gcc:latest AS compiler

WORKDIR /app
COPY src/queens_logic.c .
RUN gcc -shared -o queens_logic.so -fPIC queens_logic.c

FROM python:3.9-slim
WORKDIR /app

# System dependencies for Tkinter and OpenCV
RUN apt-get update && apt-get install -y \
    python3-tk \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    numpy \
    pillow \
    opencv-python-headless

COPY --from=compiler /app/queens_logic.so .
COPY src/*.py .
COPY queen_asset.png . 
COPY input_samples/*.png .
COPY input_samples/*.txt .

CMD ["python", "queens_interface.py"]