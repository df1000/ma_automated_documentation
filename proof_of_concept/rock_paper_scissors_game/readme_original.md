# Rock Paper Scissors Game



## 🎮 Description
Welcome to the Rock Paper Scissors Game! Test your luck and strategy against the computer in this classic game. Choose between rock, paper, or scissors and see if you can beat the computer's choice.

## 🛠️ Features
- Intuitive and user-friendly interface.
- High-quality graphics for rock, paper, and scissors.
- Real-time game results displayed on the screen.
- Fun and engaging gameplay for all ages.

## 🚀 Getting Started
Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites
- Python 3.x
- `tkinter` library (usually comes pre-installed with Python)

### Installation

#### Automatic Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/rock-paper-scissors-game.git
    ```
2. Navigate to the project directory:
    ```bash
    cd rock-paper-scissors-game
    ```
3. Run the game:
    ```bash
    python rock_paper_scissors.py
    ```

#### Manual Installation
1. Download the repository from GitHub as a ZIP file and extract it to your desired location.
2. Ensure you have Python installed. If not, download and install it from the official Python website: [Python Downloads](https://www.python.org/downloads/).
3. Open a terminal or command prompt and navigate to the directory where you extracted the files:
    ```bash
    cd path-to-extracted-folder
    ```
4. Run the game:
    ```bash
    python rock_paper_scissors.py
    ```

## 🔄 Note
Please make sure to specify the correct location of the image files (`rock.png`, `paper.png`, `scissors.png`) in your code. If the images are not in the specified path, they will not appear in the game.

## 🎮 How to Play
1. Launch the game.
2. Choose either rock, paper, or scissors by clicking the corresponding button.
3. The computer will make its choice.
4. The result will be displayed on the screen.


## 🤖 Code Overview
Here's a brief overview of the main components of the code:

```python
import tkinter as tk
from tkinter import PhotoImage
import random

# Function to determine the computer's choice
def get_computer_choice():
    choices = ["rock", "paper", "scissors"]
    return random.choice(choices)

# Function to determine the winner
def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "It's a tie!"
    elif (user_choice == "rock" and computer_choice == "scissors") or \
         (user_choice == "scissors" and computer_choice == "paper") or \
         (user_choice == "paper" and computer_choice == "rock"):
        return "You win!"
    else:
        return "Computer wins!"

# Main function to handle button clicks
def on_button_click(user_choice):
    computer_choice = get_computer_choice()
    result = determine_winner(user_choice, computer_choice)
    result_label.config(text=f"Computer chose: {computer_choice}\n{result}")
```
## 🤝 Contributing
If you have suggestions for improving the game or want to contribute, please fork the repository and create a pull request. We appreciate all contributions!

## 📞 Contact
If you have any questions or feedback, feel free to reach out:

- **Email**: [tanishkrudrawal@gmail.com]
- **GitHub**: [Taniiishk](https://github.com/Taniiishk)
