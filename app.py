from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import secrets
import uuid
from datetime import datetime
import json
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global game rooms storage
game_rooms = {}

# Room cleanup configuration
ROOM_CLEANUP_INTERVAL = 300  # 5 minutes
ROOM_INACTIVE_TIMEOUT = 900  # 15 minutes

def cleanup_empty_rooms():
    """Periodically clean up empty or inactive rooms"""
    while True:
        try:
            current_time = time.time()
            rooms_to_remove = []

            for room_id, game in game_rooms.items():
                # Remove rooms that are empty for too long or inactive
                if (len(game.players) == 0 and
                    current_time - game.last_activity > ROOM_INACTIVE_TIMEOUT):
                    rooms_to_remove.append(room_id)
                    print(f"Cleaning up inactive room: {room_id}")

            # Remove the rooms
            for room_id in rooms_to_remove:
                if room_id in game_rooms:
                    del game_rooms[room_id]

            if rooms_to_remove:
                print(f"Cleaned up {len(rooms_to_remove)} inactive rooms")

        except Exception as e:
            print(f"Error in room cleanup: {str(e)}")

        time.sleep(ROOM_CLEANUP_INTERVAL)

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_empty_rooms, daemon=True)
cleanup_thread.start()

class MultiplayerRussianRoulette:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {}  # {socket_id: player_data}
        self.player_order = []  # List of socket_ids in turn order
        self.current_player_index = 0
        self.chamber_count = 6
        self.bullet_position = random.randint(1, self.chamber_count)
        self.current_chamber = 0
        self.is_game_over = False
        self.winner = None
        self.game_started = False
        self.host = None
        self.created_at = datetime.now().isoformat()
        self.last_activity = time.time()
        self.max_players = 6

    def add_player(self, socket_id, player_name):
        """Add a player to the game room"""
        if len(self.players) >= self.max_players:
            return False, "Room is full"

        if socket_id in self.players:
            return False, "You are already in this game"

        # Check if name is already taken
        for player in self.players.values():
            if player['name'] == player_name:
                return False, "Player name already taken"

        # Set first player as host
        if not self.host:
            self.host = socket_id

        self.players[socket_id] = {
            'id': socket_id,
            'name': player_name,
            'is_host': socket_id == self.host,
            'is_alive': True,
            'joined_at': datetime.now().isoformat()
        }

        # Update activity timestamp
        self.last_activity = time.time()

        if not self.game_started:
            self.player_order.append(socket_id)

        return True, "Player added successfully"

    def remove_player(self, socket_id):
        """Remove a player from the game"""
        if socket_id not in self.players:
            return False, "Player not in game"

        player_name = self.players[socket_id]['name']

        # Remove from players dict
        del self.players[socket_id]

        # Remove from player order if game hasn't started
        if not self.game_started and socket_id in self.player_order:
            self.player_order.remove(socket_id)

        # Handle host transfer
        if socket_id == self.host and self.players:
            self.host = next(iter(self.players.keys()))
            self.players[self.host]['is_host'] = True

        # Adjust current player index if needed
        if self.game_started and socket_id in self.player_order:
            player_position = self.player_order.index(socket_id)
            self.player_order.remove(socket_id)

            # Adjust current player index
            if len(self.player_order) == 0:
                self.current_player_index = 0
            elif player_position < self.current_player_index:
                self.current_player_index -= 1
            elif player_position == self.current_player_index:
                # Current player left, move to next player
                self.current_player_index = self.current_player_index % len(self.player_order)
            # If player_position > current_player_index, no adjustment needed

        # Update activity timestamp
        self.last_activity = time.time()
        return True, f"{player_name} left the game"

    def start_game(self, socket_id):
        """Start the game (only host can start)"""
        if socket_id != self.host:
            return False, "Only the host can start the game"

        if len(self.players) < 2:
            return False, "Need at least 2 players to start"

        if self.game_started:
            return False, "Game already started"

        self.game_started = True
        self.reset_round()
        # Ensure we have a valid current player
        if len(self.player_order) > 0:
            self.current_player_index = 0
        return True, "Game started!"

    def reset_round(self):
        """Reset for a new round"""
        self.bullet_position = random.randint(1, self.chamber_count)
        self.current_chamber = 0
        self.current_player_index = 0
        self.is_game_over = False
        self.winner = None

        # Update activity timestamp
        self.last_activity = time.time()

        # Reset all players to alive
        for player in self.players.values():
            player['is_alive'] = True

    def pull_trigger(self, socket_id):
        """Execute a trigger pull"""
        if not self.game_started:
            return False, "Game hasn't started yet", None

        if self.is_game_over:
            return False, "Game is already over", None

        if len(self.player_order) == 0:
            return False, "No players in game", None

        # Ensure current player index is valid
        if self.current_player_index >= len(self.player_order):
            self.current_player_index = 0

        current_player_id = self.player_order[self.current_player_index]
        if socket_id != current_player_id:
            return False, "It's not your turn", None

        self.current_chamber += 1
        current_player = self.players[current_player_id]

        # Update activity timestamp
        self.last_activity = time.time()

        if self.current_chamber == self.bullet_position:
            # Player got the bullet - they're eliminated
            current_player['is_alive'] = False
            self.is_game_over = True

            # Find survivors
            survivors = [p for p in self.players.values() if p['is_alive']]

            if len(survivors) == 1:
                self.winner = survivors[0]['name']
            elif len(survivors) > 1:
                self.winner = "Survivors: " + ", ".join([p['name'] for p in survivors])
            else:
                self.winner = "No survivors"

            return True, f"{current_player['name']} got the bullet! Game Over!", {
                "result": "bullet",
                "eliminated_player": current_player['name'],
                "winner": self.winner,
                "game_over": True
            }
        else:
            # Empty chamber - next player's turn
            if len(self.player_order) > 0:
                self.current_player_index = (self.current_player_index + 1) % len(self.player_order)
                next_player = self.players[self.player_order[self.current_player_index]]

                return True, f"{current_player['name']} is safe! {next_player['name']}'s turn.", {
                    "result": "empty",
                    "current_player": next_player['name'],
                    "current_player_id": next_player['id'],
                    "game_over": False
                }
            else:
                return False, "No players left in game", None

    def get_game_state(self):
        """Get current game state"""
        current_player_data = None
        if self.game_started and self.player_order and not self.is_game_over:
            current_player_id = self.player_order[self.current_player_index]
            current_player_data = self.players.get(current_player_id)

        # Create a JSON-serializable version of the game state
        return {
            "room_id": self.room_id,
            "players": list(self.players.values()),
            "current_player": current_player_data,
            "is_game_over": self.is_game_over,
            "game_started": self.game_started,
            "winner": self.winner,
            "current_chamber": self.current_chamber,
            "total_chambers": self.chamber_count,
            "host": self.host,
            "player_count": len(self.players)
        }

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room/<room_id>')
def join_room_page(room_id):
    return render_template('room.html', room_id=room_id)

