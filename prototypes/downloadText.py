from enum import Enum

GREEN_START = "\033[92m"
RED_START = "\033[31m"
BLUE_START = "\033[34m"
END_COLOR = "\033[0m" 

class Pseudocode:
    def __init__(self, lines, missingLines):
        self.lines = lines
        self.missingLines = set(missingLines)
        for line in missingLines:
            assert line < len(self.lines)

    @staticmethod
    def anonymize_line(line):
        res = ""
        for c in line:
            if c == "\t":
                res += c
            else:
                res += "*"
        return res

    def reveal_line(self, phrase):
        for idx, line in enumerate(self.lines):
            if phrase in line and idx in self.missingLines:
                self.missingLines.remove(idx)

    def print_code(self):
        embellishedLines = self.lines.copy()
        for line in self.missingLines:
            embellishedLines[line] = Pseudocode.anonymize_line(self.lines[line])
        print("\n--- PSEUDOCODE ---")
        print("\n".join(embellishedLines))
        print()


class DownloadableText:
    PhraseStartWord = "STARTPHRASE"
    PhraseEndWord = "ENDPHRASE"

    def __init__(self, text):
        self.phrases = []
        self.lines = []
        self.words = []
        wordIdx = 0
        currentPhrase = None

        for line in text.split("\n"):
            self.lines.append([])
            for word in line.split():
                if word == DownloadableText.PhraseStartWord:
                    if currentPhrase is not None:
                        raise ValueError("Attempted to start new phrase before closing current one")
                    currentPhrase = [wordIdx]
                elif word == DownloadableText.PhraseEndWord:
                    if currentPhrase is None:
                        raise ValueError("Attempted to close phrase before starting one")
                    currentPhrase.append(wordIdx)
                    self.phrases.append(currentPhrase.copy())
                    currentPhrase = None
                else:
                    self.lines[-1].append(word)
                    self.words.append(word)
                    wordIdx += 1

    def get_phrase(self, wordIdx):
        for phrase in self.phrases:
            if phrase[0] <= wordIdx < phrase[1]:
                return phrase
        return None

    def try_probe(self, wordIdx):
        phrase = self.get_phrase(wordIdx)
        if phrase is not None:
            return " ".join(self.words[phrase[0]:phrase[1]])
        return None

    def print_text(self):
        print("\n--- TERMINAL TEXT ---")
        print("\n".join([" ".join(line) for line in self.lines]))
    
    def print_text_with_indices(self):
        print("\n--- TERMINAL TEXT ---")
        idx = 0
        for line in self.lines:
            line_display = []
            for word in line:
                line_display.append(f"{word}{BLUE_START}({idx}){END_COLOR}")
                idx += 1
            print(" ".join(line_display))
        print()


class Problem:
    class ViewState(Enum):
        Pseudocode = 0
        Terminal = 1

    def __init__(self, name, url, pseudocode, terminals):
        self.name = name
        self.url = url
        self.pseudocode = pseudocode
        self.terminals = terminals
        self.active_terminal = 0
        self.viewState = Problem.ViewState.Pseudocode

    def draw(self):
        if self.viewState == Problem.ViewState.Pseudocode:
            self.draw_problem_view()
        else:
            self.draw_terminal_view()
    
    def get_player_input(self):
        if self.viewState == Problem.ViewState.Pseudocode:
            self.get_input_problem_view()
        else:
            self.get_input_terminal_view()

    def draw_problem_view(self):
        print("\n---DIRECTIONS---")
        print(f"Complete the pseudocode for ({self.name}) by looking through the terminals for missing snippets")
        print(f"View problem description at {self.url}")
        self.pseudocode.print_code()
        print("Options:")
        print("1. Toggle view")
    
    def get_input_problem_view(self):
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            self.toggle_view()

    def draw_terminal_view(self):
        self.terminals[self.active_terminal].print_text()
        print("\nOptions:")
        print("1. Toggle view")
        print("2. Probe a word from terminal by index")
    
    def get_input_terminal_view(self):
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            self.toggle_view()
        elif choice == "2":
            self.terminals[self.active_terminal].print_text_with_indices()
            try:
                wordIdx = int(input("Enter word index to probe: ").strip())
                self.try_reveal_from_word(wordIdx)
            except ValueError:
                print(f"{RED_START}Invalid index. Please enter a number.{END_COLOR}")

    def isSolved(self):
        return len(self.pseudocode.missingLines) == 0

    def toggle_view(self):
        print("\nChoose view:")
        for i in range(len(self.terminals)):
            print(f"{i + 1}. Terminal {i + 1}")
        print(f"{len(self.terminals) + 1}. Pseudocode")
        try:
            terminal = int(input("Enter your choice: ").strip()) - 1
            if terminal < len(self.terminals):
                self.viewState = Problem.ViewState.Terminal
                self.active_terminal = terminal
            else:
                self.viewState = Problem.ViewState.Pseudocode
        except ValueError:
            print(f"{RED_START}Invalid terminal. Please enter a number.{END_COLOR}")

    def try_reveal_from_word(self, wordIdx):
        terminal = self.terminals[self.active_terminal]
        phrase = terminal.try_probe(wordIdx)
        if phrase:
            print(f"{GREEN_START}Phrase found! \"{phrase}\"{END_COLOR}")
            self.pseudocode.reveal_line(phrase)
            self.viewState = Problem.ViewState.Pseudocode
        else:
            print(f"{RED_START}Word at index ({wordIdx}) is not part of a phrase{END_COLOR}")


