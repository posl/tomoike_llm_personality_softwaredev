#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio

import fire

from metagpt.roles import (
    Architect,
    Engineer,
    ProductManager,
    ProjectManager,
    QaEngineer,
)
from metagpt.team import Team


async def startup(
    idea: str,
    investment: float = 3.0,
    n_round: int = 5,
    code_review: bool = False,
    run_tests: bool = False,
    implement: bool = True,
    product_manager_personality:str = "", # [TOMOIKE EDIT]
    architect_personality:str = "", # [TOMOIKE EDIT]
    project_manager_personality:str = "", # [TOMOIKE EDIT]
    engineer_personality:str = "", # [TOMOIKE EDIT]
    qa_engineer_personality:str = "", # [TOMOIKE EDIT]
):
    """Run a startup. Be a boss."""
    print("start_up[------------------------------------")
    print(f"product_manager_personality:{product_manager_personality}")
    print(f"architect_personality:{architect_personality}")
    print(f"project_manager_personality:{project_manager_personality}")
    print(f"engineer_personality:{engineer_personality}")
    print("start_up------------------------------------]\n")

    company = Team()
    company.hire(
        [
            ProductManager(personality=product_manager_personality),
            Architect(personality=architect_personality),
            ProjectManager(personality=project_manager_personality),
        ]
    )

    # if implement or code_review
    if implement or code_review:
        # developing features: implement the idea
        company.hire([Engineer(n_borg=5, use_code_review=code_review,personality=engineer_personality)])

    if run_tests:
        # developing features: run tests on the spot and identify bugs
        # (bug fixing capability comes soon!)
        company.hire([QaEngineer(personality=qa_engineer_personality)])

    company.invest(investment)
    company.start_project(idea)
    await company.run(n_round=n_round)


def main(
    idea: str,
    investment: float = 3.0,
    n_round: int = 5,
    code_review: bool = True,
    run_tests: bool = False,
    implement: bool = True,
    idea_file:str = "", # [TOMOIKE EDIT]
    product_manager_personality:str = "", # [TOMOIKE EDIT]
    architect_personality:str = "", # [TOMOIKE EDIT]
    project_manager_personality:str = "", # [TOMOIKE EDIT]
    engineer_personality:str = "", # [TOMOIKE EDIT]
    qa_engineer_personality:str = "", # [TOMOIKE EDIT]
):
    """
    We are a software startup comprised of AI. By investing in us,
    you are empowering a future filled with limitless possibilities.
    :param idea: Your innovative idea, such as "Creating a snake game."
    :param investment: As an investor, you have the opportunity to contribute
    a certain dollar amount to this AI company.
    :param n_round:
    :param code_review: Whether to use code review.
    :return:
    """
    # <--  [TOMOIKE EDIT] 
    try:
        with open(idea_file, "r") as f:
            idea = f.read()
        print("アイデアファイルの読み込みに成功しました")
    except:
        print("アイデアを引数から読み込みます")
    
    print("main[------------------------------------")
    print(f"idea:\n{idea}")
    print(f"product_manager_personality:{product_manager_personality}")
    print(f"architect_personality:{architect_personality}")
    print(f"project_manager_personality:{project_manager_personality}")
    print(f"engineer_personality:{engineer_personality}")
    print("main------------------------------------]\n")


    asyncio.run(startup(idea, investment, n_round, code_review, run_tests, implement,
                        product_manager_personality=product_manager_personality, # [TOMOIKE EDIT]
                        architect_personality=architect_personality, # [TOMOIKE EDIT]
                        project_manager_personality=project_manager_personality, # [TOMOIKE EDIT]
                        engineer_personality=engineer_personality, # [TOMOIKE EDIT]
                        qa_engineer_personality=qa_engineer_personality # [TOMOIKE EDIT]
                        ))


if __name__ == "__main__":
    fire.Fire(main)
