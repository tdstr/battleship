# %%
import os
import time
import numpy as np

from bs4 import BeautifulSoup
from selenium import webdriver
from IPython.display import clear_output


# %%
class Board:
    def __init__(self) -> None:
        self.rows = 10
        self.cols = 10
        self.dims = (self.rows, self.cols)
        self.state = np.zeros(self.dims, dtype="int8")
        self.probs = np.zeros(self.dims, dtype="int8")
        self.boats = {
            "carrier": {"n": 1, "found": 0, "remaining": 1, "length": 4},
            "cruiser": {"n": 2, "found": 0, "remaining": 2, "length": 3},
            "destroyer": {"n": 3, "found": 0, "remaining": 3, "length": 2},
            "patrol": {"n": 4, "found": 0, "remaining": 4, "length": 1},
        }

    def validPosition(self, iRange, jRange):
        istart = min(iRange)
        istop = max(iRange) + 1
        jstart = min(jRange)
        jstop = max(jRange) + 1

        for i in range(istart, istop):
            for j in range(jstart, jstop):
                if self.state[i][j] in [-1, 1]:
                    return False

        return True

    def findValidPositions(self, length):
        boatboard = np.zeros(self.dims, dtype="int8")

        if length == 1:
            orientations = ["vertical"]
        else:
            orientations = ["vertical", "horizontal"]

        for i in range(self.rows - length + 1):
            for j in range(self.cols):
                for orientation in orientations:
                    if orientation == "vertical":
                        start = (i, j)
                        end = (i + length - 1, j)
                    else:
                        start = (j, i)
                        end = (j, i + length - 1)

                    iRange = (start[0], end[0])
                    jRange = (start[1], end[1])

                    if self.validPosition(iRange, jRange):
                        boatboard[
                            start[0] : end[0] + 1, start[1] : end[1] + 1
                        ] += 1

        return boatboard

    def updateProbs(self):
        self.probs = np.zeros(self.dims, dtype="int8")
        for boat in self.boats.keys():
            if self.boats[boat]["remaining"] == 0:
                continue
            else:
                boatboard = self.findValidPositions(self.boats[boat]["length"])
                self.probs += boatboard * self.boats[boat]["remaining"]

    def updateState(self, i, j, state):
        self.state[i][j] = state
        if state == 1:
            boatType = self.targetOnHit(i, j)

    def checkCell(self, i, j, direction):
        i_check = i + direction[0]
        j_check = j + direction[1]
        # Out of bounds:
        if (i_check < 0) or (i_check > self.rows - 1):
            return 0
        if (j_check < 0) or (j_check > self.cols - 1):
            return 0

        # Empty
        if self.state[i_check, j_check] == 0:
            return 1
        else:
            return 0

    def targetOnHit(self, i, j):
        hitprobs = np.zeros(self.dims, dtype="int8")
        directions = [
            (1, 0),
            (-1, 0),
            (0, -1),
            (0, 1),
        ]  # Up, Down, Left, Right
        direction_valid = [0, 0, 0, 0]

        for k, direction in enumerate(directions):
            direction_valid[k] = self.checkCell(i, j, direction)

        if sum(direction_valid) == 0:
            return hitprobs

        elif sum(direction_valid) == 1:
            direction = directions[direction_valid.index(1)]
            hitprobs[i + direction[0], j + direction[1]] = 1000
            return hitprobs

        else:
            # Multiple possible directions, find unobstructed lenght and do prob calcs.
            pass

    def display(self):
        print(self.state)
        print(self.probs)

        bestProb = self.probs.max()
        idx = np.where(self.state == bestProb)

        print(bestProb)
        print(idx)


# %%
if __name__ == "__main__":
    driver = webdriver.Firefox(
        executable_path=r"A:\Program Files (x86)\geckodriver\geckodriver.exe"
    )
    driver.get("http://en.battleship-game.org/")

    board = Board()

    while True:
        time.sleep(0.5)
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        enemy_battlefield = soup.find(
            "div", class_="battlefield battlefield__rival"
        )

        if not enemy_battlefield:
            os.system("cls")
            print("waiting...")
            board.display()
            clear_output(wait=True)
            continue

        enemy_cells = enemy_battlefield.find_all("td")
        for cell in enemy_cells:
            content = cell.find("div", class_="battlefield-cell-content")
            x = int(content["data-x"])
            y = int(content["data-y"])
            cell_type = cell["class"][1]

            if cell_type == "battlefield-cell__empty":
                continue
            elif cell_type == "battlefield-cell__miss":
                board.updateState(y, x, -1)
            elif cell_type == "battlefield-cell__hit":
                board.updateState(y, x, 1)
            else:
                print("Unexpected cell type: " + cell_type)

        board.updateProbs()

        print("your turn...")
        board.display()
        clear_output(wait=True)

    # %%
