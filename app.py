from flask import Flask, render_template_string, Response

app = Flask(__name__)

# Service Worker Code (Saves everything locally so it loads offline)
SW_SCRIPT = """
const CACHE_NAME = 'kimvone-offline-v2';
const ASSETS = [
    '/',
    '/manifest.json'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
"""

# Web App Manifest
MANIFEST_JSON = """{
  "name": "Kimvone Free App",
  "short_name": "Kimvone",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#000000",
  "theme_color": "#00e676",
  "icons": [
    {
      "src": "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=192&h=192&q=80",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}"""

GAMING_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kimvone Free App - Offline & Online Hub</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#00e676">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #000000; color: #ffffff; padding: 15px; margin: 0; }
        
        .navbar { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1a1a1a; padding-bottom: 12px; margin-bottom: 15px; }
        .logo { color: #00e676; font-size: 20px; font-weight: bold; letter-spacing: 0.5px; }
        .offline-status { background: #111; border: 1px solid #00e676; color: #00e676; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; }

        /* Search Box */
        .search-box { width: 100%; margin-bottom: 15px; box-sizing: border-box; }
        .search-box input { 
            width: 100%; 
            padding: 12px 16px; 
            font-size: 15px; 
            border: 1px solid #222; 
            border-radius: 12px; 
            background: #0a0a0a; 
            color: #fff; 
            outline: none; 
            box-sizing: border-box;
        }

        .section-title { font-size: 14px; color: #00e676; text-transform: uppercase; letter-spacing: 1px; margin: 20px 0 10px 0; font-weight: bold; }

        /* Grid */
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .game-card { background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; }
        .card-body { padding: 12px; display: flex; flex-direction: column; justify-content: space-between; flex-grow: 1; }
        .game-card h3 { color: #fff; font-size: 13px; margin: 0 0 4px 0; font-weight: 600; }
        .game-card p { color: #888; font-size: 10px; margin: 0 0 10px 0; line-height: 1.2; }
        
        .play-btn { background: #00e676; color: #000; border: none; padding: 10px 0; border-radius: 6px; font-weight: bold; font-size: 12px; text-align: center; text-decoration: none; display: block; width: 100%; cursor: pointer; text-transform: uppercase; }
        .offline-tag { background: #222; color: #00e676; font-size: 9px; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-bottom: 5px; font-weight: bold; }

        /* Game Modal */
        .game-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 2000; flex-direction: column; align-items: center; justify-content: center; }
        .game-header { width: 100%; display: flex; justify-content: space-between; padding: 15px; box-sizing: border-box; background: #111; border-bottom: 1px solid #00e676; }
        .close-btn { background: #ff1744; color: #fff; border: none; padding: 6px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        canvas { background: #111; border: 2px solid #00e676; margin-top: 20px; border-radius: 8px; }
    </style>
</head>
<body>

    <div class="navbar">
        <div class="logo">Kimvone Free App</div>
        <div class="offline-status">⚡ 100% Offline Ready</div>
    </div>

    <div class="search-box">
        <input type="text" id="gameSearch" onkeyup="filterGames()" placeholder="Search action games...">
    </div>

    <!-- 100% Offline Action Games (Work Without Data) -->
    <div class="section-title">⚡ Instant Offline Games (Zero Data)</div>
    <div class="grid" id="offlineGrid">
        <div class="game-card">
            <div class="card-body">
                <div>
                    <span class="offline-tag">WORKS OFFLINE</span>
                    <h3>Space Combat Shooter</h3>
                    <p>Arcade space combat action. Play without data.</p>
                </div>
                <button class="play-btn" onclick="startShooter()">▶ PLAY</button>
            </div>
        </div>

        <div class="game-card">
            <div class="card-body">
                <div>
                    <span class="offline-tag">WORKS OFFLINE</span>
                    <h3>Street Road Racer</h3>
                    <p>High-speed driving and dodging game offline.</p>
                </div>
                <button class="play-btn" onclick="startRacer()">▶ PLAY</button>
            </div>
        </div>
    </div>

    <!-- Online & Cloud Action Games -->
    <div class="section-title">🌐 Online 3D & GTA Hub (Needs Data)</div>
    <div class="grid" id="onlineGrid">
        <div class="game-card">
            <div class="card-body">
                <div>
                    <span class="offline-tag" style="background:#221111; color:#ff1744;">ONLINE MULTIPLAYER</span>
                    <h3>Grand Shift Auto 3D</h3>
                    <p>Open world crime city & vehicle driving.</p>
                </div>
                <a class="play-btn" href="https://playgama.com/category/gta" target="_blank">▶ PLAY ONLINE</a>
            </div>
        </div>

        <div class="game-card">
            <div class="card-body">
                <div>
                    <span class="offline-tag" style="background:#221111; color:#ff1744;">ONLINE MULTIPLAYER</span>
                    <h3>Venge 3D Tactical FPS</h3>
                    <p>Multiplayer 3D combat shooter arena.</p>
                </div>
                <a class="play-btn" href="https://venge.io/" target="_blank">▶ PLAY ONLINE</a>
            </div>
        </div>
    </div>

    <!-- Built-in Game Modal Canvas -->
    <div id="gameModal" class="game-modal">
        <div class="game-header">
            <h3 id="modalTitle" style="margin:0; color:#00e676;">Game</h3>
            <button class="close-btn" onclick="closeGame()">Close ✕</button>
        </div>
        <canvas id="gameCanvas" width="300" height="400"></canvas>
        <p style="font-size: 12px; color: #888; margin-top: 10px;">Swipe or touch screen to control!</p>
    </div>

    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }

        function filterGames() {
            let input = document.getElementById('gameSearch').value.toLowerCase();
            let cards = document.getElementsByClassName('game-card');
            for (let i = 0; i < cards.length; i++) {
                let title = cards[i].getElementsByTagName('h3')[0].innerText.toLowerCase();
                if (title.includes(input)) {
                    cards[i].style.display = "flex";
                } else {
                    cards[i].style.display = "none";
                }
            }
        }

        let canvas = document.getElementById("gameCanvas");
        let ctx = canvas.getContext("2d");
        let gameInterval;
        let gameType = "";

        function closeGame() {
            document.getElementById("gameModal").style.display = "none";
            clearInterval(gameInterval);
        }

        // Space Shooter Game
        function startShooter() {
            document.getElementById("modalTitle").innerText = "Space Combat Shooter";
            document.getElementById("gameModal").style.display = "flex";
            gameType = "shooter";
            
            let p = { x: 135, y: 340 };
            let bullets = [];
            let enemies = [];

            canvas.onmousemove = canvas.ontouchmove = (e) => {
                let rect = canvas.getBoundingClientRect();
                let clientX = e.touches ? e.touches[0].clientX : e.clientX;
                p.x = clientX - rect.left - 15;
            };

            if (gameInterval) clearInterval(gameInterval);
            gameInterval = setInterval(() => {
                ctx.clearRect(0, 0, 300, 400);
                
                // Player
                ctx.fillStyle = "#00e676";
                ctx.fillRect(p.x, p.y, 30, 30);

                // Auto bullet
                if (Math.random() < 0.25) bullets.push({ x: p.x + 12, y: p.y });

                ctx.fillStyle = "#fff";
                bullets.forEach((b, i) => {
                    b.y -= 8;
                    ctx.fillRect(b.x, b.y, 6, 10);
                    if (b.y < 0) bullets.splice(i, 1);
                });

                if (Math.random() < 0.06) enemies.push({ x: Math.random() * 270, y: 0 });

                ctx.fillStyle = "#ff1744";
                enemies.forEach((en, i) => {
                    en.y += 4;
                    ctx.fillRect(en.x, en.y, 25, 25);
                    if (en.y > 400) enemies.splice(i, 1);
                });
            }, 30);
        }

        // Road Racer Game
        function startRacer() {
            document.getElementById("modalTitle").innerText = "Street Road Racer";
            document.getElementById("gameModal").style.display = "flex";
            gameType = "racer";

            let carX = 135;
            let obstacles = [];

            canvas.onmousemove = canvas.ontouchmove = (e) => {
                let rect = canvas.getBoundingClientRect();
                let clientX = e.touches ? e.touches[0].clientX : e.clientX;
                carX = clientX - rect.left - 15;
            };

            if (gameInterval) clearInterval(gameInterval);
            gameInterval = setInterval(() => {
                ctx.clearRect(0, 0, 300, 400);

                // Road lines
                ctx.strokeStyle = "#444";
                ctx.setLineDash([20, 20]);
                ctx.beginPath(); ctx.moveTo(150, 0); ctx.lineTo(150, 400); ctx.stroke();

                // Player Car
                ctx.fillStyle = "#00e676";
                ctx.fillRect(carX, 320, 30, 50);

                // Obstacle Cars
                if (Math.random() < 0.04) {
                    obstacles.push({ x: Math.random() * 250, y: -50 });
                }

                ctx.fillStyle = "#3388ff";
                obstacles.forEach((ob, i) => {
                    ob.y += 5;
                    ctx.fillRect(ob.x, ob.y, 30, 50);
                    if (ob.y > 400) obstacles.splice(i, 1);
                });
            }, 30);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(GAMING_TEMPLATE)

@app.route('/sw.js')
def service_worker():
    return Response(SW_SCRIPT, mimetype='application/javascript')

@app.route('/manifest.json')
def manifest():
    return Response(MANIFEST_JSON, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
