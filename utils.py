import pdfplumber
import os
import json
from PIL import Image
import pandas as pd
# import cv2
# import pytesseract
from pdf2image import convert_from_path
import numpy as np
from tqdm import tqdm
import time
import base64
import urllib
import requests
from io import BytesIO
import re
# ReadPDF

#API KEY used for baidubce
API_KEY = ""
SECRET_KEY = ""
def get_access_token():

    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def call_ocr_api(img):
    #Wenshuo
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token=" + get_access_token()

    payload=f'image={get_file_content_as_base64(img)}&detect_direction=false&paragraph=false&probability=false'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()  # Raise an HTTPError if the response was an HTTP error
            time.sleep(2)
            refined_text = [x["words"] for x in response.json()["words_result"]]
            return refined_text
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            if attempt < max_attempts:
                time.sleep(60)  # wait for 1 minute before retrying
    # response = requests.request("POST", url, headers=headers, data=payload)
    # # print(response)
    time.sleep(2)
    # print(response.text)
    return f"No data"


def get_file_content_as_base64(img):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded 
    :return: base64编码信息
    """
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    content = base64.b64encode(buffered.getvalue()).decode("utf8")
    content = urllib.parse.quote_plus(content)
    # print(content)
    return content


def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

def extract_text_from_image(image):
    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
    return text


def findnth(haystack, needle, n):
    parts= haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)

def transform_award(profile):
    award_list_text = profile.split("Award Name / Title")
    award_list = []
    for i, award_text in enumerate(award_list_text[1:]):
        award = {}
        award["Title"] = award_text.split("\n")[0]
        award["Description"] = award_text.split("Details of the Award")[1].split("Basis of Award")[0]
        award_list.append(award)
    return award_list

def transform_work(profile):
    # print(profile)
    work_list_text = profile.split("Type")
    work_list = []
    for i, award_text in enumerate(work_list_text[1:]):
        award = {}
        if "Position Held /" in award_text:
            position=award_text.split("Position Held /")[1].split("\n")[0]
        else:
            position="MISSINGPOS"
            print("Position keyword missing")

        if "Period" in award_text:
            duration=award_text.split("Period")[1].split("\n")[0]
        else:
            duration="MISSINGDURATION"
            print("Duration keyword missing")

        if "Job Duties / Training Areas" in award_text:
            description=award_text.split("Job Duties / Training Areas")[1]
        else:
            description="MISSINGDESCRIPTION"
            print("Description keyword missing")

        if "Name of Organization" in award_text:
            organization=award_text.split("Name of Organization")[1].split("Country / Region")[0]
        else:
            organization="MISSINGORGANIZATION"
            print("Organization keyword missing")

        award["Title"] = position + " " + award_text.split("\n")[0] + " in " + organization
        award["Duration"] = duration
        award["Description"] = description
        work_list.append(award)
    return work_list


def extract_student_profile(pdf_path):

    section_titles = [
        "Public Examination Results",
        "English Language Proficiency",
        "Awards and Professional Qualifications",
        "Extracurricular Activities / Volunteer Work",
        "Work Experience / Internship / Training",
        "Publications",
        "Proposed Research Plan / Vision Statement",
        "Additional Information",
        "Supporting Documents",
        "/ CV",
        # "Reference Report",
    ]
    #possible keyword in CV, all should be written in lower case
    CV_tiles=[
        "cv",
        "curriculum vitae",
        "resume",
    ]

    sections_content = {title: "" for title in section_titles}
    sections_content["Education Background"] = {}
    extracted_text = []
    read_transcript_flag = 0
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if i == 0:
                # identity = (page.extract_table()[0][1].split("\n")[0], pdf_path.split("_")[0].split("-")[-1])
                identity = (page.extract_table()[0][1].split("\n")[0], pdf_path.split("\\")[-1][:11])
                # print(page.extract_table()[3])
                date_of_birth = page.extract_table()[3][1]
            elif i == 1:
                add_text = ""
                education_text = page.extract_text().split("Education Background")[1]
                if "Public Examination" not in education_text:
                    add_text = pdf.pages[i+1].extract_text().split("Public Examination")[0]
                education_text += add_text
            elif ("/ Official transcript" in page_text or "/\nOfficial\ntranscript" in page_text) and read_transcript_flag<4:
                read_transcript_flag = read_transcript_flag+1
                print(f"Official transcript is in page {i}")
                trans_image = pdf.pages[i].to_image(resolution=200).original
                transcript_text = call_ocr_api(trans_image)
                extracted_text.append(transcript_text)
            # if "Official transcript" in page.extract_text()[:100]:
            #     print(f"page: {i} is official transcript")
        sections_content["ID"] = {"identity": identity, "date_of_birth": date_of_birth}
        sections_content["Education Background"] = education_text
        sections_content["Taken Courses"] = extracted_text
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            try:
                text = page.extract_text()
                full_text += text + "\n\n"
            except:
                print(f"cannot read page {i}")
                continue


    # List of keywords to search for each category. These would need to be adjusted for different formats.
    for title in section_titles:
        # Find the start of the section by title

        if title == "/ CV":
            #find the text in Supporting Documents - Other documents
            otherDocumentText=full_text.split("II. Other documents")[1].split("Payment and Submission")[0]
            otherDocumentTextLower=otherDocumentText.lower()
            startCVPattern=r'\n\d+ ' #the pattern before cv's name, usually \n+series of number+" ", like "\n123 "
            endCVPattern=r' \d{2}/\d{2}/\d{4}' #the pattern after cv's name, usually dd/mm/yyyy, like "27/06/2023"
            cvRealTitle=None

            #Find the cv real title
            for cvTitle in CV_tiles:
                if cvTitle in otherDocumentTextLower:
                    CVKeywardIDX=otherDocumentTextLower.find(cvTitle)+len(cvTitle)
                    # seperate the line before and after the keyword
                    cvTitleLineBefore=otherDocumentTextLower[:CVKeywardIDX]
                    cvTitleLineAfter=otherDocumentTextLower[CVKeywardIDX:]

                    #find the keyword before and after CV's title
                    startCVTitle=re.findall(startCVPattern,cvTitleLineBefore)
                    endCVTitle=re.findall(endCVPattern,cvTitleLineAfter)

                    #index of CV title
                    if len(startCVTitle) == 0:
                        continue
                    else:
                        startCVTitleIDX=cvTitleLineBefore.rfind(startCVTitle[-1])+len(startCVTitle[-1])

                    if len(endCVTitle) == 0:
                        continue
                    else:
                        endCVTitleIDX=CVKeywardIDX+cvTitleLineAfter.find(endCVTitle[0])

                    cvRealTitle=otherDocumentText[startCVTitleIDX:endCVTitleIDX]
                    break #only find the first cv name

            if cvRealTitle != None:
                start_idx = findnth(full_text, f"{identity[0].replace(' ', ', ',1)} / {cvRealTitle}", 0)
            else:
                start_idx=-1
        else:
            start_idx = full_text.find(title)

        # If the title is not found, continue to the next title
        if start_idx == -1:
            continue
        # Find the end of the section, which is either the start of the next section or the end of the document
        if title == "/ CV":
            #temp_idx is the end of the title
            temp_idx = start_idx+len(f"{identity[0].replace(' ', ', ', 1)} / {cvRealTitle}")

            #Get all CV pages
            while full_text[temp_idx:].find(f"{identity[0].replace(' ', ', ', 1)} / {cvRealTitle}") != -1:
                temp_idx=temp_idx+full_text[temp_idx:].find(f"{identity[0].replace(' ', ', ', 1)} / {cvRealTitle}")+len(f"{identity[0].replace(' ', ', ', 1)} / {cvRealTitle}")

            #Only get 1 CV pages
            # while findnth(full_text[temp_idx:], f"{identity[0].replace(' ', ', ', 1)} / {cvRealTitle}", 0) == -1: #Only replace the first space. The format is Last name, First name
            #     temp_idx = findnth(full_text[temp_idx:], f"{identity[0].replace(' ', ', ',1)} / {cvRealTitle}", 0)

            end_idx = min([full_text.find(f"/ {identity[1]}", temp_idx + 1)] + [len(full_text)])
        else:
            end_idx = min([full_text.find(t, start_idx + 1) for t in section_titles if full_text.find(t, start_idx + 1) != -1] + [len(full_text)])
        # Extract the content for this section
        sections_content[title] = full_text[start_idx:end_idx].strip()

    sections_content["Awards and Professional Qualifications"] = transform_award(sections_content["Awards and Professional Qualifications"])
    sections_content["Work Experience / Internship / Training"] = transform_work(sections_content["Work Experience / Internship / Training"])
    important_keys = ["ID", "Education Background", "Awards and Professional Qualifications",
                    "Publications", "English Language Proficiency", "Proposed Research Plan / Vision Statement",
                    "/ CV", "Extracurricular Activities / Volunteer Work", "Taken Courses"]
    filtered_profile = {key: sections_content[key] for key in important_keys}

    #if the CV doesn't exist, it will be replaced by "Work Experience / Internship / Training"
    if filtered_profile["/ CV"] == "":
        filtered_profile["/ CV"]=sections_content["Work Experience / Internship / Training"]
    return filtered_profile

def read_files_in_folder(folder_path):
    # Iterate through all files in the specified folder
    read_file_list = []
    for filename in tqdm(os.listdir(folder_path)):
        # Construct absolute path to file
        file_path = os.path.join(folder_path, filename)

        # Check if the current path is a file and not a directory
        if os.path.isfile(file_path) and ".pdf" in file_path:
            print(f"Found file: {filename}")
            profile = extract_student_profile(file_path)
            profile["Proposed Research Plan / Vision Statement"] = profile["Proposed Research Plan / Vision Statement"][:10000]
            if len(json.dumps(profile)) > 20000:
                print(f"warning: {filename}, string len: {len(json.dumps(profile))}")
            read_file_list.append(profile)
            # If you need to read the file, you can open it here
            # with open(file_path, 'r') as file:
            #     content = file.read()
            #     # Do something with the content
            #     print(content)
    return read_file_list

# Call the function and pass the path to the PDF file
def read_files_in_folder(folder_path):
    # Iterate through all files in the specified folder
    read_file_list = []
    for filename in os.listdir(folder_path):
        # Construct absolute path to file
        file_path = os.path.join(folder_path, filename)

        # Check if the current path is a file and not a directory
        if os.path.isfile(file_path) and ".pdf" in file_path:
            print(f"Found file: {filename}")
            profile = extract_student_profile(file_path)
            profile["Proposed Research Plan / Vision Statement"] = profile["Proposed Research Plan / Vision Statement"][:5000]
            if len(json.dumps(profile)) > 20000:
                print(f"warning: {filename}, string len: {len(json.dumps(profile))}")
            read_file_list.append(profile)
            # If you need to read the file, you can open it here
            # with open(file_path, 'r') as file:
            #     content = file.read()
            #     # Do something with the content
            #     print(content)
    return read_file_list



def decompose_response(response):
    sections = response.strip().split('\n\n')

    # Initialize lists to store data
    major = None
    ratings = {}
    summary = None

    # Loop through each line and extract data
    for section in sections:
        lines = section.strip().split('\n')
        if 'Major' in lines[0]:
            major = lines[0].split(': ')[1].split('(')[0]
        if 'Rating' in lines[0]:
            for line in lines[1:]:
                category, score_and_des = line.split(':')[0], line.split(':')[-1]
                category = category.strip()
                score = score_and_des.split('(')[0].strip().split('/')[0]
                try:
                    description = score_and_des.split('(')[1].split(')')[0]
                except:
                    description = ""
                try:
                    score = float(score)
                except ValueError:
                    score = -1
                ratings[category] = score
                ratings[category + "_description"] = description
        elif 'Summary' in lines[0]:
            summary = ' '.join(lines[1:]).strip()

    # Create a dataframe
    df = pd.DataFrame(ratings, index=[0])

    # Add Major column
    df['Major'] = major
    df["Summary"] = summary
    return df