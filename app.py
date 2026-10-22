
import json
import streamlit as st
import paho.mqtt.client as mqtt

st.set_page_config(
    page_title="Control MQTT",
    page_icon="🎛️",
    layout="centered"
)

# Mantener estos datos iguales a los del ESP32
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
MQTT_TOPIC = "IMIA"

st.title("🎛️ Control de actuadores")
st.subheader("Control de servo y luces mediante MQTT")

@st.cache_resource
def crear_cliente():
    cliente = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="StreamlitControlIMIA"
    )
    cliente.connect(MQTT_BROKER, MQTT_PORT, 60)
    cliente.loop_start()
    return cliente

def enviar_comando(datos):
    try:
        cliente = crear_cliente()
        mensaje = json.dumps(datos)
        resultado = cliente.publish(
            MQTT_TOPIC,
            mensaje,
            qos=0
        )
        resultado.wait_for_publish(timeout=3)

        if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
            st.success(f"Comando enviado: {mensaje}")
        else:
            st.error("No se pudo publicar el mensaje MQTT.")

    except Exception as error:
        st.error(f"Error de conexión MQTT: {error}")

st.caption(
    f"Broker: {MQTT_BROKER} | Puerto: {MQTT_PORT} | "
    f"Tópico: {MQTT_TOPIC}"
)

col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 ABRIR", use_container_width=True):
        enviar_comando({"gesto": "Abre"})

with col2:
    if st.button("🔴 CERRAR", use_container_width=True):
        enviar_comando({"gesto": "Cierra"})

st.divider()

st.subheader("Posición del servo")

angulo = st.slider(
    "Selecciona el ángulo",
    min_value=0,
    max_value=180,
    value=90,
    step=5
)

st.write(f"Ángulo seleccionado: **{angulo}°**")

if st.button("Enviar ángulo", use_container_width=True):
    enviar_comando({
        "gesto": "Angulo",
        "angulo": angulo
    })

