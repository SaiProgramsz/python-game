from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Game variables
WIDTH = 800
HEIGHT = 600
PLAYER_SIZE = 50
ENEMY_SIZE = 30
BULLET_SIZE = 10
PLAYER_SPEED = 5
ENEMY_SPEED = 3
BULLET_SPEED = 10
FPS = 30

player_x = WIDTH // 2 - PLAYER_SIZE // 2
player_y = HEIGHT - PLAYER_SIZE - 20  # Slightly above the bottom
enemies = []
bullets = []
score = 0

def create_enemy():
    x = random.randint(0, WIDTH - ENEMY_SIZE)
    y = random.randint(50, 200) # Enemies spawn in the top part
    enemies.append({"x": x, "y": y})

for _ in range(5): # Start with 5 enemies
  create_enemy()

@app.route("/")
def index():
    return render_template("game.html")

@app.route("/game_data")
def game_data():
    return jsonify({
        "player_x": player_x,
        "player_y": player_y,
        "enemies": enemies,
        "bullets": bullets,
        "score": score,
        "width": WIDTH,
        "height": HEIGHT,
        "player_size": PLAYER_SIZE,
        "enemy_size": ENEMY_SIZE,
        "bullet_size": BULLET_SIZE
    })

@app.route("/update_player", methods=["POST"])
def update_player():
    global player_x
    data = request.get_json()
    player_x = data["x"]
    return jsonify({"status": "ok"})

@app.route("/shoot", methods=["POST"])
def shoot():
    global bullets
    bullet_x = player_x + PLAYER_SIZE // 2 - BULLET_SIZE // 2
    bullet_y = player_y - BULLET_SIZE
    bullets.append({"x": bullet_x, "y": bullet_y})
    return jsonify({"status": "ok"})

@app.route("/update_game", methods=["POST"])
def update_game():
    global enemies, bullets, score

    # Move bullets
    bullets_to_remove = []
    for i, bullet in enumerate(bullets):
        bullet["y"] -= BULLET_SPEED
        if bullet["y"] < 0:
            bullets_to_remove.append(i)

    # Remove off-screen bullets (iterate in reverse to avoid index issues)
    for i in sorted(bullets_to_remove, reverse=True):
        del bullets[i]

    # Move enemies and handle collisions
    enemies_to_remove = []
    for i, enemy in enumerate(enemies):
        enemy["y"] += ENEMY_SPEED

        # Enemy off-screen (game over - you might want to handle this differently)
        if enemy["y"] > HEIGHT:
           return jsonify({"game_over": True}) # Indicate game over

        # Bullet collision
        bullets_to_remove = []
        for j, bullet in enumerate(bullets):
            if (
                bullet["x"] < enemy["x"] + ENEMY_SIZE
                and bullet["x"] + BULLET_SIZE > enemy["x"]
                and bullet["y"] < enemy["y"] + ENEMY_SIZE
                and bullet["y"] + BULLET_SIZE > enemy["y"]
            ):
                enemies_to_remove.append(i)
                bullets_to_remove.append(j)
                score += 1
                break  # Only one bullet can hit an enemy at a time

        # Remove hit bullets
        for k in sorted(bullets_to_remove, reverse=True):
            del bullets[k]

    # Remove hit enemies (iterate in reverse to avoid index issues)
    for i in sorted(enemies_to_remove, reverse=True):
        del enemies[i]
        create_enemy() # Replace the enemy

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
