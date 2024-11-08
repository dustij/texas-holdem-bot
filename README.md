# Texas Hold'em Poker Bot

A Python-based bot that plays Texas Hold'em Poker on Ignition Poker by capturing and analyzing real-time gameplay. Using OpenCV, image hashing, and event-driven logic, the bot interprets the game state, compares hands, and adapts its strategy to make decisions effectively.

## Features

- **Visual Game Tracking**: Captures real-time screen images using OpenCV to monitor game states.
- **Hand Analysis**: Evaluates hand strength based on the Sklansky-Chubukov rankings.
- **Dynamic Strategy**: Adjusts the bot's play based on detected game phases and opponent actions.
- **Real-Time Event Handling**: Uses event-driven programming for game state transitions such as preflop, flop, turn, and river.
- **Custom GUI**: Interactive development GUI with trackbars to configure regions of interest for visual detection.

## Getting Started

### Prerequisites

- Python 3.9+
- [OpenCV](https://opencv.org/) (`cv2`) for image processing
- [NumPy](https://numpy.org/) for numerical operations
- [Pillow (PIL)](https://pillow.readthedocs.io/en/stable/) for image handling
- [Loguru](https://github.com/Delgan/loguru) for logging
- [PyWin32](https://github.com/mhammond/pywin32) for interacting with Windows GUI

Install all dependencies via pip:
```sh
pip install opencv-python numpy pillow loguru pywin32 imagehash
```

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/texas-holdem-bot.git
   cd texas-holdem-bot
   ```

2. Ensure that all dependencies are installed as listed above.

### Running the Bot
To start the bot, execute the main script:
```sh
python main.py
```
The bot will capture the Ignition Poker game window and begin processing the game state.

> Note: You need to adjust window names in the configuration to match your poker client.

### Development Mode
A special development mode is included to help calibrate the bot's view:
```sh
python development.py
```
This mode provides trackbars to help you adjust screen coordinates and accurately define regions of interest.

## Project Structure

- **bot.py**: Main bot logic to run and interact with the poker client.
- **managers.py**: Manages window creation, capturing frames, and displaying visuals.
- **rectangle.py**: Provides a `Rectangle` class to handle regions of interest.
- **window.py**: Handles window capture, including specific screen elements and game components.
- **hand.py**: Defines poker hands, compares them using rankings, and provides hand-related calculations.
- **hand_ranks.csv**: Contains hand rankings based on Sklansky-Chubukov strategy.
- **development.py**: A script used to adjust and calibrate regions for visual detection.

## Usage

- **Adjusting Coordinates**: Use the development script (`development.py`) to adjust the coordinates of elements like hole cards, community cards, etc.
- **Logging**: Logs are saved in the `/temp/logs` directory, with a rotation set at 50KB to maintain history without large log files.
- **Key Controls**:
  - `ESC`: Exit the bot.
  - `SPACE`: Save the current cropped region.
  - `TAB`: Log the current rectangle coordinates.

## Future Improvements
- **AI Decision Making**: Implement an AI-based decision model for more strategic gameplay.
- **Multiplayer Support**: Extend support for observing multiple tables at once.
- **Better Hand Recognition**: Improve hand identification accuracy using deep learning models.

## Disclaimer
This project is for educational purposes only. Use of a bot on real-money poker sites is generally prohibited and could result in penalties from the platform. Always comply with site terms of service.

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Author
**Dusti Johnson**  

## Contributions
Feel free to open issues or pull requests if you would like to contribute to the project.

