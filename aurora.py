import os
import webbrowser
import speech_recognition as sr
import pyttsx3
from datetime import datetime
from dotenv import load_dotenv

# NOVA BIBLIOTECA DO GOOGLE
from google import genai
from google.genai import types

# ==========================================
# 1. CONFIGURAÇÕES E SEGURANÇA
# ==========================================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERRO: Chave GEMINI_API_KEY não encontrada no arquivo .env")
    exit()

# Configura o Cérebro (Gemini) usando o Novo SDK
try:
    client = genai.Client(api_key=api_key)
    print("✅ Cérebro da Aurora configurado com sucesso!")
except Exception as e:
    print(f"❌ Erro na configuração do Gemini: {e}")
    exit()

# ==========================================
# 2. MOTOR DE VOZ (SAÍDA)
# ==========================================
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "brazil" in voice.name.lower() or "portuguese" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 185)

def speak(text):
    """Faz a Aurora falar e imprime no terminal"""
    print(f"🌌 Aurora: {text}")
    engine.say(text)
    engine.runAndWait()

# ==========================================
# 3. RECONHECIMENTO DE VOZ (ENTRADA)
# ==========================================
def listen():
    """Captura o áudio do microfone e transforma em texto"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎙️ Ouvindo... (Pode falar)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio, language='pt-BR')
            print(f"👤 Você (Voz): {query}")
            return query.lower()
        except Exception:
            return ""

# ==========================================
# 4. AUTOMAÇÃO LOCAL
# ==========================================
def executar_comandos_locais(comando):
    """Ações rápidas sem gastar API"""
    if 'que horas são' in comando or 'horário' in comando:
        hora = datetime.now().strftime('%H:%M')
        speak(f"Agora são {hora}")
        return True
    elif 'abrir youtube' in comando:
        speak("Abrindo o YouTube.")
        webbrowser.open("https://www.youtube.com")
        return True
    elif 'abrir meu github' in comando:
        speak("Abrindo seu GitHub, Diego.")
        webbrowser.open("https://github.com/21Programe")
        return True
    elif 'pesquisar por' in comando:
        termo = comando.replace('pesquisar por', '').strip()
        speak(f"Pesquisando {termo} no Google.")
        webbrowser.open(f"https://www.google.com/search?q={termo}")
        return True
    return False

# ==========================================
# 5. LOOP HÍBRIDO 
# ==========================================
def start_aurora():
    speak("Sistemas prontos. Modo híbrido ativado.")
    
    while True:
        print("\n" + "-"*30)
        print("⌨️  Digite algo ou aperte [ENTER] para falar:")
        entrada = input(">> ").strip()

        if entrada:
            comando = entrada.lower()
        else:
            comando = listen()

        if not comando:
            continue

        if any(p in comando for p in ["desligar", "sair", "parar"]):
            speak("Encerrando sistemas. Até logo, Diego!")
            break

        # Tenta local primeiro, se não, vai para a IA
        if not executar_comandos_locais(comando):
            try:
                # O CÉREBRO NOVO: gemini-2.5-flash
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=comando,
                    config=types.GenerateContentConfig(
                        system_instruction="Seu nome é Aurora. Você é uma assistente virtual de tecnologia e segurança da informação. Responda de forma curta e amigável."
                    )
                )
                speak(response.text)
            except Exception as e:
                print(f"Erro no processamento: {e}")
                speak("Tive um problema ao processar isso no meu cérebro digital.")

if __name__ == "__main__":
    start_aurora()