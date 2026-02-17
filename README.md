# LINKEDIN QUEENS BRUTEFORCE

A logic game popularized by LinkedIn where you fill the grid so that there is only one Queen per row, column, and colored region.

The queens bruteforce logic are all implemented using C, and all the input/out processing are implemented using Python. The C layer communicates to the Python layer through the Python library of ctypes.

# HOW TO BUILD & RUN

MAKE SURE you activate your VIRTUAL ENVIRONMENT for Python and install these python dependencies:
- tkinter (installed via package manager, not pip)
- Pillow
- opencv-python
- numpy

using
```bash
pip install numpy Pillow opencv-python
```
or
```bash
pip3 install numpy Pillow opencv-python
```
If you are on Linux and tkinter is not included in your Python installation, you can install it using your package manager.
Example:
```bash
sudo apt-get install python3-tk
```

After that, you can run the build&run script (buildnrun.sh for linux and buildnrun.bat for windows).

If you don't fancy using my script, you can always run the program by running
```bash
python3 queens_interface.py
```
on the bin folder.


# DOCKER ALTERNATIVE

Alternatively, you can run this project on docker using these commands

```bash
sudo docker build -t queens-solver .
```
After the image has been built, you can run it using these commands (for Linux or WSL2 of Windows 11)
```bash
sudo docker run -it --rm \
    -e DISPLAY=:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    queens-solver
```
Or if you are running docker from windows you can run it using
```bash
$IP = (Get-NetIPAddress -InterfaceAlias "vEthernet (WSL)" -AddressFamily IPv4).IPAddress
docker run -it --rm `
    -e DISPLAY=$IP:0.0 `
    -v ${PWD}:/app/data `
    queens-solver
```



THIS PROJECT IN ITS ENTIRETY IS DESIGNED AND WRITTEN BY ME (Billie Bhaskara Wibawa 13524024)
