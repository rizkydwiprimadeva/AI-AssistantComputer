import speech_recognition as srec
import webbrowser
from openai import OpenAI
import pygame
import os
import pyautogui
import edge_tts
import asyncio
import uuid
import pyvts 
import websocket
import json
import glob
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


for f in glob.glob("midori_*.mp3"):
    print("Menghapus:", f)
    try:
        os.remove(f)
    except Exception as e:
        print(e)
        
#/ --- SETTING VTUBE STUDIO ---
plugin_info = {
    "plugin_name": "Midori_AI",
    "developer": "NITRO",
    "authentication_token_path": "./token.txt"
}
vts = pyvts.vts(plugin_info=plugin_info)


#/ Fungsi untuk kirim perintah ke VTube Studio
async def ubah_ekspresi(nama_file):

    print("VTS REQUEST DIKIRIM")
    print(f"Mencoba ubah ke: {nama_file}")

    try:

        hasil = await vts.request({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "MidoriExp",
            "messageType": "ExpressionActivationRequest",
            "data": {
                "expressionFile": nama_file,
                "active": True
            }
        })

        print("HASIL:", hasil)

    except Exception as e:

        print("ERROR:", e)




async def matikan_ekspresi(nama_file):

    try:

        hasil = await vts.request({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "MidoriExpOff",
            "messageType": "ExpressionActivationRequest",
            "data": {
                "expressionFile": nama_file,
                "active": False
            }
        })

        print("EKSPRESI DIMATIKAN:", hasil)

    except Exception as e:
        print("ERROR MATIKAN:", e)

#/ Logika pilih file .exp3.json berdasarkan teks
# Cukup salin fungsi cek_emosi Tuan dan jalankan tes sederhana

#/ api key / base url
client = OpenAI(
    api_key="-",
    base_url="https://api.groq.com/openai/v1"
)
# OPENROUTER API

# INIT MUSIC
pygame.mixer.init()
print("Pygame Init:", pygame.mixer.get_init())
# FUNGSI BICARA EDGE TTS

async def suara_edge(teks):

    file_suara = f"midori_{uuid.uuid4().hex}.mp3"

    communicate = edge_tts.Communicate(
        text=teks,
        voice="id-ID-GadisNeural",
        rate="-1%"
    )

    await communicate.save(file_suara)

    pygame.mixer.music.load(file_suara)
    print("Memutar file:", file_suara)
    pygame.mixer.music.play()
    print("BUSY:", pygame.mixer.music.get_busy())
    print("MULAI PUTAR SUARA")
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    print("SELESAI PUTAR SUARA")
    pygame.mixer.music.unload()

    try:
        os.remove(file_suara)
    except:
        pass


async def ngomong(teks, emosi_file="biasa.exp3.json"):

    print("carlotta :", teks)

    # Aktifkan ekspresi
    await ubah_ekspresi(emosi_file)

    # Bicara
    await suara_edge(teks)

    # Tunggu 4 detik
    await asyncio.sleep(4)

    # Matikan ekspresi yang tadi aktif
    await matikan_ekspresi(emosi_file)

# FUNGSI MENDENGAR
def perintah():

    r = srec.Recognizer()

    with srec.Microphone() as source:

        print("Mendengarkan...")

        r.adjust_for_ambient_noise(source)

        audio = r.listen(
            source,
            phrase_time_limit=5
        )

    try:

         print("Sedang mengenali suara...")

         text = r.recognize_google(
         audio,
         language='id-ID'
        )

         print("User :", text)

         return text.lower()

    except Exception as e:

         print("ERROR MIC:", e)

         return ""

