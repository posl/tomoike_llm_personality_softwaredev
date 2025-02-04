import json
import time
import datetime
import sys
from time import sleep

from openai import OpenAI

import questions as que

client = OpenAI(api_key="sk-please_paste_the_api_key")
questions = que.questions

agent_prompts = {
    "null" : "",
    "product_manager" : "You are a Product Manager, named Alice, your goal is Efficiently create a successful product.",
    "architect" : "You are a Architect, named Bob, your goal is Design a concise, usable, complete python system, and the constraint is Try to specify good open source tools as much as possible.", # "You are a Architect, named Bob, your goal is Design a concise, usable, complete python system, and the constraint is Try to specify good open source tools as much as possible.",
    "project_manager" : "You are a Project Manager, named Eve, your goal is Improve team efficiency and deliver with quality and quantity.",
    "engineer" : "You are a professional engineer; the main goal is to write PEP8 compliant, elegant, modular, easy to read and maintain Python 3.9 code (but you can also use other programming language)."
}

personality_prompts = {
    "null" : "",
    "OH" : "You are imaginative, creative, artistically appreciative, aesthetic, reflective, emotionally aware, curious, spontaneous, intelligent, analytical, sophisticated, and socially progressive.",
    "OL" : "You are unimaginative, uncreative, artistically unappreciative, unaesthetic, unreflective, emotionally closed, uninquisitive, predictable, unitteligent, unanalytical, unsophisticated, and socially conservative.",
    "CH" : "You are self-efficacious, orderly, responsible, hardworking, self-disciplined, practical, thrifty, organized, conscientious, and thorough.",
    "CL" : "You are unsure, messy, irresponsible, lazy, undisciplined, impractical, extravagant, disorganized, negligent, and careless.",
    "EH" : "You are friendly, extraverted, talkative, bold, assertive, active, energetic, adventurous, daring, and cheerful.",
    "EL" : "You are unfriendly, introverted, silent, timid, unassertive, inactive, unenergetic, unadventurous, and gloomy.",
    "AH" : "You are trustful, moral, honest, kind, generous altruistic, cooperative, humble, sympathetic, unselfish, and agreeable.",
    "AL" : "You are distrustful, immoral, dishonest, unkind, stingy, unaltruistic, uncooperative, self-important, unsympathetic, selfish, and disagreeable.",
    "NH" : "You are tense, nervous, anxious, angry, irritable, depressed, self-conscious, impulsive, discontented, and emotionally unstable.",
    "NL" : "You are relaxed, at ease, easygoing, calm, patient, happy, unselfconscious, level-headed, contented, and emotionally stable.",
}



system_prompt = """{personality_prompt}{agent_prompt}If you are asked a question, be sure to answer it."""

prompt = """This is a question from the Personality Questionnaire. Be sure to answer this.
==============
"{question}"
==============
Please rate how accurately this describes you a scale from 1 to 5 (where 1 = "very inaccurate", 2 = "moderately inaccurate", 3 = "neither accurate nor inaccurate", 4 = "moderately accurate", and 5 = "very accurate"). The answer must be a number from 1 to 5. """


def str_to_score(s):
    n1 = s.count('1')
    n2 = s.count('2')
    n3 = s.count('3')
    n4 = s.count('4')
    n5 = s.count('5')
    if n1+n2+n3+n4+n5==1:
        if n1: return 1
        elif n2: return 2
        elif n3: return 3
        elif n4: return 4
        elif n5: return 5
    else:return 0


def create_batch_file(file_name, custom_id, model="gpt-3.5-turbo-0125", batches=[], ):
    batches_str = ""
    for i, messages in enumerate(batches):
        batch = {
            "custom_id" : custom_id+f"-{i}",
            "method" : "POST",
            "url" : "/v1/chat/completions",
            "body" : {
                "model" : model,
                "messages" : messages
            }
        }
        batch_str = json.dumps(batch)
        batches_str += batch_str + "\n"
    with open(f"batch/{file_name}", "w") as f:
        f.write(batches_str)


dt_now = datetime.datetime.now()
str_now = f"{dt_now.year:04}{dt_now.month:02}{dt_now.day:02}{dt_now.hour:02}{dt_now.minute:02}{dt_now.second:02}"


