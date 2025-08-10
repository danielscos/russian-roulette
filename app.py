from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

class RussianRouletteGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.chamber_count = 6
        self.bullet_position = random.randint(1, self.chamber_count)
        self.current_chamber = 0
        self.is_game_over = False
        self.winner = None
        self.players = []
        self.current_player_index = 0

    def add_player(self, name):
        if len(self.players) < 6:  # Max 6 players
            self.players.append(name)
            return True
        return False

    def pull_trigger(self):
        if self.is_game_over:
            return {"success": False, "message": "Game is already over"}

        self.current_chamber += 1
        current_player = self.players[self.current_player_index]

        if self.current_chamber == self.bullet_position:
            # Player got the bullet - they lose
            self.is_game_over = True
            remaining_players = [p for i, p in enumerate(self.players) if i != self.current_player_index]
            self.winner = remaining_players[0] if len(remaining_players) == 1 else "Survivors: " + ", ".join(remaining_players)
            return {
                "success": True,
                "result": "bullet",
                "message": f"{current_player} got the bullet! Game Over!",
                "winner": self.winner,
                "game_over": True
            }
        else:
            # Empty chamber - move to next player
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            return {
                "success": True,
                "result": "empty",
                "message": f"{current_player} is safe! Next player's turn.",
                "current_player": self.players[self.current_player_index],
                "game_over": False
            }

# Global game instance
game = RussianRouletteGame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup')
def setup():
    return render_template('setup.html')

@app.route('/game')
def game_page():
    if len(game.players) < 2:
        return redirect(url_for('setup'))
    return render_template('game.html', players=game.players, current_player=game.players[game.current_player_index])

@app.route('/add_player', methods=['POST'])
def add_player():
    data = request.get_json()
    player_name = data.get('name', '').strip()

    if not player_name:
        return jsonify({"success": False, "message": "Player name cannot be empty"})

    if player_name in game.players:
        return jsonify({"success": False, "message": "Player name already exists"})

    if game.add_player(player_name):
        return jsonify({"success": True, "players": game.players})
    else:
        return jsonify({"success": False, "message": "Maximum 6 players allowed"})

@app.route('/start_game', methods=['POST'])
def start_game():
    if len(game.players) < 2:
        return jsonify({"success": False, "message": "At least 2 players required"})

    game.reset_game()
    # Keep the players but reset the game state
    players_copy = game.players.copy()
    game.reset_game()
    game.players = players_copy

    return jsonify({"success": True, "current_player": game.players[0]})

@app.route('/pull_trigger', methods=['POST'])
def pull_trigger():
    result = game.pull_trigger()
    return jsonify(result)

@app.route('/reset_game', methods=['POST'])
def reset_game():
    game.reset_game()
    return jsonify({"success": True, "message": "Game reset successfully"})

@app.route('/get_game_state')
def get_game_state():
    return jsonify({
        "players": game.players,
        "current_player": game.players[game.current_player_index] if game.players else None,
        "is_game_over": game.is_game_over,
        "winner": game.winner,
        "current_chamber": game.current_chamber,
        "total_chambers": game.chamber_count
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8123)
