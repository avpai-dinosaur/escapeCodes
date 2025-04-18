import pygame
import requests
import json
import threading
import time
from src.core.ecodeEvents import EventManager, EcodeEvent
import src.constants as c
import src.core.utils as utils

class LeetcodeManager:
    """Class to handle opening leetcode and detect when problems are solved."""

    lock = threading.Lock()

    def __init__(self):
        """Constructor."""
        self.startTimestamp = time.time()
        self.username = None
        self.stats = None
        self.totalSolved = 0

        self.inProgressProblems = set()

        # Event Subscribers
        EventManager.subscribe(EcodeEvent.OPEN_PROBLEM, self.on_open_problem)

    def handle_event(self, event: pygame.Event) -> None:
        """Handle events off the event queue."""
        if event.type == c.CHECK_PROBLEMS:
            apiRequestThread = threading.Thread(target=self.check_submissions, args=(self.startTimestamp,))
            apiRequestThread.start()
        elif event.type == c.USER_LOGIN:
            self.username = event.username
            self.stats = event.stats
            self.totalSolved = self.stats["totalSolved"]

    def on_open_problem(self, url):
        utils.open_url(url)
        problemSlug = utils.get_problem_slug(url)
        self.inProgressProblems.add(problemSlug)

    def check_submissions(self, lowerTimestamp: int) -> None:
        """Check the user's last 50 accepted submissions."""
        LeetcodeManager.lock.acquire_lock()
        
        url = "https://leetcode.com/graphql"
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
        
        response = requests.get(url, json=payload, headers=headers)
        recentSubmissions = json.loads(response.text)["data"]
        print(f"Getting {self.username}'s recent submissions")
        print(recentSubmissions)
        
        LeetcodeManager.lock.acquire_lock()
        
        solvedProblems = []
        if response.status_code == 200:
            for problemSlug in self.inProgressProblems:
                if self.was_problem_solved(
                    problemSlug,
                    recentSubmissions["recentAcSubmissionList"],
                    lowerTimestamp
                ): 
                    solvedProblems.append(problemSlug)
        [self.inProgressProblems.remove(p) for p in solvedProblems]
        pygame.event.post(pygame.Event(c.CHECKED_PROBLEMS))
        
        LeetcodeManager.lock.release_lock()
    
    def was_problem_solved(
        self,
        problemSlug: str,
        submissionList: list,
        lowerTimestamp: int
    ):
        """Given a list of submissions, check if the given problem was solved.
        
            problemSlug: url slug assigned to the problem by leetcode
            submissionList: list of user's recent submissions
            lowerTimestamp: time the submission should have occured after to be considered valid
        """
        for submission in submissionList:
            if (
                submission["titleSlug"] == problemSlug \
                and int(submission["timestamp"]) >= lowerTimestamp
            ):
                EventManager.emit(EcodeEvent.PROBLEM_SOLVED, problemSlug=problemSlug)
                return True
        return False
            
    def update(self):
        """Update to run each game loop."""
        pass
