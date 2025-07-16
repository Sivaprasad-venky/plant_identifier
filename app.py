from flask import Flask, render_template, request, send_from_directory
import os
import requests
import wikipedia

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    error = None
    image_url = None

    if request.method == 'POST':
        image = request.files.get('image')
        if image:
            os.makedirs("uploads", exist_ok=True)
            image_path = os.path.join("uploads", image.filename)
            image.save(image_path)

            files = {'images': open(image_path, 'rb')}
            params = {'api-key': '2b10pviSH012yTWRGr2mo2Ye'}
            response = requests.post("https://my-api.plantnet.org/v2/identify/all", files=files, params=params)

            try:
                data = response.json()
                suggestion = data["results"][0]

                scientific_name = suggestion["species"]["scientificNameWithoutAuthor"]
                common_names = suggestion["species"].get("commonNames", [])
                confidence = round(suggestion["score"] * 100, 2)

                # Get Wikipedia summary (uses)
                try:
                    wiki_summary = wikipedia.summary(scientific_name, sentences=3)
                except:
                    wiki_summary = "Uses not available."

                # Related images
                images = []
                for item in data["results"]:
                    for img in item.get("images", []):
                        url = img.get("url", {})
                        img_url = url.get("o") or url.get("s")
                        if img_url:
                            images.append(img_url)

                result = {
                    "scientific_name": scientific_name,
                    "common_names": ', '.join(common_names) if common_names else "Not available",
                    "confidence": confidence,
                    "images": images[:4],
                    "uses": wiki_summary
                }

                image_url = "/uploads/" + image.filename

            except Exception as e:
                error = "Could not process the image or response."

    return render_template('index.html', result=result, error=error, image_url=image_url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(debug=True)
