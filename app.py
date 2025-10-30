from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "8142007006:AAEcJSgodwzhkskMszVbQWzCkgRqpiN8jTA"
CHAT_ID = "-1003080056473"

MENU_PIZZE = {
    "Marinara": 4.5, "Margherita": 4.5, "Prosciutto": 7.0,
    "Prosciutto e Funghi": 7.5, "Quattro Stagioni": 8.0, "Tartufata": 8.0,
    "Bismark": 7.5, "Prosciutto e Panna": 7.5, "Prosciutto e Ananas": 7.5,
    "Capricciosa": 9.0, "Nord Sud": 7.0, "Salame": 7.0,
    "Diavola": 7.5, "Inca**zzata": 8.0, "Ghiotta": 8.0,
    "Salsiccia": 7.0, "Salsiccia e Friarielli": 9.0, "Medmac": 8.0,
    "Rustica": 8.0, "Italia": 7.5, "Boscaiola": 8.5,
    "Bomba": 8.5, "Napoli": 6.5, "Siciliana": 6.5,
    "Romana": 7.5, "Pugliese": 6.5, "Tonno e Cipolla": 7.5,
    "Patatosa": 7.0, "Americana": 8.0, "Tre Stella": 8.0,
    "Affumicata": 8.0, "Tirolese": 9.0, "Quattro Formaggi": 9.0,
    "Bufala": 8.0, "Gennaro": 10.0, "Braccio di Ferro": 8.0,
    "Biancaneve": 7.5, "Gorgonzola": 7.5, "Fantasia": 9.0,
    "Zola e Noci": 8.0, "Zola e Pera": 8.0, "Zola e Miele": 8.0,
    "Speck": 7.5, "Crudo": 8.0, "Valtellina": 9.0,
    "Modo Mio": 10.0, "Porcini": 8.0, "Rucola": 7.0,
    "Primavera": 7.5, "Campagnola": 8.0, "Vegetariana": 8.0,
    "Parmigiana": 8.0, "Canadese": 8.5, "Mare Chiaro": 8.5,
    "Frutti di Mare": 10.0, "Viagra": 9.0, "Pesto": 7.0,
    "Pizza Kebab": 10.0
}

@app.route('/')
def index():
    return render_template('index.html', menu=MENU_PIZZE)

@app.route('/invia-ordine', methods=['POST'])
def invia_ordine():
    try:
        data = request.json
        
        tipo = data['tipo']
        nome = data['nome']
        telefono = data['telefono']
        orario = data['orario']
        carrello = data['carrello']
        costo_extra = float(data.get('costoExtra', 0))
        
        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        totale_pizze = sum(MENU_PIZZE[p['nome']] * p['qty'] for p in carrello)
        totale_finale = totale_pizze + costo_extra
        
        if tipo == 'ritiro':
            messaggio = f"🍕 *NUOVO ORDINE - RITIRO* 🍕\n\n"
        else:
            messaggio = f"🍕 *NUOVO ORDINE - CONSEGNA* 🍕\n\n"
        
        messaggio += f"📅 {now}\n\n"
        messaggio += "*👤 Cliente:*\n"
        messaggio += f"Nome: {nome}\n"
        messaggio += f"Tel: {telefono}\n"
        messaggio += f"Orario: {orario}\n"
        
        if tipo == 'consegna':
            via = data.get('via', '')
            numero = data.get('numero', '')
            citofono = data.get('citofono', '')
            messaggio += f"\n*📍 Indirizzo:*\n"
            messaggio += f"{via}, {numero}\n"
            if citofono:
                messaggio += f"Citofono: {citofono}\n"
        
        messaggio += "\n*🍕 Pizze:*\n"
        
        idx = 0
        for pizza in carrello:
            for i in range(pizza['qty']):
                idx += 1
                if pizza.get('note'):
                    messaggio += f"{idx}. {pizza['nome']} - €{MENU_PIZZE[pizza['nome']]:.2f}\n   _({pizza['note']})_\n"
                else:
                    messaggio += f"{idx}. {pizza['nome']} - €{MENU_PIZZE[pizza['nome']]:.2f}\n"
        
        messaggio += f"\n*💶 Totale pizze:* €{totale_pizze:.2f}"
        
        if costo_extra > 0:
            messaggio += f"\n*🚗 Consegna:* €{costo_extra:.2f}"
        
        messaggio += f"\n\n*💰 TOTALE: €{totale_finale:.2f}*"
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": messaggio,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return jsonify({"success": True, "totale": totale_finale})
        else:
            return jsonify({"success": False, "error": f"Errore {response.status_code}"}), 500
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
