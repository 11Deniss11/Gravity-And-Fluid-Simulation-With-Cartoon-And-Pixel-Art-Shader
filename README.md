This is:

- A Gravity Sim
- A Fluid Sim
- A Script to Create Water Visuals
- A Script to Convert To Pixel Art

Library install in virtual environment instructions:

- Install PYTHON 3.12 with pip if you haven't already
- Open a terminal
- Go to the code directory -> $ cd C:\path\to\code\folder
- Create virtual environment in directory (recommended) -> $ python -m venv .venv
- Activate virtual environment (if applicable) -> $ .venv/scripts/activate
- Install all required libraries -> $ pip install -r requirements.txt

Run desired script by:

- Opening a terminal to the code directory
- Activate virtual environment with -> .venv\Scripts\activate
- Run desired script with -> python NameOfScript.py

Usage Instructions:

- Run desired simulation with your desired settings (change in python file)
- You can find the barebones particle simulation in Animations\\[animation_number]\render once done
- If it looks good, run ProcessVideo.py to make it look like water, which will use your latest animation result and save in the same directory, in Animations\\[animation_number]\render
- If you'd like to, run TurnVideoIntoPixelArt.py and paste the input path, Animations\\[animation_number]\render\processed*output*[kernalSize]\_[numColours]\_[gradientOffset].mp4 and output path, C:\any\path\you\want
