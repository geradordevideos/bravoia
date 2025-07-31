# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, send_file
from moviepy.editor import *
import os, uuid, pyttsx3

app = Flask(__name__)

def salvar_audio_com_pyttsx3(texto, caminho):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    voices = engine.getProperty('voices')
    for voice in voices:
        if "brazil" in voice.name.lower() or "pt" in voice.languages[0].lower():
            engine.setProperty('voice', voice.id)
            break
    engine.save_to_file(texto, caminho)
    engine.runAndWait()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        trechos = request.form['texto'].splitlines()
        formato = request.form.get('formato', 'youtube')

        formatos = {
            "youtube": (1280, 720),
            "reels": (720, 1280),
            "quadrado": (720, 720)
        }
        tamanho = formatos.get(formato, (1280, 720))

        clipes = []

        for trecho in trechos:
            if not trecho.strip():
                continue
            video_id = str(uuid.uuid4())
            audio_path = f"audio_{video_id}.mp3"
            salvar_audio_com_pyttsx3(trecho.strip(), audio_path)

            audio = AudioFileClip(audio_path)
            duracao = audio.duration

            if os.path.exists("static/fundo.mp4"):
                fundo = VideoFileClip("static/fundo.mp4").subclip(0, duracao).resize(tamanho)
            else:
                fundo = ColorClip(size=tamanho, color=(0, 0, 0), duration=duracao)

            txt = TextClip(trecho.strip(), fontsize=48, color='white', size=tamanho, method='caption', align='center')
            txt = txt.set_duration(duracao).set_position(("center", "bottom"))

            clipe_final = CompositeVideoClip([fundo, txt]).set_audio(audio)
            clipes.append(clipe_final)

        video_completo = concatenate_videoclips(clipes, method="compose")
        video_final_path = f"video_{uuid.uuid4()}.mp4"
        video_completo.write_videofile(video_final_path, fps=24)

        for f in os.listdir():
            if f.startswith("audio_") and f.endswith(".mp3"):
                os.remove(f)

        return send_file(video_final_path, as_attachment=True)

    return render_template('index.html')