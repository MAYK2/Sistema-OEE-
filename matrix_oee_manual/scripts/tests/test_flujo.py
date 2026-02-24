import requests

BASE_URL = 'http://127.0.0.1:5000/api/orders'

def probar_sistema():
    print("--- 1. CREANDO ORDEN DE TRABAJO (OT) ---")
    nueva_ot = {
        "ot_number": "OT-PRUEBA-AUTO",
        "client_name": "Cliente Juan",
        "product_id": 1,
        "phone": "555-1234"
    }
    
    try:
        resp = requests.post(BASE_URL, json=nueva_ot)
        if resp.status_code == 201:
            print(f"✅ OT Creada: {resp.json()}")
            ot_id = resp.json()['id']
        else:
            print(f"❌ Error creando OT: {resp.text}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar. ¿Está corriendo 'python run.py' en la otra terminal?")
        return

    print("\n--- 2. OPERARIO INICIA LA ORDEN ---")
    # El operario pulsa "Iniciar"
    datos_inicio = {"operator_count": 2}
    resp = requests.post(f"{BASE_URL}/{ot_id}/start", json=datos_inicio)
    print(f"Respuesta Inicio: {resp.status_code} - {resp.json()}")

    print("\n--- 3. REGISTRANDO UNA PARADA ---")
    # Simulamos parada
    parada = {
        "stage": "ejecucion",
        "type": "improductivo",
        "reason": "Atasco de bidones",
        "duration_minutes": 10
    }
    resp = requests.post(f"{BASE_URL}/{ot_id}/downtime", json=parada)
    print(f"Respuesta Parada: {resp.status_code} - {resp.json()}")

    print("\n--- 4. FINALIZANDO ORDEN ---")
    datos_fin = {
        "total_produced": 100,
        "total_defective": 5
    }
    resp = requests.post(f"{BASE_URL}/{ot_id}/stop", json=datos_fin)
    print(f"🏁 Resultado Final: {resp.json()}")

if __name__ == "__main__":
    probar_sistema()