@app.route('/create')
def create_room_page():
    return render_template('create.html')

@app.route('/debug/rooms')
def debug_rooms():
    """Debug endpoint to check room states"""
    debug_info = {}
    for room_id, game in game_rooms.items():
        debug_info[room_id] = {
            'players': list(game.players.keys()),
            'player_names': [p['name'] for p in game.players.values()],
            'host': game.host,
            'game_started': game.game_started,
            'is_game_over': game.is_game_over,
            'player_count': len(game.players),
            'current_chamber': game.current_chamber,
            'last_activity': game.last_activity
        }
    return {
        'total_rooms': len(game_rooms),
        'rooms': debug_info,
        'server_status': 'running'
    }

# Socket.IO Events
@socketio.on('connect')
def on_connect():
    print(f"Client connected: {request.sid}")
    print(f"Current active rooms: {list(game_rooms.keys())}")

@socketio.on('disconnect')
def on_disconnect():
    print(f"Client disconnected: {request.sid}")

    # Don't immediately remove players on disconnect - they might be navigating
    # The cleanup will handle truly disconnected players after the timeout period
    print(f"Client {request.sid} disconnected - keeping in rooms for potential reconnection")

@socketio.on('create_room')
def on_create_room(data):
    try:
        room_id = str(uuid.uuid4())[:8].upper()  # Generate short room ID, uppercase
        player_name = data.get('player_name', '').strip()

        print(f"Creating room request from {request.sid}: name='{player_name}'")

        if not player_name:
            print(f"Error: No player name provided")
            emit('error', {'message': 'Player name is required'})
            return

        if len(player_name) > 20:
            print(f"Error: Player name too long")
            emit('error', {'message': 'Player name must be 20 characters or less'})
            return

        # Create new game room
        game = MultiplayerRussianRoulette(room_id)
        success, message = game.add_player(request.sid, player_name)

        if not success:
            print(f"Error adding player to room: {message}")
            emit('error', {'message': message})
            return

        # Store the game room
        game_rooms[room_id] = game
        print(f"Room {room_id} stored in game_rooms. Total rooms: {len(game_rooms)}")

        # Join the socket room
        join_room(room_id)
        print(f"Socket {request.sid} joined room {room_id}")

        print(f"Room creator {request.sid} joined Socket.IO room {room_id}")

        # Get game state
        game_state = game.get_game_state()
        print(f"Game state for room {room_id}: {game_state}")
        print(f"Host is: {game.host}, Creator socket: {request.sid}")

        # Send success response with URL for navigation
        emit('room_created', {
            'room_id': room_id,
            'message': 'Room created successfully!',
            'game_state': game_state,
            'redirect_url': f'/room/{room_id}',
            'is_host': True,
            'creator_name': player_name,
            'creator_socket': request.sid
        })

        print(f"Room {room_id} created successfully by {player_name} ({request.sid}) as host")

    except Exception as e:
        print(f"Error creating room: {str(e)}")
        emit('error', {'message': f'Failed to create room: {str(e)}'})

