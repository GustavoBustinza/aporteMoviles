from flask import Flask, request, jsonify
from textblob import TextBlob
from googletrans import Translator
import requests

app = Flask(_name_)

stop_words = set(["the", "and", "is", "in", "it"])  # Add your own stop words if needed

def clean_text(text):
    blob = TextBlob(text)
    cleaned_tokens = [word.lemmatize() for word in blob.words if word.isalnum() and word.lower() not in stop_words]
    return ' '.join(cleaned_tokens)

@app.route('/analizar_sentimiento', methods=['POST'])
def analizar_sentimiento():
    try:
        data = request.get_json()

        comentarios = data.get('comentarios', [])

        translator = Translator()
        polarities = []
        comments_cleaned = []

        for comentario in comentarios:
            translation = translator.translate(comentario, dest='en')
            translated_text = translation.text

            cleaned_text = clean_text(translated_text)
            comments_cleaned.append(cleaned_text)

            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity
            polarities.append(polarity)

            print(f"Comentario original (español): {comentario}")
            print(f"Comentario traducido y limpio (inglés): {cleaned_text}")
            print(f"Polaridad: {polarity}\n")

        positive_count = sum(p > 0 for p in polarities)
        negative_count = sum(p < 0 for p in polarities)
        neutral_count = sum(p == 0 for p in polarities)

        # Crear un gráfico circular para mostrar la distribución de polaridades
        labels = ['Positivo', 'Negativo', 'Neutral']
        sizes = [positive_count, negative_count, neutral_count]
        colors = ['lightgreen', 'lightcoral', 'lightskyblue']
        explode = (0.1, 0.1, 0)  # Destacar las secciones

        # Guardar el gráfico en un archivo
        plt.figure(figsize=(8, 6))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title('Distribución de polaridades')
        plt.axis('equal')  # Asegurar que el gráfico sea un círculo en lugar de una elipse
        plt.tight_layout()
        plt.savefig('grafico_polaridades.png')

        # Enviar el gráfico y otros resultados a la URL proporcionada
        with open('grafico_polaridades.png', 'rb') as file:
            files = {'grafico_polaridades': ('grafico_polaridades.png', file)}
            results = {
                'success': True,
                'polaridades': polarities,
                'comentarios_cleaned': comments_cleaned
            }
            response = requests.post('https://vipcell-desarrolloweb.000webhostapp.com/moviles/admin/recibir_calificaciones.php', files=files, data=results)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if _name_ == '_main_':
    app.run(debug=True)