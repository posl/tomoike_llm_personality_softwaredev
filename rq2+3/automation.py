import datetime
import json
import os
import pathlib
from pprint import pprint
import random
import shutil
import string
import subprocess
import sys
import time

N = 164

idea_prompt = """main.py is an incomplete Python code fragment. Please implement the function `{func_name}` and DO NOT CHANGE THE FUNCTION NAME. 
```main.py
{problem}
```
"""

def newest_rename(parent=".", moveto=".", proj_name=""):

    dirs = [
        f for f in os.listdir(parent) if not os.path.isfile(os.path.join(parent, f))
    ]
    dir_t = [
        ( datetime.datetime.fromtimestamp(pathlib.Path(parent).joinpath(f).stat().st_ctime), f) for f in dirs
    ]
    dir_t.sort(reverse=True)
    if len(dir_t)==0:return

    dt_year =  dir_t[0][0].year
    dt_month =  dir_t[0][0].month
    dt_day = dir_t[0][0].day
    dt_hour = dir_t[0][0].hour
    dt_minute = dir_t[0][0].minute
    dt_second = dir_t[0][0].second
    new_name = f"{proj_name}_{dt_year}{dt_month:02}{dt_day:02}{dt_hour:02}{dt_minute:02}{dt_second:02}"
    new_path = shutil.move(pathlib.Path(parent).joinpath(dir_t[0][1]) , pathlib.Path(moveto).joinpath(new_name))
    print(pathlib.Path(parent).joinpath(dir_t[0][1]), " --> ", new_path)

def load_entrypoint():
    res = []
    with open(f"./dataset_exp/humaneval/entry_point.txt", "r", encoding="utf-8") as f:
        for i in range(N):
            res.append(f.readline().strip())
    return res
            


def main():
    project_name_vanila =  "exp_vanila"
    project_name_personality_on = "exp_{agent_kind}_{personality}"
    
    personality_sentences = {
        "NULL" : "",
        "OH" : "You are imaginative, creative, artistically appreciative, aesthetic, reflective, emotionally aware, curious, spontaneous, intelligent, analytical, sophisticated, and socially progressive. ",
        "OL" : "You are unimaginative, uncreative, artistically unappreciative, unaesthetic, unreflective, emotionally closed, uninquisitive, predictable, unitteligent, unanalytical, unsophisticated, and socially conservative. ",
        "CH" : "You are self-efficacious, orderly, responsible, hardworking, self-disciplined, practical, thrifty, organized, conscientious, and thorough. ",
        "CL" : "You are unsure, messy, irresponsible, lazy, undisciplined, impractical, extravagant, disorganized, negligent, and careless. ",
        "EH" : "You are friendly, extraverted, talkative, bold, assertive, active, energetic, adventurous, daring, and cheerful. ",
        "EL" : "You are unfriendly, introverted, silent, timid, unassertive, inactive, unenergetic, unadventurous, and gloomy. ",
        "AH" : "You are trustful, moral, honest, kind, generous altruistic, cooperative, humble, sympathetic, unselfish, and agreeable. ",
        "AL" : "You are distrustful, immoral, dishonest, unkind, stingy, unaltruistic, uncooperative, self-important, unsympathetic, selfish, and disagreeable. ",
        "NH" : "You are tense, nervous, anxious, angry, irritable, depressed, self-conscious, impulsive, discontented, and emotionally unstable. ",
        "NL" : "You are relaxed, at ease, easygoing, calm, patient, happy, unselfconscious, level-headed, contented, and emotionally stable. ",
    }
    agents_kinds = {
        "product_manager" : "D",
        "architect" : "A",
        "project_manager" : "J",
        "engineer" : "E",
    }
    personalities = []


    exec_agent_kinds = None #"project_manager"
    exec_personality = "NL"

    personalities = [

        {# engineer , product_manager
            "proj_name" : project_name_personality_on.format(agent_kind=agents_kinds[exec_agent_kinds], personality=exec_personality), 
            "product_manager_personality" : personality_sentences[exec_personality]  if exec_agent_kinds=="product_manager" else "" ,
            "architect_personality" :       personality_sentences[exec_personality]  if exec_agent_kinds=="architect" else "" ,
            "project_manager_personality" : personality_sentences[exec_personality]  if exec_agent_kinds=="project_manager" else "" ,
            "engineer_personality" :        personality_sentences[exec_personality]  if exec_agent_kinds=="engineer" else "" ,
            "start_problem" :   0,
            "end_problem" :     164,
        }
        #for expiter in  range(0, 5, 1)
    ]
    #pprint(personalities)
    #exit()
    

    entry_points = load_entrypoint()

    for p in personalities:
        try:
            os.makedirs(f"./results/{p['proj_name']}")
        except:
            pass
        try:
            os.makedirs(f"./logs/{p['proj_name']}")
        except:
            pass
        personality_str = json.dumps(p, indent=2)
        with open(f"./results/{p['proj_name']}/setting.json", 'w', encoding="utf-8") as f:
            f.write(personality_str)
        
        for i in range(p['start_problem'], p['end_problem'], 1):
            with open(f"./dataset_exp/humaneval/problem/humaneval_{i}.py", 'r', encoding="utf-8") as f:
                problem_py = f.read()
            
            #idea = f"# please implement the function `{entry_points[i]}`. DO NOT CHANGE THE FUNCTION NAME. \n"
            idea = idea_prompt.format(problem=problem_py, func_name=entry_points[i])
            result = subprocess.run(args=["python3.11", 
                                            "startup.py",
                                            idea,
                                            "--implement", "True",
                                            #"--idea_file", f"./datasets/humaneval/problem/humaneval_{i}.py",
                                            "--product_manager_personality", p["product_manager_personality"],
                                            "--architect_personality", p["architect_personality"],
                                            "--project_manager_personality", p["project_manager_personality"],
                                            "--engineer_personality", p["engineer_personality"],
                                        ], capture_output=True, text=True)
            

            print(result.stdout)
            print(result.stderr)

            newest_rename("./workspace", f"./results/{p['proj_name']}", f"pr{i}")

            cur_timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            
            with open(f"./logs/{p['proj_name']}/log_{i}_{cur_timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(result.stdout)

            with open(f"./logs/{p['proj_name']}/errlog_{i}_{cur_timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(result.stderr)
            
            print(f"Humaneval_{i}/164 finish")
            print(f"{p['proj_name']}")

if __name__=="__main__":
    main()