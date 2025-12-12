import time
import requests
import json
import threading
import re 
import os
from tqdm import tqdm
from utils import *


save_path = "./Result"
url = ""

headers = {
    "Content-Type": "application/json",
    "Authorization": ""
}

new_data = []

def request(system_prompt, profile):
    data = {
        "model": "gpt-4",
        "messages": [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(profile)}],
        # "max_tokens": 4096,
        "temperature": 0.0
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data)).json()
        response = response['choices'][0]['message']['content']
        time.sleep(3)
        return response
    except Exception as e:
        print(e)
        time.sleep(3)



system_prompt = "You are a interviewer who reviews the application of Master of Philosophy in Top-tier university, \
                and you are expected to analyze the user background in critical ways, be aware that you should use your background information on evaluating the school, award, publication, and worked company reputation. \
                Overall, you should provide the analysis in following steps: \
                1. categorized them into one of the following majors: Science, Engineering, Liberal Arts, Arts, Design, Business, Management, Medical \
                2. Rate the Student into the following criteria from 1 to 100, including: GPA, Math Ability, Mastery of Language, Specialty core courses, Lab courses, capstone/design project \
                , Internship, Community service, Student clubs, Major Int'l/National Competition ,College of Bachelor Degree, College of higher degree, and Referees Feedbacks. \
                It is worth noted that in Mastery of Language, the full score of IELTS is 9.0, and full score of TOEFL is 120. And in GPA, normally 3.5/4.3 are consider fair gpa, below 3 is not good enough.\
                Try to be critical on Proposed Research Plan / Vision Statement, and the project the student did, for those who don't write will recieved the score deduction on Capstone/Design project. \
                In terms of award, be aware that the Mathematical Contest in Modeling is worth noting only if it is the first price. For other competition National Competition is worth noting. \
                3. Write a short summary about the evaluation on student\n\n \
                The following are the sample response: \
                1. Major: Business (Finance and FinTech) \
                2. Rating: \
                  - GPA: 70/100 (original gpa 3.0/4.0)\
                  - Math Ability: 80/100 (Assuming based on the finance background and CFA level 2) - Mastery of Language: 65/100 (IELTS score of 6.5)\
                  - Specialty core courses: 80/100 (Master's in Finance and CFA level 2)\
                  - Lab courses: 70/100 (Experience in research projects) \
                  - Capstone/Design project: 75/100 (Research projects and publications) \
                  - Internship: 70/100 (Not explicitly mentioned but assumed from the experience) \
                  - Community service: 60/100 (Participation in University Art Troupe) \
                  - Student clubs: 75/100 (Vice President of Wings Guitar Association) \
                  - Major Int'l/National Competition: 80/100 (Third place in Mock Trading Contest) \
                  - College of Bachelor Degree: 80/100 (Shandong University of Finance and Economics) \
                  - College of higher degree: 85/100 (University of Southampton) \
                3. Summary: \
                  XXXXX "

important_keys = ["Education Background", "Awards and Professional Qualifications", 
                    "Publications", "English Language Proficiency", "Proposed Research Plan / Vision Statement", 
                    "CV", "Extracurricular Activities / Volunteer Work", "Taken Courses"]

if __name__ == '__main__':
    folder_path = input('Student Application Folder Path (the directory of the pdf path): ')
    profile_list = read_files_in_folder(folder_path)
    # correct_path = input("Do You Want To Continue? [y/n]")
    
    # print(profile_list)
    save_path = f"{folder_path}/Result"
    for profile in tqdm(profile_list):
        ID = profile["ID"]
        filtered_profile = {key: profile[key] for key in important_keys}
        response = request(system_prompt,filtered_profile)
        profile["response"] = response
        if not os.path.exists(save_path):
            # Create a new directory because it does not exist
            os.makedirs(save_path)
        with open(f'{save_path}/{ID["identity"][1]}.json', 'w') as fp:
            json.dump(profile, fp)
    read_file_list = []
    df_list = []
    save_csv_path = f"{folder_path}/csv_summary"
    for filename in os.listdir(save_path):
        # Construct absolute path to file
        file_path = os.path.join(save_path, filename)
        
        # Check if the current path is a file and not a directory
        if os.path.isfile(file_path) and ".json" in file_path:
            print(f"Found file: {filename}")
            with open(file_path, 'r') as fp:
                data = json.load(fp)
            # print(data["response"])
            decomposed_text = decompose_response(data["response"])
            decomposed_text["id"] = data["ID"]["identity"][1]
            decomposed_text["name"] = data["ID"]["identity"][0]
            # cols = decomposed_text.columns
            # cols.insert(0, cols.pop(cols.index('id')))
            # cols.insert(1, cols.pop(cols.index('name')))
            df_list.append(decomposed_text)
            # read_file_list.append(extract_student_profile(file_path))
            # If you need to read the file, you can open it here
            # with open(file_path, 'r') as file:
            #     content = file.read()
            #     # Do something with the content
            #     print(content)

    decomposed_df = pd.concat(df_list, ignore_index=True)
    cols = decomposed_df.columns.tolist()
    cols = cols[-2:] +cols[-4:-2] + cols[:-4]
    decomposed_df = decomposed_df[cols]
    if not os.path.exists(save_csv_path):
        # Create a new directory because it does not exist
        os.makedirs(save_csv_path)
    decomposed_df.to_csv(f"{save_csv_path}/summary.csv", index=False)