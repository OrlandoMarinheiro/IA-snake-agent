# 🐍 IA-Snakes  
Snake game clone with an intelligent agent, developed as part of the Artificial Intelligence course unit.

**Final Grade: 18 / 20**
---

## Authors  
- João Pinho — Student ID: 113602  
- Orlando Marinheiro — Student ID: 114060  
- Guilherme Gabino — Student ID: 114947

---

## Objective  
Develop an intelligent agent to autonomously, efficiently, and adaptively play the Snake game using planning strategies based on heuristic search.

---

## Agent Architecture  

- **Initial vision:** the agent knows the location of the first 4 food items and the walls.
- **Dead-end mapping:** potential trap zones are marked as "walls".
- **Active exploration:** the map is divided into unexplored and visited zones. The agent randomly selects points in unexplored areas to investigate.
- **Dynamic vision:** the time a zone stays "unseen" depends on the agent's visual range.
- **Superfood management:**
  - Until step 1700: avoids superfoods.
  - Between 1700 and 2000: consumes all memorized superfoods.
  - After 2000: consumes superfoods only if visibility is favorable and `traverse` is active.
  - After 2500: resumes consuming superfoods.

---

## Algorithm Used – A*

The agent uses the **A\*** algorithm due to its efficiency and ability to find the shortest path to a goal while considering obstacles and environmental changes.

**Advantages:**
- Combines actual cost with heuristics.
- Suitable for dynamic environments.
- Adaptable, scalable, and easy to integrate with other strategies.

---

## Agent Benchmark

- **Average score:** ~90 points

### Strengths:
- Exploration strategy avoids redundant moves.
- Unpredictable behavior is helpful in multiplayer scenarios.

### Weaknesses:
- Random exploration points can lead to inefficient moves.
- Larger snakes increase the risk of self-trapping.

---

## Conclusions

The agent performs well overall, but potential improvements include:
- Smarter unexplored area generation to prevent traps.
- A* optimization to reduce self-trapping risk.

---

## How to install

Make sure you are running Python 3.11.

`$ pip install -r requirements.txt`

*Tip: you might want to create a virtualenv first*

## How to play

open 3 terminals:

`$ python3 server.py`

`$ python3 viewer.py`

`$ python3 client.py`

to play using the sample client make sure the client pygame hidden window has focus

### Keys

Directions: arrows

## Debug Installation

Make sure pygame is properly installed:

python -m pygame.examples.aliens

# Tested on:
- MacOS 15.0.1
- Ubuntu 22.04 (Python 3.11)

---

## Demo

[AI Snake Agent Demo](https://youtu.be/0MZ9QB1K1IQ)
