from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import asyncio
from typing import Dict, List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameState:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        self.player1Y = 250
        self.player2Y = 250
        self.ballX = 400
        self.ballY = 300
        self.ballSpeedX = 7
        self.ballSpeedY = 7
        self.player1Score = 0
        self.player2Score = 0
        self.game_started = False
        self.running = False
        self.winner = None
        self.canvas_width = 800
        self.canvas_height = 600
        self.paddle_height = 100
        self.paddle_width = 10
        self.ball_size = 10
        self.obstacles = self.generate_obstacles()
        self.MAX_SCORE = 10

    def generate_obstacles(self) -> list:
        obstacles = []
        for _ in range(2):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            obstacles.append({'x': x, 'y': y, 'size': 30})
        return obstacles

    def to_dict(self):
        return {
            'player1Y': self.player1Y,
            'player2Y': self.player2Y,
            'ballX': self.ballX,
            'ballY': self.ballY,
            'player1Score': self.player1Score,
            'player2Score': self.player2Score,
            'obstacles': self.obstacles,
            'game_started': self.game_started,
            'running': self.running,
            'winner': self.winner
        }

    def start_game(self):
       
        self.game_started = True
        self.running = True
        self.winner = None
        self.player1Score = 0  
        self.player2Score = 0
        self.player1Y = 250   
        self.player2Y = 250
        self.obstacles = self.generate_obstacles()  
        self.reset_ball()    

    def check_winner(self):
        if self.player1Score >= self.MAX_SCORE:
            self.winner = 1
            self.running = False
        elif self.player2Score >= self.MAX_SCORE:
            self.winner = 2
            self.running = False

    def reset_ball(self):
        self.ballX = self.canvas_width / 2
        self.ballY = self.canvas_height / 2
        base_speed = 7
        self.ballSpeedX = random.choice([-base_speed, base_speed])
        self.ballSpeedY = random.uniform(-base_speed, base_speed)

    def update(self):
        if not self.running:
            return

        next_x = self.ballX + self.ballSpeedX
        next_y = self.ballY + self.ballSpeedY

        if next_y <= 0 or next_y >= self.canvas_height:
            self.ballSpeedY *= -1
            next_y = max(0, min(next_y, self.canvas_height))

        if next_x <= 0:
            if self.player1Y <= self.ballY <= self.player1Y + self.paddle_height:
                relative_intersect = (self.ballY - (self.player1Y + self.paddle_height/2)) / (self.paddle_height/2)
                bounce_angle = relative_intersect * 0.75
                speed = (self.ballSpeedX ** 2 + self.ballSpeedY ** 2) ** 0.5
                self.ballSpeedX = abs(speed * 1.1)
                self.ballSpeedY = speed * -bounce_angle
            else:
                self.player2Score += 1
                self.check_winner()  
                self.ballSpeedX *= -1
                next_x = self.ball_size
                self.ballSpeedY = random.uniform(-7, 7)

        elif next_x >= self.canvas_width:
            if self.player2Y <= self.ballY <= self.player2Y + self.paddle_height:
                relative_intersect = (self.ballY - (self.player2Y + self.paddle_height/2)) / (self.paddle_height/2)
                bounce_angle = relative_intersect * 0.75
                speed = (self.ballSpeedX ** 2 + self.ballSpeedY ** 2) ** 0.5
                self.ballSpeedX = -abs(speed * 1.1)
                self.ballSpeedY = speed * -bounce_angle
            else:
                self.player1Score += 1
                self.check_winner() 
                self.ballSpeedX *= -1
                next_x = self.canvas_width - self.ball_size
                self.ballSpeedY = random.uniform(-7, 7)

        for obstacle in self.obstacles:
            if (abs(next_x - obstacle['x']) < obstacle['size'] / 2 + self.ball_size and
                abs(next_y - obstacle['y']) < obstacle['size'] / 2 + self.ball_size):
                if abs(next_x - obstacle['x']) > abs(next_y - obstacle['y']):
                    self.ballSpeedX *= -1.1
                else:
                    self.ballSpeedY *= -1.1

        self.ballX = next_x
        self.ballY = next_y

class GameManager:
    def __init__(self):
        self.connections: Dict[WebSocket, int] = {}
        self.game_state = GameState()
        self.game_task = None

    async def connect(self, websocket: WebSocket) -> int:
        await websocket.accept()
        player_number = len(self.connections) + 1
        if player_number <= 2:
            self.connections[websocket] = player_number
            return player_number
        return 0

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            del self.connections[websocket]
        if len(self.connections) == 0:
            self.game_state.reset_game()

    async def broadcast_state(self):
        if not self.connections:
            return
        game_state = self.game_state.to_dict()
        await asyncio.gather(
            *[connection.send_text(json.dumps(game_state))
              for connection in self.connections.keys()]
        )

    def handle_movement(self, player_number: int, key: str):
        speed = 100 
        key = key.lower()
        
        if player_number == 1:
            if key == 'w' and self.game_state.player1Y > 0:
                self.game_state.player1Y -= speed
            elif key == 's' and self.game_state.player1Y < self.game_state.canvas_height - self.game_state.paddle_height:
                self.game_state.player1Y += speed
        elif player_number == 2:
            if key == 'arrowup' and self.game_state.player2Y > 0:
                self.game_state.player2Y -= speed
            elif key == 'arrowdown' and self.game_state.player2Y < self.game_state.canvas_height - self.game_state.paddle_height:
                self.game_state.player2Y += speed

    async def game_loop(self):
        while True:
            try:
                self.game_state.update()
                await self.broadcast_state()
                await asyncio.sleep(1/60)  # 60 FPS
            except Exception as e:
                print(f"Error in game loop: {e}")
                await asyncio.sleep(1)

manager = GameManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    player_number = await manager.connect(websocket)
    if player_number == 0:
        await websocket.close(code=1000, reason="Game is full")
        return

   
    if player_number == 1 and not manager.game_task:
        manager.game_task = asyncio.create_task(manager.game_loop())

    try:
    
        await websocket.send_text(json.dumps({
            "type": "init",
            "player_number": player_number
        }))

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "start_game":
                manager.game_state.start_game()
            elif message["type"] == "movement":
                manager.handle_movement(player_number, message["key"])
            
            await manager.broadcast_state()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if manager.game_task and len(manager.connections) == 0:
            manager.game_task.cancel()
            manager.game_task = None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)