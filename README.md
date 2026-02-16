# LINKEDIN QUEENS BRUTEFORCE

A logic game popularized by LinkedIn where you fill the grid so that there is only one Queen per row, column, and colored region.

# HOW TO BUILD

Make sure you activate your virtual environment for python and install these python dependancies:
- tkinter
- pillow
- opencv
- numpy


After that, you can run the build script (.sh for linux and .bat for windows).

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