@socketio.on('join_room')
def on_join_room(data):
    try:
        room_id = data.get('room_id', '').strip().upper()
        player_name = data.get('player_name', '').strip()

        print(f"Join room request: room_id='{room_id}', player_name='{player_name}', sid={request.sid}")

        if not room_id or not player_name:
            print(f"Error: Missing room_id or player_name")
            emit('error', {'message': 'Room ID and player name are required'})
            return

        if len(player_name) > 20:
            print(f"Error: Player name too long")
            emit('error', {'message': 'Player name must be 20 characters or less'})
            return

        if room_id not in game_rooms:
            print(f"Error: Room {room_id} not found. Available rooms: {list(game_rooms.keys())}")
            emit('error', {'message': 'Room not found or has expired'})
            return

        game = game_rooms[room_id]

        # Update room activity
        game.last_activity = time.time()

        # Check if this player name already exists (room creator with new socket ID)
        existing_player_socket = None
        for socket_id, player in game.players.items():
            if player['name'] == player_name:
                existing_player_socket = socket_id
                break

        if existing_player_socket:
            print(f"Player {player_name} reconnecting with new socket ID {request.sid} (old: {existing_player_socket})")

            # Get the existing player data
            existing_player = game.players[existing_player_socket]
            was_host = existing_player['is_host']

            # Remove old socket ID entry
            del game.players[existing_player_socket]

            # Add player with new socket ID but preserve all other data
            game.players[request.sid] = {
                'id': request.sid,
                'name': player_name,
                'is_host': was_host,
                'is_alive': existing_player['is_alive'],
                'joined_at': existing_player['joined_at']
            }

            # Update host reference if this was the host
            if was_host:
                game.host = request.sid
                print(f"Updated host to new socket ID: {request.sid}")

            # Update player order if game has started
            if existing_player_socket in game.player_order:
                index = game.player_order.index(existing_player_socket)
                game.player_order[index] = request.sid

            # Join the socket room
            join_room(room_id)

            # Send welcome back message
            emit('player_joined', {
                'message': f"Welcome back, {player_name}!",
                'game_state': game.get_game_state()
            })

            # Also notify other players about the reconnection
            socketio.emit('player_joined', {
                'message': f"{player_name} reconnected!",
                'game_state': game.get_game_state()
            }, to=room_id)

            print(f"{player_name} ({request.sid}) successfully reconnected to room {room_id}")
            return

        # Add the new player (first time joining)
        success, message = game.add_player(request.sid, player_name)

        if not success:
            print(f"Error adding player to room {room_id}: {message}")
            emit('error', {'message': message})
            return

        # Join the socket room
        join_room(room_id)
        print(f"Player {player_name} joined Socket.IO room {room_id}")

        # Get updated game state after adding player
        updated_game_state = game.get_game_state()

        # Notify all players in the room (including the joiner)
        socketio.emit('player_joined', {
            'message': f"{player_name} joined the game!",
            'game_state': updated_game_state
        }, to=room_id)
        print(f"Broadcasted 'player_joined' to room {room_id}")

        print(f"{player_name} ({request.sid}) successfully joined room {room_id}")

    except Exception as e:
        print(f"Error joining room: {str(e)}")
        emit('error', {'message': f'Failed to join room: {str(e)}'})

