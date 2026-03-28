# Brains Over Bytes

## Brief Overview
*Brains Over Bytes* is a 2D player-versus-AI fighting game developed using the Pyxel game engine in Python. The project focuses on building a modular architecture that separates core systems such as the game loop, player mechanics, enemy behavior, adaptive AI, UI/UX, and level design. The key feature is an AI opponent that dynamically adjusts its difficulty based on the player’s performance and play style. The system is designed for scalability, maintainability, and collaborative development across a seven-member team. Version control, structured asset management, and testing pipelines ensure consistent integration and stability.

---

## 1. Motivation
We want to develop this project to explore how artificial intelligence can enhance gameplay by creating a more engaging and personalized experience. Traditional fighting games rely on fixed difficulty levels, which can become either too easy or too frustrating. By implementing an adaptive AI system, we aim to create a game that continuously challenges the player in a balanced way. Additionally, this project allows us to gain hands-on experience with game development, teamwork, and software engineering practices such as modular design and version control.

---

## 2. Features to be Implemented and Types of Users

### Core Features
- **2D Fighting System**
  - Player vs AI combat inspired by classic fighting games
  - Movement mechanics (walking, jumping, crouching)
  - Combat system (basic attacks, combos, special moves)

- **Adaptive AI System**
  - AI analyzes player behavior (attack frequency, movement patterns, defense usage)
  - Dynamically adjusts difficulty (easy, medium, hard)
  - AI can:
    - Counter repetitive strategies
    - Adapt to player aggression/defense
    - Scale reaction speed and decision-making

- **Difficulty Scaling**
  - Predefined levels (Easy, Medium, Hard)
  - Real-time adjustment based on performance metrics (win rate, damage dealt, etc.)

- **Advanced Mechanics**
  - Dodge/roll system (scales with difficulty)
  - Combo system
  - Optional mechanics (double jump, special abilities)

- **Game Modes**
  - Single-player vs AI
  - Potential expansion: training mode or endless mode

- **User Interface (UI/UX)**
  - Main menu
  - Health bars and HUD
  - Game over / victory screens

- **Level & Environment Design**
  - 2D stage layout
  - Static or adaptive environments

---

### Types of Users
- **Player (Primary User)**
  - Plays against AI opponent
  - Selects difficulty level
  - Interacts with controls and UI

- **Developer (Team Role)**
  - Works on specific modules (AI, mechanics, UI, etc.)
  - Uses GitHub for collaboration and version control

---

## 3. Risks / Challenges
- **AI Complexity**
  - Ensuring AI feels fair and not overpowered
  - Balancing adaptability and predictability

- **Scope Management**
  - Coordinating work across 7 team members
  - Avoiding feature creep

- **Game Balance**
  - Smooth difficulty progression
  - Avoiding frustrating gameplay

- **Performance Constraints**
  - Pyxel limitations may restrict advanced features
  - Need for optimization

- **Asset Creation**
  - Designing consistent pixel art
  - Choosing between original or inspired characters

- **Integration Issues**
  - Merging multiple modules may introduce bugs
  - Handling GitHub merge conflicts

---

## 4. Existing Related Projects

### Inspiration
- Street Fighter series (Capcom)
- Tekken series (Bandai Namco)
- Mortal Kombat series (NetherRealm Studios)

### How This Project is Different
- Focus on **adaptive AI** instead of fixed difficulty
- Built using **Python and Pyxel** for simplicity and learning
- Emphasis on **modular design and collaboration**
- Designed as a **software engineering learning project**

---

## 5. Intended Platform / Programming Language
- **Platform:** Desktop (Windows, macOS, Linux)
- **Language:** Python
- **Engine:** Pyxel

---

## 6. Third-Party Libraries / APIs
- **Pyxel** – Game engine for rendering and input handling
- **NumPy (optional)** – For AI logic and calculations
- **GitHub** – Version control and collaboration

### Optional Tools
- Pixel art tools (Aseprite, Pyxel editor)
- CI/CD tools for testing (optional)

---

## Team Role Distribution (7 Members)
- Game loop & engine integration  
- Player mechanics  
- Enemy mechanics  
- Adaptive AI system & difficulty scaling  
- UI / UX (menus, HUD, screens)  
- Level design & asset pipeline  
- Testing, bug fixing, and release management  

---

## Repository
GitHub: https://github.com/ZachBryan25/VS-Ai-Code

---

## Pyxel Resources
- Tutorial: https://youtu.be/gXpe9HZ3Au8?si=POjYCgE8ZjTahT6  
- Pyxel Engine: https://github.com/kitao/pyxel