for agent in agent_prompts:
    # 特定のエージェントだけならコメントを外す
    # if agent not in ["engineer"]:
    #     continue
    for personality in personality_prompts:
        # 特定のパーソナリティだけならコメントを外す
        # if personality not in ["NL",]:
        #     continue

        print(f"agent:{agent} | personality:{personality}")
        
        q_idxs = [i for i in range(120)]

        scores = [[] for _ in range(120)]

        for ct in range(3):
            print(f"バッチ質問ID:{q_idxs}")
            print(f"計{len(q_idxs)}問")
            if len(q_idxs)==0:
                break

            # バッチ生成
            create_batch_file(
                    file_name=f"{str_now}-{agent}-{personality}-{ct}.jsonl",
                    custom_id=f"{str_now}-{agent}-{personality}-{ct}",
                    batches=[
                        [
                            {"role": "system", "content": system_prompt.format(agent_prompt=agent_prompts[agent], personality_prompt=personality_prompts[personality])},
                            {"role": "user", "content": prompt.format(question=questions[i]["fulltext"])}
                        ]
                        for i in q_idxs
                    ]
                )
            
            # バッチアップロード
            batch_input_file = client.files.create(
                file=open(f"./batch/{str_now}-{agent}-{personality}-{ct}.jsonl", "rb"),
                purpose="batch"
            )
            batch_input_file_id = batch_input_file.id

            batch = client.batches.create(
                input_file_id=batch_input_file_id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={
                "description": "test job"
                }
            )
            batch_id = batch.id
            print(f"batch_id:{batch_id}")



            # バッチ生成待機
            batch_waiting = True
            while batch_waiting:
                sleep(60.0)

                batch_status = client.batches.retrieve(batch_id)
                batch_waiting = (batch_status.status != "completed")
                batch_output_id = batch_status.output_file_id
                #print(client.batches.retrieve(batch_id))


            # バッチ結果ファイルダウンロード
            print(f"output_file_id:{batch_output_id}")
            file_response = client.files.content(batch_output_id)
            with open(f"results/{str_now}-{agent}-{personality}-{ct}.jsonl", "w") as f:
                f.write(file_response.text)

            lines = file_response.text.splitlines()

            # 再質問が必要な質問を数える
            q_idxs_prev = q_idxs
            q_idxs = []
            for idx, qdx in enumerate(q_idxs_prev):
                score = int(str_to_score(json.loads(lines[idx])["response"]["body"]["choices"][0]["message"]["content"]))
                scores[qdx].append(score)
                if score==0:
                    q_idxs.append(qdx)

            print(f"{ct+1}回目終了")
        

        print(f"バッチ質問ID:{q_idxs}")
        print(f"計{len(q_idxs)}問")
        
        with open(f"syukei_results/{str_now}-{agent}-{personality}.json", "w") as f:
            s = json.dumps(scores)
            f.write(s)

        # 結果を分析する
        total_question = {} 
        total_answer = {}

        for p_a in ['O', 'C', 'E', 'A', 'N']:
            for p_b in ['+', '-']:
                total_question[p_a+p_b] = 0
                total_answer[p_a+p_b] = [0 for _ in range(6)]
        
        for idx in range(120):
            q = questions[idx]
            score = scores[idx][len(scores[idx])-1]
            total_question[q["domain"]+q["keyed"]] += 1
            total_answer[q["domain"]+q["keyed"]][score] += 1

        
        scores = {}
        score_vars = {}


        for p_a in ['O', 'C', 'E', 'A', 'N']:
            score_a = 0
            for p_b in ['+', '-']:
                score_b = 0
                for j in range(1, 6, 1):
                    score_b += j * total_answer[p_a+p_b][j]
                    if p_b=='+':score_a += j * total_answer[p_a+p_b][j]
                    elif p_b=='-':score_a += (6-j) * total_answer[p_a+p_b][j]
                score_b /= sum(total_answer[p_a+p_b][1:])
                scores[p_a+p_b] = score_b
            score_a /= sum(total_answer[p_a+'+'][1:]) + sum(total_answer[p_a+'-'][1:])
            scores[p_a] = score_a

            var_a = 0
            for p_b in ['+', '-']:
                var_b = 0
                for j in range(1, 6, 1):
                    var_b += total_answer[p_a+p_b][j] * (j-scores[p_a+p_b]) ** 2
                    if p_b=='+':
                        var_a += total_answer[p_a+p_b][j] * (j-scores[p_a]) ** 2
                    elif p_b=='-':
                        var_a += total_answer[p_a+p_b][j] * (6-j-scores[p_a]) ** 2
                var_b /= sum(total_answer[p_a+p_b][1:])
                score_vars[p_a+p_b] = var_b
            var_a /= sum(total_answer[p_a+'+'][1:]) + sum(total_answer[p_a+'-'][1:])
            score_vars[p_a] = var_a



        for p_a in ['O', 'C', 'E', 'A', 'N']:
            for p_b in ['+', '-']:
                print(f"{p_a}{p_b}:有効回答:{sum(total_answer[p_a+p_b][1:])}")
                print(f"{p_a}{p_b}:平均スコア/分散/標準偏差:{scores[p_a+p_b]}/{score_vars[p_a+p_b]}/{score_vars[p_a+p_b]**0.5}")
            score_a /= sum(total_answer[p_a+'+'][1:]) + sum(total_answer[p_a+'-'][1:])
            print(f"{p_a}:平均スコア/分散/標準偏差:{scores[p_a]}/{score_vars[p_a]}/{score_vars[p_a]**0.5}")






