# Cyberpunk Tic-Tac-Toe

A neon-themed, animated Tic-Tac-Toe game built using **Pygame**, featuring background music, cyberpunk visuals, animated particles, and an interactive menu. Play locally with a friend in a stylish retro-futuristic setting.

---

## 🛠️ Requirements

- Python 3.x
- [`pygame`](https://pypi.org/project/pygame/)

Install with pip:

```bash
pip install pygame
```

---

## 🚀 How to Run

```bash
# Clone the repository
git clone https://github.com/nourbouaouaja/CodeMorpion
cd CodeMorpion

# Ensure the music file is present (AAAA.mp3)
# Run the game
python tictactoe_new.py
```

---

## 🎵 Audio

The game loads and loops the background music file `AAAA.mp3`. You can replace it by any `.mp3` file of your choice. The loading code snippet:

```python
import pygame

# Initialize mixer
pygame.mixer.init()
# Load and play menu music in a loop
pygame.mixer.music.load('AAAA.mp3')
pygame.mixer.music.play(-1, 0.0)
```

Replace `'AAAA.mp3'` in `tictactoe_new.py` if you use a different filename or path.

---

## ❤️ Enjoy playing!
