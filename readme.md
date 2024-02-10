In order to run this website, first open file lip_reading_application_on_google_colab.ipynb on Google Colab with GPU. Then, replace <ngrok authtoken> with an authtoken obtained from the ngrok dashboard. After that, run all cells to start the website. You can access the website through the generated ngrok url.

## Structure of this repository:
```bash
    |   .gitignore
    |   .gitmodules
    |   app.py
    |   benchmark-infer-test.ipynb
    |   benchmark_GRID_eval.ipynb
    |   clip1.mp4
    |   clip2.mp4
    |   flask_log.log
    |   lip_reading_application_on_google_colab.ipynb
    |   main.py
    |   readme.md
    |   requirements.txt
    |   
    +---static
    |       script.js
    |       style.css
    |       
    \---templates
            index.html
```
- The source code for frontend is in the static folder and the templates folder.
- The source code for backend is in the main.py file.
- The deployment on Google Colab is in the lip_reading_application_on_google_colab.ipynb file.

## Acknowledgements

This repository uses code from [Visual Speech Recognition for Multiple Languages](https://github.com/mpc001/Visual_Speech_Recognition_for_Multiple_Languages)
