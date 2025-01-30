This is:
- A Gravity Sim
- A Fluid Sim
- A Script to Create Water Visuals
- A Script to Convert To Pixel Art
  
Library install in virtual environment instructions (INSTALL PYTHON 3.12 WITH PIP IF YOU HAVEN'T ALREADY):
- Run InstallLibraries.bat script either by double clicking or through terminal
  
Run desired script by:
- Opening a terminal
- going to the code directory -> cd C:\path\to\code\folder
- activate virtual environment with -> .venv\Scripts\activate
- run desired script with -> python NameOfScript.py
  
Usage Instructions:  
- Run desired simulation with your desired settings (change in python file)  
- You can find the barebones particle simulation in Animations\\[animation_number]\render once done  
- If it looks good, run ProcessVideo.py to make it look like water, which will use your latest animation result and save in the same directory, in Animations\\[animation_number]\render
- If you'd like to, run TurnVideoIntoPixelArt.py and paste the input path, Animations\\[animation_number]\render\processed_output_[kernalSize]\_[numColours]\_[gradientOffset].mp4 and output path, C:\any\path\you\want
