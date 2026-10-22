
import paho.mqtt.client as paho
import json
import streamlit as st
import numpy as np
from PIL import Image
from keras.models import load_model

# Configuracion MQTT
BROKER = "broker.mqttdashboard.com"
PORT = 1883
TOPIC = "IMIA"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT")
    else:
        print("Error de conexion MQTT:", rc)

def on_publish(client, userdata, mid):
    print("Mensaje publicado. ID:", mid)

@st.cache_resource
def crear_cliente():
    # Sintaxis compatible con versiones anteriores de paho-mqtt
    cliente = paho.Client("APP_CERR")
    cliente.on_connect = on_connect
    cliente.on_publish = on_publish
    cliente.connect(BROKER, PORT, 60)
    cliente.loop_start()
    return cliente

def enviar_gesto(gesto):
    try:
        cliente = crear_cliente()
        mensaje = json.dumps({"gesto": gesto})

        info = cliente.publish(
            TOPIC,
            mensaje,
            qos=0,
            retain=False
        )

        info.wait_for_publish(timeout=3)

        if info.rc == paho.MQTT_ERR_SUCCESS:
            st.success(f"Comando enviado: {gesto}")
            print("Publicado en", TOPIC, ":", mensaje)
        else:
            st.error(f"Error al publicar MQTT: {info.rc}")

    except Exception as error:
        st.error(f"Error MQTT: {error}")

st.title("Cerradura Inteligente")
st.caption(f"Broker: {BROKER} | Puerto: {PORT} | Topico: {TOPIC}")

@st.cache_resource
def cargar_modelo():
    return load_model("keras_model.h5")

try:
    model = cargar_modelo()
except Exception as error:
    st.error(f"No se pudo cargar keras_model.h5: {error}")
    st.stop()

img_file_buffer = st.camera_input("Toma una foto para reconocer el gesto")

if img_file_buffer is not None:
    img = Image.open(img_file_buffer).convert("RGB")
    img = img.resize((224, 224))

    img_array = np.asarray(img, dtype=np.float32)
    normalized_image_array = (img_array / 127.0) - 1.0

    data = np.ndarray(
        shape=(1, 224, 224, 3),
        dtype=np.float32
    )
    data[0] = normalized_image_array

    prediction = model.predict(data, verbose=0)
    st.write("Prediccion:", prediction.tolist())

    if prediction[0][0] > 0.3:
        st.header("Abriendo")
        enviar_gesto("Abre")

    elif prediction[0][1] > 0.3:
        st.header("Cerrando")
        enviar_gesto("Cierra")

    else:
        st.warning("No se reconocio un gesto con suficiente confianza.")


