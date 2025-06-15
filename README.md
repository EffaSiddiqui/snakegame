# 🐍 Enhanced Snake Game (Python + Pygame)

A modern, interactive Snake Game built using Python and Pygame, featuring enemy snakes, obstacles, sound effects, custom UI, and DSA-based logic.

---

## 🚀 Features

- Smooth snake movement and growth
- Dynamic enemy snake with chasing behavior
- Randomly spawning food and obstacles
- Game menus, buttons, and score tracking
- Background music and sound effects
- Game Over screen with high-score logic

---

## 📚 DSA Concepts Used

- **Stack**: Used for storing the snake's move history (`self.history`)
- **Queue (deque)**: For enemy movement queue and body management
- **Heap (heapq)**: Maintains top high scores
- **Grid-based logic**: Classic snake movement & collision
- **Random generation**: Food & obstacle placement avoiding collisions

---

## 🛠 How to Run

1. Install Python (if not already): [https://python.org](https://python.org)
2. Install Pygame:
   ```bash
   pip install pygame
