import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import streamlit as st
from datetime  import datetime
import sqlite3

#Conexión con base de datos
conn = sqlite3.connect("playlist.db")
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS canciones (
        "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
        "cancion"	TEXT,
        "artista"	TEXT,
        "edad"	INTEGER,
        "fecha"	TEXT,
        "hora"	TEXT,
        "dia"	TEXT
)
''')

conn.commit()

SPOTIPY_CLIENT_ID = st.secrets.get("SPOTIPY_CLIENT_ID") or os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = st.secrets.get("SPOTIPY_CLIENT_SECRET") or os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = st.secrets.get("SPOTIPY_REDIRECT_URI") or os.getenv("SPOTIPY_REDIRECT_URI")

#sp es el objeto que permite la interacion con la API de Spotify
#sp + un metodo es una peticion a la API de Spotify
sp_search = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-modify-public playlist-modify-private"
))

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
                ahora = datetime.now()
                fecha = ahora.strftime("%d/%m/%Y")
                hora = ahora.strftime("%H:%M")
                dia = ahora.strftime("%A")
                # Insertamos los datos en la tabla "canciones"
                c.execute('''
                    INSERT INTO canciones (cancion, artista, edad, fecha, hora, dia)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (track['name'], track['artists'][0]['name'], edad, fecha, hora, dia))
                #Confirmamos la inserción en la base de datos
                conn.commit()
                #Con esta linea agregamos la canción a la playlist
                sp.playlist_add_items(PLAYLIST_ID, [track['uri']])
                #Aquí separamos la columna para que no se amontone mucho lo visual
                with col3: st.success(f"¡Canción agregada!")
                


        