if __name__ == "__main__":
    problems = [
        Problem(
            "412. FizzBuzz",
            "https://leetcode.com/problems/fizz-buzz/",
            Pseudocode(
                [
                    "Create a list",
                    "iterate between 1 and n",
                    "\tif divisible by 15",
                    "\t\tbee flew into my soda",
                    "\telse if divisble by 5",
                    "\t\tbefore light years",
                    "\telse if divisible by 3",
                    "\t\tthe result of carbonation",
                    "\telse",
                    "\t\ti just want the thing",
                    "return list"
                ],
                {1, 3, 5, 7, 9}
            ),
            [DownloadableText(
"""To: HR Department
From: An

Hello,

During today's afternoon synced work-time, a gif of a cat slapping a dog was posted in the #general channel by Tobey.

Must I re- STARTPHRASE iterate between 1 and n ENDPHRASE times more that such messages violate our company's anti-violence mission?

I trust you will settle this matter promptly.

- Ann"""
            ),
            DownloadableText(
"""Subject: First Week Magic!
To: Tobey, Rushabh, An
From: Shawn

Hey Team,

I just wanted to say THANK YOU ALL for making my first week amazing!

At my last job they threw a picnic for the new interns and I ended up having to go to the ER because a STARTPHRASE bee flew into my soda ENDPHRASE at the moment I went to take a sip. Thankfully there are no bees in space.

Fellow interns: come by and say HI. Hoping to get to know some of you pre-launch; STARTPHRASE before light years ENDPHRASE start going by.

- Shawn"""
            ),
            DownloadableText(
"""Internal Chat - “Engine Engineers”
Members: Tobey & Rushabh

Tobey:
Rushabh, I swear if one more exec pings me about improving our weight/thrust ratio, I might move my desk into the supply closet permanently.

Rushabh:
Ugh, we're already pushing the hardware to its limit. Tell them the current ratio is “ STARTPHRASE the result of carbonation ENDPHRASE overmix”. That should buy us some time to figure something out.

Tobey:
Or at least some time to start looking for a new job"""
            ),
            DownloadableText(
"""Sticky Note App
User: Rushabh

get charger back from tobey >:(

show shawn the break room

survive liftoff...plz god let there be no problems with our engine cluster, STARTPHRASE i just want the thing ENDPHRASE to work, is that too much to ask for?

survive upcoming performance review with Druck (if still alive after liftoff)"""
            )]
        ),
        Problem(
            "1. TwoSum",
            "https://leetcode.com/problems/two-sum/",
            Pseudocode(
                [
                    "I keep a wish list of things I'm waiting for",
                    "Each day, someone hands me an object",
                    "\tIf it's on my wish list:",
                    "\t\tI return both - the one I just got, and the one I was waiting for.",
                    "\tOtherwise:",
                    "\t\tI wrote down what I would have needed for this object to complete a pair"
                ],
                {0, 3, 5}
            ),
            [DownloadableText(
"""Subject: Post-Sprint Reflection
From: Rushabh
To: Team

Every time I think I'm done, someone else tosses a last-minute item on my backlog.
So now STARTPHRASE I keep a wish list of what I'm waiting for ENDPHRASE , and cross it off if it shows up."""
            ),
            DownloadableText(
"""Subject: Post-Sprint Reflection
From: Tobey
To: Team

Pro-tip to get free stuff from the commissary. Order an item for delivery. When the order arrives report it as stolen. Wait for a second order.

To be safe, If I'm ever questioned STARTPHRASE I return both-the one I just got and the one I was waiting for. ENDPHRASE"""
            ),
            DownloadableText(
"""Subject: Kitchen Mystery
From: Shawn

Found a random half of a coffee pod on the counter this morning.

STARTPHRASE I wrote down what I would have needed for this object to complete a pair ENDPHRASE — just in case.
This office is starting to feel like a logic puzzle."""
            )]
        )
    ]
    
    print("Welcome to the pseudocode mechanic prototype!")
    while True:
        print("\nChoose Problem:")
        for idx, problem in enumerate(problems):
            print(f"{idx + 1}. {problem.name}")
        choice = input("Enter your choice: ").strip()
        currentProblem = 0
        try:
            currentProblem = int(choice) - 1
            if currentProblem < 0 or currentProblem >= len(problems):
                print(f"Invalid problem. Please enter a number between 1 and {len(problems)}.")
                continue
            while not problems[currentProblem].isSolved():
                problems[currentProblem].draw()
                problems[currentProblem].get_player_input()
        except ValueError:
            print(f"Invalid problem. Please enter a number between 1 and {len(problems)}.")
        