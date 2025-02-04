import json
import time
import datetime
import sys
from time import sleep
import glob
from pprint import pprint

import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM

import questions as que

questions = que.questions

agents = [
    "null", 
    "product_manager",
    "architect",
    "project_manager",
    "engineer"
]

personalities = [
    "null",
    "OH", "OL",
    "CH", "CL",
    "EH", "EL",
    "AH", "AL",
    "NH", "NL"
]



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











def get_score(file_path):
    print(file_path)
    with open(file_path, "r") as f:
        ss = f.read()
    
    scores = json.loads(ss)

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
                if p_b=='+':
                    score_a += j * total_answer[p_a+p_b][j]
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
    return scores



def save_fig_pdf(l, file_path, index, columns, vmin=-5, vmax=5, figsize=None):
    df = pd.DataFrame(
            data=l, 
            index=index, 
            columns=columns
            )
        
    #pprint(l)
    plt.figure(figsize=figsize)
    sns.heatmap(df, cmap='bwr',annot=True, fmt=".2f", vmin=vmin, vmax=vmax)# sns.heatmap(df, cmap='RdYlBu')
    plt.savefig(f'{file_path}.svg')
    plt.close('all')
    drawing = svg2rlg(f'{file_path}.svg')
    renderPDF.drawToFile(drawing, f"{file_path}.pdf")


scores = {}


for agent in agents:
    scores[agent] = {}
    for personality in personalities:
        j_paths = [n for n in glob.glob(f'./syukei_results/*-{agent}-{personality}.json')]
        j_paths.sort()
        j_path = j_paths[-1]
        #if len(j_paths)==1:continue
        print(agent, personality)
        print(j_paths)
        print(j_path)

        scores[agent][personality] = get_score(j_path)

print(scores)




# each page : agent fix; (give_personality, test_personality)
for agent in agents:
    print(agent)


    for sgn in ['H', 'L']:
        l = [[0 for _ in range(5)] for _ in range(6)]
        for j, p_test in enumerate(['O', 'C', 'E', 'A', 'N']):
            l[0][j] = scores[agent]["null"][p_test]
        for i, p_give in enumerate(['O', 'C', 'E', 'A', 'N']):
            for j, p_test in enumerate(['O', 'C', 'E', 'A', 'N']):
                l[i+1][j] = scores[agent][p_give+sgn][p_test]
        
        save_fig_pdf(
            l, 
            f"figs/{sgn}/{agent}",
            index=["null"]+[f"give_{s}_{sgn}" for s in ['O', 'C', 'E', 'A', 'N']],
            columns=[f"test_{s}" for s in ['O', 'C', 'E', 'A', 'N']],
            vmin=1, vmax=5
        )


    for sgn in ['H', 'L']:
        l = [[0 for _ in range(5)] for _ in range(5)]
        for i, p_give in enumerate(['O', 'C', 'E', 'A', 'N']):
            for j, p_test in enumerate(['O', 'C', 'E', 'A', 'N']):
                l[i][j] = scores[agent][p_give+sgn][p_test] - scores[agent]["null"][p_test]
        
        save_fig_pdf(
            l, 
            f"figs/diff_{sgn}_null/{agent}",
            index=[f"give_{s}_{sgn}" for s in ['O', 'C', 'E', 'A', 'N']],
            columns=[f"test_{s}" for s in ['O', 'C', 'E', 'A', 'N']],
            vmin=-4, vmax=4
        )


    l = [[0 for _ in range(5)] for _ in range(5)]
    for i, p_give in enumerate(['O', 'C', 'E', 'A', 'N']):
        for j, p_test in enumerate(['O', 'C', 'E', 'A', 'N']):
            l[i][j] = scores[agent][p_give+"H"][p_test] - scores[agent][p_give+"L"][p_test]
    
    save_fig_pdf(
        l, 
        f"figs/diff_H_L/{agent}",
        index=[f"give_{s}" for s in ['O', 'C', 'E', 'A', 'N']],
        columns=[f"test_{s}" for s in ['O', 'C', 'E', 'A', 'N']],
        vmin=-4, vmax=4
    )


    