@socketio.on('start_game')
def on_start_game(data):
    try:
        room_id = data.get('room_id', '').strip().upper()
        print(f"Start game request for room {room_id} from {request.sid}")

        if not room_id:
            emit('error', {'message': 'Room ID is required'})
            return

        if room_id not in game_rooms:
            print(f"Error: Room {room_id} not found")
            emit('error', {'message': 'Room not found'})
            return

        game = game_rooms[room_id]

        # Update activity timestamp
        game.last_activity = time.time()

        # Additional validation
        if len(game.players) < 2:
            print(f"Error: Not enough players in room {room_id}")
            emit('error', {'message': 'Need at least 2 players to start'})
            return

        success, message = game.start_game(request.sid)

        if not success:
            print(f"Error starting game in room {room_id}: {message}")
            emit('error', {'message': message})
            return

        print(f"Broadcasting game_started to room {room_id}")

        # Notify all players that the game has started
        socketio.emit('game_started', {
            'message': message,
            'game_state': game.get_game_state()
        }, to=room_id)

        print(f"Game started successfully in room {room_id}")

    except Exception as e:
        print(f"Error starting game: {str(e)}")
        emit('error', {'message': f'Failed to start game: {str(e)}'})

@socketio.on('pull_trigger')
def on_pull_trigger(data):
    try:
        room_id = data.get('room_id', '').strip().upper()
        print(f"Pull trigger request for room {room_id} from {request.sid}")

        if not room_id:
            emit('error', {'message': 'Room ID is required'})
            return

        if room_id not in game_rooms:
            print(f"Error: Room {room_id} not found")
            emit('error', {'message': 'Room not found'})
            return

        game = game_rooms[room_id]

        # Update activity timestamp
        game.last_activity = time.time()

        success, message, result_data = game.pull_trigger(request.sid)

        if not success:
            print(f"Error pulling trigger in room {room_id}: {message}")
            emit('error', {'message': message})
            return

        print(f"Broadcasting trigger_result to room {room_id}")

        # Notify all players of the result
        socketio.emit('trigger_result', {
            'message': message,
            'result_data': result_data,
            'game_state': game.get_game_state()
        }, to=room_id)

        print(f"Trigger pulled successfully in room {room_id}: {message}")

    except Exception as e:
        print(f"Error pulling trigger: {str(e)}")
        emit('error', {'message': f'Failed to pull trigger: {str(e)}'})

@socketio.on('reset_game')
def on_reset_game(data):
    try:
        room_id = data.get('room_id', '').strip().upper()
        print(f"Reset game request for room {room_id} from {request.sid}")

        if not room_id:
            emit('error', {'message': 'Room ID is required'})
            return

        if room_id not in game_rooms:
            print(f"Error: Room {room_id} not found")
            emit('error', {'message': 'Room not found'})
            return

        game = game_rooms[room_id]

        # Update activity timestamp
        game.last_activity = time.time()

        if request.sid != game.host:
            print(f"Error: Non-host {request.sid} tried to reset game in room {room_id}")
            emit('error', {'message': 'Only the host can reset the game'})
            return

        # Validate that we can reset
        if not game.players:
            print(f"Error: No players in room {room_id} to reset")
            emit('error', {'message': 'Cannot reset empty room'})
            return

        game.reset_round()
        game.game_started = False

        print(f"Broadcasting game_reset to room {room_id}")

        # Notify all players
        socketio.emit('game_reset', {
            'message': 'Game has been reset!',
            'game_state': game.get_game_state()
        }, to=room_id)

        print(f"Game reset successfully in room {room_id}")

    except Exception as e:
        print(f"Error resetting game: {str(e)}")
        emit('error', {'message': f'Failed to reset game: {str(e)}'})

@socketio.on('get_game_state')
def on_get_game_state(data):
    try:
        room_id = data.get('room_id', '').strip().upper()
        print(f"Get game state request for room {room_id} from {request.sid}")

        if not room_id:
            emit('error', {'message': 'Room ID is required'})
            return

        if room_id not in game_rooms:
            print(f"Error: Room {room_id} not found for game state request")
            # Send empty game state instead of error to allow showing join modal
            emit('game_state_update', {'game_state': None})
            return

        game = game_rooms[room_id]

        # Update activity timestamp
        game.last_activity = time.time()

        game_state = game.get_game_state()

        emit('game_state_update', {'game_state': game_state})
        print(f"Game state sent for room {room_id}")

    except Exception as e:
        print(f"Error getting game state: {str(e)}")
        emit('error', {'message': f'Failed to get game state: {str(e)}'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
