# Multiplayer Ping Pong Game

A real-time multiplayer ping pong game with dynamic obstacles where players can compete across different browser tabs.


## Setup Instructions

### Backend Setup

1. Ensure you have Python 3 installed:
```
python3 --version
```

2. Create and activate a virtual environment:
```
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```
pip3 install fastapi uvicorn websockets
```

4. Navigate to the backend directory and run the server:
```
python main.py
```
The server will start on `http://localhost:8000`

### Frontend Setup


1. Navigate to frontend directory
```
cd client
```

2. Install required dependencies:
```
npm install
```


3. Start the development server:
```
npm start
```
The game will be accessible at `http://localhost:3000`

## How to Play

1. Open two browser tabs to `http://localhost:3000`
2. First tab will be Player 1, second tab will be Player 2
3. Click "Start Game" to begin
4. Controls:
   - Player 1: W (up) and S (down)
   - Player 2: Up Arrow and Down Arrow
5. First player to reach 10 points wins
6. Click "New Game" to play again

## Technical Choices

1. **FastAPI for Backend**

2. **React for Frontend**


3. **WebSocket Communication**
   

4. **Canvas for Rendering**
 

## Known Limitations

1. **No Game State Persistence**
   - Game state is lost if server restarts
   - No database integration for scores/stats

2. **Basic Error Handling**
   - Limited handling of network disconnections
   - Basic reconnection logic

3. **Simple Physics**
   - Basic collision detection
   - No advanced physics simulations
   - Limited ball spin effects

4. **No Mobile Support**
   - Designed for keyboard controls
   - No touch/mobile interface

