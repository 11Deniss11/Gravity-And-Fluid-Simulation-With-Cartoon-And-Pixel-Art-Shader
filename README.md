This is:
- A Gravity Sim
- A Fluid Sim
- A Script to Create Water Visuals
- A Script to Convert To Pixel Art

Library install in virtual environment instructions:
- Run InstallLibraries.bat script either by double clicking or through terminal

Run desired script by:
- Opening a terminal
- going to the code directory -> cd C:\path\to\code\folder
- activate virtual environment with -> .venv\Scripts\activate
- run desired script with -> python NameOfScript.py

Both of the simulations run parallel on the CPU, and will save all frames in Animations/[animation number] and final video in Animations/[animation number]/render  
The ProcessVideo script will process the latest animation and save in the Animations/[animation number]/render folder  
The pixel art script will require both an input video path and output folder path
