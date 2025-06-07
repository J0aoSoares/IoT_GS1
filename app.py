from flask import Flask, request, redirect
from flask_mqtt import Mqtt
from datetime import datetime

app = Flask(__name__)
alerts = []
latest_value = "0.000"

# Configurações do MQTT
app.config['MQTT_BROKER_URL'] = 'test.mosquitto.org'
app.config['MQTT_BROKER_PORT'] = 1883
mqtt = Mqtt(app)

# Callback quando recebe uma mensagem
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global latest_value
    payload = message.payload.decode()
    latest_value = payload

    
    try:
        voltage = float(payload)
        if voltage < 1.5:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            alerts.append(f"[{timestamp}] ⚠️ Tensão baixa detectada: {voltage:.3f}V")
    except ValueError:
        pass

# Inicia a escuta no tópico
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("Pot_read")

@app.route("/")
def index():
    return f"""
    <html>
    <head>
        <title>Monitoramento</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #1e1e1e;
                padding: 30px;
                color: #f0f0f0;
            }}

            .card {{
                background: #2c2c2c;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 0 15px rgba(0,0,0,0.5);
                max-width: 800px;
                margin: auto;
            }}

            h1 {{
                color: #00bcd4;
                margin-top: 0;
            }}

            h2 {{
                color: #f0f0f0;
                border-top: 1px solid #444;
                padding-top: 10px;
            }}

            .volt {{
                font-size: 24px;
                color: #4caf50;
                margin-bottom: 20px;
            }}

            ul {{
                padding-left: 20px;
                list-style-type: square;
            }}

            li {{
                margin-bottom: 10px;
            }}

            button {{
                margin: 5px;
                padding: 10px 15px;
                font-size: 16px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                transition: 0.3s ease;
            }}

            .refresh {{
                background-color: #4CAF50;
                color: white;
            }}

            .refresh:hover {{
                background-color: #45a049;
            }}

            .clear {{
                background-color: #f44336;
                color: white;
            }}

            .clear:hover {{
                background-color: #d32f2f;
            }}

            .export {{
                background-color: #2196F3;
                color: white;
            }}

            .export:hover {{
                background-color: #1976d2;
            }}

            .viewall {{
                background-color: #9c27b0;
                color: white;
            }}

            .viewall:hover {{
                background-color: #7b1fa2;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>SIGRFE - Monitoramento em Tempo Real</h1>
            <p class="volt">Última leitura de tensão: <b>{latest_value} V</b></p>

            <form method="post" action="/limpar" style="display: inline;">
                <button class="clear" type="submit">🧹 Limpar Alertas</button>
            </form>
            <form method="post" action="/exportar" style="display: inline;">
                <button class="export" type="submit">💾 Exportar Alertas</button>
            </form>
            <button class="viewall" onclick="window.location='/todos'">📋 Ver Todos</button>
            <button class="refresh" onclick="location.reload()">🔄 Atualizar</button>

            <h2>Últimos Alertas:</h2>
            <ul>
                {''.join(f"<li>{a}</li>" for a in alerts[-5:] or ["Nenhum alerta ainda."])}
            </ul>
        </div>
    </body>
    </html>
    """

@app.route("/limpar", methods=["POST"])
def limpar():
    global alerts
    alerts = []
    return redirect("/")

@app.route("/exportar", methods=["POST"])
def exportar():
    with open("alertas.txt", "w") as f:
        for alerta in alerts:
            f.write(alerta + "\n")
    return redirect("/")

@app.route("/todos")
def todos():
    return "<br>".join(alerts) or "Nenhum alerta ainda."

if __name__ == "__main__":
    app.run(debug=True)
