import pygame
import requests
import json
import threading
import time
from pprint import pprint
from src.core.ecodeEvents import EventManager, EcodeEvent
import src.constants as c
import src.core.utils as utils

class LeetcodeManager:
    """Class to handle opening leetcode and detect when problems are solved."""

    lock = threading.Lock()
    graphqlEndpoint = "https://leetcode.com/graphql"

    def __init__(self):
        """Constructor."""
        self.startTimestamp = time.time()
        self.username = None
        self.stats = None
        self.inProgressProblems = set()

        # Event Subscribers
        EventManager.subscribe(EcodeEvent.OPEN_PROBLEM, self.on_open_problem)
        EventManager.subscribe(EcodeEvent.GET_PROBLEM_DESCRIPTION, LeetcodeManager.on_get_problem_description)
        EventManager.subscribe(EcodeEvent.CHECK_PROBLEMS, self.on_check_problems)

    def handle_event(self, event: pygame.Event) -> None:
        """Handle events off the event queue."""
        if event.type == c.USER_LOGIN:
            self.username = event.username
            self.stats = event.stats

    def on_open_problem(self, url):
        utils.open_url(url)
        problemSlug = utils.get_problem_slug(url)
        self.inProgressProblems.add(problemSlug)
    
    def on_get_problem_description(problemSlug):
        t = threading.Thread(
            target=LeetcodeManager.get_problem_description,
            args=(problemSlug,)
        )
        t.start()
    
    def on_check_problems(self):
        t = threading.Thread(
            target=self.check_submissions,
            args=(self.startTimestamp,)
        )
        t.start()

    def check_submissions(self, lowerTimestamp: int) -> None:
        """Check the user's last 50 accepted submissions."""
        print(f"Getting {self.username}'s recent submissions")
        
        LeetcodeManager.lock.acquire_lock()
        
        payload = {
            "query" :
                """
                query recentAcSubmissions($username: String!, $limit: Int!) {
                    recentAcSubmissionList(username: $username, limit: $limit) {
                        id
                        title
                        titleSlug
                        timestamp
                    }
                }
                """,
            "variables" : {
                "username" : self.username,
                "limit" : 50
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        LeetcodeManager.lock.release_lock()
        
        response = requests.post(
            LeetcodeManager.graphqlEndpoint,
            json=payload,
            headers=headers
        )
        recentSubmissions = json.loads(response.text)["data"]
        pprint(recentSubmissions)
        
        LeetcodeManager.lock.acquire_lock()
        
        solvedProblems = []
        if response.status_code == 200:
            for problemSlug in self.inProgressProblems:
                if LeetcodeManager.was_problem_solved(
                    problemSlug,
                    recentSubmissions["recentAcSubmissionList"],
                    lowerTimestamp
                ): 
                    solvedProblems.append(problemSlug)
        for p in solvedProblems:
            self.inProgressProblems.remove(p)
        
        LeetcodeManager.lock.release_lock()
    
    def get_problem_description(problemSlug: str) -> None:
        """Given a problem slug, get the problem's description.
        
            problemSlug: url slug assigned to the problem by leetcode
        """
        payload = {
            "query":
                """
                query questionContent($titleSlug: String!) {
                    question(titleSlug: $titleSlug) {
                        content
                    }
                }
                """,
            "variables": {
                "titleSlug": problemSlug
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            LeetcodeManager.graphqlEndpoint,
            json=payload,
            headers=headers
        )
        print(f"Getting problem description for {problemSlug}")

        if response.status_code == 200:
            data = json.loads(response.text)
            if "data" in data:
                problemDescription = data["data"]["question"]["content"]
                pygame.event.post(
                    pygame.Event(
                        c.PROBLEM_DESCRIPTION,
                        {"slug": problemSlug, "html": problemDescription}
                    )
                )
            else:
                print("\tError: No data returned")
                return None
        else:
            print(f"\tError: {response.status_code}")

    def was_problem_solved(
        problemSlug: str,
        submissionList: list,
        lowerTimestamp: int
    ) -> bool:
        """Given a list of submissions, check if the given problem was solved.
        
            problemSlug: url slug assigned to the problem by leetcode
            submissionList: list of user's recent submissions
            lowerTimestamp: time the submission should have occured after to be considered valid
        """
        for submission in submissionList:
            print(submission, lowerTimestamp)
            if (
                submission["titleSlug"] == problemSlug \
                and int(submission["timestamp"]) >= lowerTimestamp
            ):
                EventManager.emit(EcodeEvent.PROBLEM_SOLVED, problemSlug=problemSlug)
                return True
        return False
