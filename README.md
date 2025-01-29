This is:  
- A Gravity Sim  
- A Fluid Sim  
- A Script to Create Water Visuals  
- A Script to Convert To Pixel Art

Virtual Environment Setup (optional, but recommended, assuming you have python installed)
- Open Terminal
- change directory to the folder of these scripts by running -> cd C:\path\to\code\folder
- run this command to create virtual environment -> python -m venv .venv
- run this command to activate the virtual environment -> .venv\Scripts\activate  

Requires Python Libraries (either in virtual environment or globally):  
-  Numpy: run -> pip install numpy  
-  Numba: run -> pip install Numba  
-  OpenCV2: run -> pip install opencv-python 

Run desired script by running -> cd C:\path\to\code\folder  
followed by -> python NameOfScript.py  

Both of the simulations run parallel on the CPU, and will save all frames in Animations/[animation number] and final video in Animations/[animation number]/render  
The ProcessVideo script will process the latest animation and save in the Animations/[animation number]/render folder  
The pixel art script will require both an input video path and output folder path  