# each page : test_personality fix; (agent, give_personality)
for p_test in ['O', 'C', 'E', 'A', 'N']:

    for sgn in ['H', 'L']:
        l = [[0 for _ in range(5)] for _ in range(4)]
        for i, agent in enumerate(agents[1:]):
            for j, p_give in enumerate(['O', 'C', 'E', 'A', 'N']):
                l[i][j] = scores[agent][p_give+sgn][p_test] - scores["null"][p_give+sgn][p_test]
        save_fig_pdf(
            l, 
            f"figs/diff_a_null/give_{sgn}_test_{p_test}",
            index=agents[1:],
            columns=[f"give_{s}_{sgn}" for s in ['O', 'C', 'E', 'A', 'N']],
            vmin=-4, vmax=4,
            figsize=(12, 8)
        )
    

    l = [[0 for _ in range(11)] for _ in range(4)]
    for i, p_give in enumerate(personalities):
        for j, agent in enumerate(agents[1:]):
            l[j][i] = scores[agent][p_give][p_test] - scores["null"][p_give][p_test]
    save_fig_pdf(
        l, 
        f"figs/diff_a_null/test_{p_test}",
        index=agents[1:],
        columns=[f"give_{s}" for s in personalities],
        vmin=-4, vmax=4,
        figsize=(16, 8)
    )


    for sgn in ['H', 'L']:
        l = [[0 for _ in range(5)] for _ in range(5)]
        for i, agent in enumerate(agents):
            for j, p_give in enumerate(['O', 'C', 'E', 'A', 'N']):
                l[i][j] = scores[agent][p_give+sgn][p_test] - scores[agent]["null"][p_test]
        save_fig_pdf(
            l, 
            f"figs/diff_p_null/give_{sgn}_test_{p_test}",
            index=agents,
            columns=[f"give_{s}_{sgn}" for s in ['O', 'C', 'E', 'A', 'N']],
            vmin=-4, vmax=4,
            figsize=(12, 8)
        )
    
    l = [[0 for _ in range(10)] for _ in range(5)]
    for i, p_give in enumerate(personalities[1:]):
        for j, agent in enumerate(agents):
            l[j][i] = scores[agent][p_give][p_test] - scores[agent]["null"][p_test]
    save_fig_pdf(
        l, 
        f"figs/diff_p_null/test_{p_test}",
        index=agents,
        columns=[f"give_{s}" for s in personalities[1:]],
        vmin=-4, vmax=4,
        figsize=(16, 8)
    )






# each page : give_personality fix; (agent, test_personality)
for p_give in personalities:
    l = [[0 for _ in range(5)] for _ in range(4)]
    for i, agent in enumerate(agents[1:]):
        for j, p_test in enumerate(['O', 'C', 'E', 'A', 'N']):
            l[i][j] = scores[agent][p_give][p_test] - scores["null"][p_give][p_test]
    
    save_fig_pdf(
        l, 
        f"figs/diff_a_null/give_{p_give}",
        index=agents[1:],
        columns=[f"test_{s}" for s in ['O', 'C', 'E', 'A', 'N']],
        vmin=-4, vmax=4,
        figsize=(8, 8)
    )

for p_give in personalities[1:]:
    l = [[0 for _ in range(5)] for _ in range(5)]
    for i, agent in enumerate(agents):
        for j, p_test in enumerate(['O', 'C', 'E', 'A', 'N']):
            l[i][j] = scores[agent][p_give][p_test] - scores[agent]["null"][p_test]
    
    save_fig_pdf(
        l, 
        f"figs/diff_p_null/give_{p_give}",
        index=agents,
        columns=[f"test_{s}" for s in ['O', 'C', 'E', 'A', 'N']],
        vmin=-4, vmax=4,
        figsize=(8, 8)
    )

