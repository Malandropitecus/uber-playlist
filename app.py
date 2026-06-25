import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import streamlit as st
from datetime  import datetime
import requests
from supabase import create_client
import pytz
#Conexión con Supabase - Eliminamos Sqlite3 para mod. bd local en Postgre Cloud


#Credenciales de Spotipy
SPOTIPY_CLIENT_ID = st.secrets.get("SPOTIPY_CLIENT_ID") or os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = st.secrets.get("SPOTIPY_CLIENT_SECRET") or os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = st.secrets.get("SPOTIPY_REDIRECT_URI") or os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIPY_REFRESH_TOKEN = st.secrets.get("SPOTIPY_REFRESH_TOKEN") or os.getenv("SPOTIPY_REFRESH_TOKEN")

#Credenciales de Supabase - Postgree DB
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)



#sp es el objeto que permite la interacion con la API de Spotify
#sp + un metodo es una peticion a la API de Spotify
sp_search = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

def get_access_token():
    response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": SPOTIPY_REFRESH_TOKEN,
        "client_id": SPOTIPY_CLIENT_ID,
        "client_secret": SPOTIPY_CLIENT_SECRET
    })
    return response.json()["access_token"]

sp = spotipy.Spotify(auth=get_access_token())

#Identificador que se mostró al iniciar la conexión con spotify desde el inicio
SPOTIFY_USER_ID = "eds69eac9ezdoh2fk34swimo7"

#El identificador del playlist se guardará en esta variable para guardar canciones aquí
PLAYLIST_ID = "6GlExWsI0WRdPmLPmMK6zo"

#Muestra el título en grande en la página web
st.title(' 🎧 Uber Playlist')

st.subheader("¿Qué canción te gustaría escuchar en este viaje?")

edad = st.number_input("Tu edad", min_value=0, max_value=100, step=1)

cancion =  st.text_input("🔍 Busca tu canción o artista")

if st.button ("Buscar"):
    if cancion == "":
        st.error ("Escribe el nombre de una canción o artista")
    else:
        resultados = sp.search(q=cancion, type="track", limit=10)
        st.session_state.resultados = resultados

#Aquí mostramos las canciones si es que hay resultados guardados
if "resultados" in st.session_state:
    #Enumerate enumera las canciones para identificarlas
    for i, track in enumerate(st.session_state.resultados["tracks"]["items"]):
        #Dividimos en 3 columnas, una ancha (4) y dos angostas(1,1)
        col1, col2, col3 = st.columns([3,1,1])
        #En la columna ancha mostramos el nombre de la canción y el artista
        with col1:
            st.write(f"🎵 {track['name']} - {track['artists'][0]['name']}")
        #En la columna angosta mostramos un botón para agregar la canción
        with col2:
            if st.button("➕ Agregar", key=f"btn_{i}"):
                #Esto para analizar tendencias por mes, analizar datos por año y que le gusta a la gente dada cierta hora
                zona = pytz.timezone("America/Chihuahua")
                ahora = datetime.now(zona)
                fecha = ahora.strftime("%d/%m/%Y")
                hora = ahora.strftime("%H:%M")
                dia = ahora.strftime("%A")
                # Insertamos los datos en la tabla "canciones", cambiamos por método supabase
                supabase_client.table("canciones").insert({ #Insertamos los datos en la tabla "canciones"
                    "cancion": track['name'],
                    "artista": track['artists'][0]['name'],
                    "edad": edad,
                    "fecha": fecha,
                    "hora": hora,
                    "dia": dia
                }).execute() #Ejecuta la operación
                #Con esta linea agregamos la canción a la playlist
                sp.playlist_add_items(PLAYLIST_ID, [track['uri']])
                #Aquí separamos la columna para que no se amontone mucho lo visual
                with col3: st.success(f"¡Canción agregada!")
                


        

