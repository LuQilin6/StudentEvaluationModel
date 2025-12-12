# Requirement
As it required Google’s Tesseract-OCR Engine. we should installed them in advanced. After installing the OCR-Engine, you should install the requirements.txt via pip.
### Ubuntu
```
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

### or in Mac
```
brew install tesseract
```

### Run pip
```
pip install -r requirements.txt
```

# Usage

You could run **run.py** after installing the environment, and the model will ask you the directory of student folder. 
After selecting the folder, the code will review the application material by calling GPT-4 api (Current use professor Hao Liu's key). 
The application will generate csv_summary and Result Folder in the assigned directory to summarized the student information.
As OCR is involved, it may required 1-2 minutes to read each pdf files. 
