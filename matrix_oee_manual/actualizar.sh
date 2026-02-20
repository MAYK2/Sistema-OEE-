#!/bin/bash

echo "----------------------------------------"
echo "🔄 ACTUALIZANDO SISTEMA MATRIX OEE..."
echo "----------------------------------------"

# 1. Matar el proceso que ocupa el puerto 5052
PID=$(lsof -t -i:5052)

if [ -z "$PID" ]; then
    echo "✅ El puerto 5052 estaba libre."
else
    echo "⚠️ Se encontró proceso corriendo (PID $PID). Matándolo..."
    kill -9 $PID
    sleep 1
    echo "💀 Proceso anterior eliminado."
fi

# 2. (Opcional) Activar entorno virtual si no está activo
# source venv/bin/activate 

# 3. Iniciar el nuevo proceso con Nohup
echo "🚀 Iniciando nuevo servidor..."
nohup venv/bin/python run.py >> matrix_oee_manual.log 2>&1 &

# 4. Esperar un momento y mostrar si arrancó
sleep 2
echo "----------------------------------------"
echo "📊 ESTADO DEL LOG (Últimas 5 líneas):"
echo "----------------------------------------"
tail -n 5 matrix_oee_manual.log
echo "----------------------------------------"
echo "✅ ¡LISTO! Si ves 'Running on...', ya puedes entrar."