# FUNGSI AI
def tanya_ai(user):

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[

                {
                    "role": "system",
        "content":
        """
        Nama kamu midori.

        Kamu ramah,
        santai,
        natural,
        
        selalu berbicara dengan bahasa indonesia asli
        jika ada kata seperti ajakan , perintah atau halo hai gunakan kata yang sedikit lebih panjang misal haloooo~
        Jawab singkat dan jelas. 
        dan ketika saya bilang hai ada yang bisa aku bantu seperti gitu tanpa midori , nama di gunakan jika aku bertanya nama 

        Di akhir setiap jawaban WAJIB tambahkan salah satu tag berikut:

        [EMOSI:datar]
        [EMOSI:malu]
        [EMOSI:menangis]
        [EMOSI:marah]
        [EMOSI:panik]
        [EMOSI:biasa]
        [EMOSI:murung]
        [EMOSI:ingintertawa]
        [EMOSI:senyumtipismiring]

        Pilih SATU emosi yang paling cocok dengan jawabanmu.
        """
                },

                {
                    "role": "user",
                    "content": user
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        print(e)

        return "Maaf tuan, AI sedang sibuk"

# PROGRAM UTAMA
async def run_michelle():

    global driver


    await asyncio.sleep(2)


    await ngomong("Halloo selamat datang ", "biasa.exp3.json")

    while True:

        user = perintah()

        # JIKA TIDAK ADA SUARA
        if user == "":
            continue

        # PERINTAH TUTUP
        elif "selesai" in user:
           await ngomong("Baik , sampai jumpa.", "senyum.exp3.json")
           break

        # tab apliksi 
        elif "tutup tab sekarang" in user:

            await ngomong("Baik, saya sudah menutup tab yang sedang aktif")             #tutup tab aplikasi 

            pyautogui.hotkey('ctrl', 'w')

        #/ >> YOUTUBE << / BUKA YOUTUBE / CARI YOUTUBE / TUTUP YOUTUBE / SiSTEM PLAY / PAUSE
        # BUKA YOUTUBE
        elif "buka youtube" in user:

            await ngomong("Baik, membuka Youtube")

            if driver is None:

               driver = webdriver.Edge()

               driver.get("https://www.youtube.com")

        # CARI YOUTUBE 
        elif "cari youtube" in user:

            kata = user.replace("cari youtube", "").strip()

            await ngomong(f"Mencari {kata} di Youtube")

            if driver is None:###

               driver = webdriver.Edge()

               driver.get("https://www.youtube.com")

            search_box = driver.find_element(
            By.NAME,
            "search_query"
            )

            search_box.clear()

            search_box.send_keys(kata)
 
            search_box.send_keys(Keys.ENTER)

        # TUTUP YOUTUBE
        elif "tutup youtube" in user:

          if driver is not None:

            await ngomong("Menutup Youtube")

            driver.quit()

            driver = None

        # SISTEM APP / PUTAR / PAUSE / PLAY / FULL SCREEN
        # PUTAR VIDEO DAN KATAKAN NOMOR 1-???
        elif "putar video" in user:

            try:

                nomor = int(
                user.replace("putar video", "").strip()  
                )

                videos = driver.find_elements(
                By.ID,
                "video-title"
                )

                if 1 <= nomor <= len(videos):

                    videos[nomor - 1].click()

                    await ngomong(
                    f"Memutar video nomor {nomor}"  
                    )

                else:

                    await ngomong(
                    "Nomor video tidak ditemukan"
                    )

            except:

                    await ngomong(
                    "Sebutkan nomor videonya tuan"
                    )

        # PAUSE VIDEO
        elif "pause video" in user or "stop video" in user:

            body = driver.find_element(By.TAG_NAME, "body")

            body.send_keys("k")

            await ngomong("Video dijeda")

        # LANJUTKAN VIDEO 
        elif "lanjutkan video" in user or "play video" in user:

            body = driver.find_element(By.TAG_NAME, "body")

            body.send_keys("k")

            await ngomong("Video dilanjutkan")

            
 
        else:
         
          print("MASUK KE AI")

          jawaban = tanya_ai(user)

          print("JAWABAN AI:", jawaban)

          match = re.search(r"\[EMOSI:(.*?)\]", jawaban)

          if match:
             emosi = match.group(1).strip().lower()
          else:
             emosi = "biasa"

          teks_bersih = re.sub(
              r"\[EMOSI:.*?\]",
              "",
              jawaban
          ).strip()

          map_emosi = {
              "datar": "datar.exp3.json",
              "malu": "malu.exp3.json",
              "menangis": "menangis.exp3.json",
              "marah": "marah.exp3.json",
              "panik": "panik.exp3.json",
              "biasa": "biasa.exp3.json",
              "murung": "murung.exp3.json",
              "ingintertawa": "ingintertawa.exp3.json",
              "senyumtipismiring": "senyumtipismiring.exp3.json",
          }

          await ngomong(
                teks_bersih,
                map_emosi.get(emosi, "biasa.exp3.json")
          )

driver = None

async def mulai_sistem():
    try:
        await vts.connect()

        print("MEMINTA TOKEN...")

        hasil = await vts.request_authenticate_token()
        print("TOKEN:", hasil)

        hasil = await vts.request_authenticate()

        print("AUTH:", hasil)

        print("BERHASIL TERHUBUNG DENGAN VTUBE STUDIO")

        await asyncio.sleep(2)

        await run_michelle()

    except Exception as e:
        print("Gagal inisialisasi VTS:", e)

if __name__ == "__main__":
    driver = None
    asyncio.run(mulai_sistem())