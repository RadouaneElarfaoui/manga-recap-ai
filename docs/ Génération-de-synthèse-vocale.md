# Génération de synthèse vocale

L'API Gemini peut transformer une entrée de texte en contenu audio à une ou plusieurs voix à l'aide de fonctionnalités de génération de synthèse vocale (TTS) natives. La génération de synthèse vocale (TTS) est contrôlable, ce qui signifie que vous pouvez utiliser le langage naturel pour structurer les interactions et guider le style, l'accent, le rythme et le ton de l'audio.

La fonctionnalité TTS diffère de la génération vocale fournie par l'API Live, qui est conçue pour les entrées et sorties audio interactives, non structurées et multimodales. Alors que l'API Live excelle dans les contextes conversationnels dynamiques, la synthèse vocale via l'API Gemini est conçue pour les scénarios qui nécessitent une récitation exacte du texte avec un contrôle précis du style et du son, comme la génération de podcasts ou de livres audio.

Ce guide explique comment générer de l'audio à un ou plusieurs locuteurs à partir de texte.

> **Preview :** la synthèse vocale native est disponible en version preview.

## Avant de commencer
Assurez-vous d'utiliser une variante du modèle Gemini 2.5 avec des fonctionnalités de synthèse vocale (TTS) natives, comme indiqué dans la section Modèles compatibles. Pour obtenir des résultats optimaux, réfléchissez au modèle qui correspond le mieux à votre cas d'utilisation spécifique.

Il peut être utile de tester les modèles TTS Gemini 2.5 dans AI Studio avant de commencer à créer.

**Remarque :** Les modèles TTS acceptent les entrées textuelles uniquement et génèrent des sorties audio uniquement. Pour obtenir la liste complète des restrictions spécifiques aux modèles TTS, consultez la section Limites.

## Synthèse vocale à un seul locuteur
Pour convertir du texte en contenu audio à une seule voix, définissez la modalité de réponse sur "audio" et transmettez un objet `SpeechConfig` avec `VoiceConfig` défini. Vous devrez choisir un nom de voix parmi les voix de sortie prédéfinies.

Cet exemple enregistre le contenu audio généré par le modèle dans un fichier WAV :

### Python

```python
from google import genai
from google.genai import types
import wave

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

client = genai.Client()

response = client.models.generate_content(
   model="gemini-2.5-flash-preview-tts",
   contents="Say cheerfully: Have a wonderful day!",
   config=types.GenerateContentConfig(
      response_modalities=["AUDIO"],
      speech_config=types.SpeechConfig(
         voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
               voice_name='Kore',
            )
         )
      ),
   )
)

data = response.candidates[0].content.parts[0].inline_data.data

file_name='out.wav'
wave_file(file_name, data) # Saves the file to current directory
```

Pour obtenir d'autres exemples de code, consultez le fichier "TTS - Get Started" (TTS – Premiers pas) dans le dépôt de cookbooks.

## Synthèse vocale multi-locuteurs
Pour l'audio multi-locuteurs, vous aurez besoin d'un objet `MultiSpeakerVoiceConfig` avec chaque locuteur (jusqu'à deux) configuré en tant que `SpeakerVoiceConfig`. Vous devez définir chaque speaker avec les mêmes noms que ceux utilisés dans le prompt :

### Python

```python
from google import genai
from google.genai import types
import wave

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

client = genai.Client()

prompt = """TTS the following conversation between Joe and Jane:
         Joe: How's it going today Jane?
         Jane: Not too bad, how about you?"""

response = client.models.generate_content(
   model="gemini-2.5-flash-preview-tts",
   contents=prompt,
   config=types.GenerateContentConfig(
      response_modalities=["AUDIO"],
      speech_config=types.SpeechConfig(
         multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[
               types.SpeakerVoiceConfig(
                  speaker='Joe',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore',
                     )
                  )
               ),
               types.SpeakerVoiceConfig(
                  speaker='Jane',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Puck',
                     )
                  )
               ),
            ]
         )
      )
   )
)

data = response.candidates[0].content.parts[0].inline_data.data

file_name='out.wav'
wave_file(file_name, data) # Saves the file to current directory
```

## Contrôler le style de parole avec des requêtes
Vous pouvez contrôler le style, le ton, l'accent et le rythme à l'aide de requêtes en langage naturel pour la synthèse vocale à une ou plusieurs voix. Par exemple, dans un prompt à un seul locuteur, vous pouvez dire :

> Say in an spooky whisper:
> "By the pricking of my thumbs...
> Something wicked this way comes"

Dans une requête à plusieurs locuteurs, fournissez au modèle le nom de chaque locuteur et la transcription correspondante. Vous pouvez également fournir des conseils pour chaque enceinte individuellement :

> Make Speaker1 sound tired and bored, and Speaker2 sound excited and happy:
>
> Speaker1: So... what's on the agenda today?
> Speaker2: You're never going to guess!

Essayez d'utiliser une option vocale qui correspond au style ou à l'émotion que vous souhaitez transmettre, pour l'accentuer encore plus. Dans la requête précédente, par exemple, le ton haletant d'Encelade peut mettre l'accent sur les mots "fatigué" et "ennuyé", tandis que le ton enjoué de Puck peut compléter les mots "enthousiaste" et "heureux".

## Générer un prompt pour convertir un texte en audio
Les modèles TTS ne génèrent que de l'audio, mais vous pouvez utiliser d'autres modèles pour générer d'abord une transcription, puis la transmettre au modèle TTS pour qu'il la lise à voix haute.

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()

transcript = client.models.generate_content(
   model="gemini-2.5-flash",
   contents="""Generate a short transcript around 100 words that reads
            like it was clipped from a podcast by excited herpetologists.
            The hosts names are Dr. Anya and Liam.""").text

response = client.models.generate_content(
   model="gemini-2.5-flash-preview-tts",
   contents=transcript,
   config=types.GenerateContentConfig(
      response_modalities=["AUDIO"],
      speech_config=types.SpeechConfig(
         multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[
               types.SpeakerVoiceConfig(
                  speaker='Dr. Anya',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore',
                     )
                  )
               ),
               types.SpeakerVoiceConfig(
                  speaker='Liam',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Puck',
                     )
                  )
               ),
            ]
         )
      )
   )
)

# ...Code to stream or save the output
```

## Options vocales
Les modèles TTS sont compatibles avec les 30 options vocales suivantes dans le champ `voice_name` :

*   Zephyr : Lumineux
*   Puck : Upbeat
*   Charon : Contenu informatif
*   Kore : Ferme
*   Fenrir : excitabilité
*   Leda : Jeune
*   Orus : cabinet d'avocats
*   Aoede : Breezy
*   Callirrhoe : tranquille
*   Autonoe : Lumineux
*   Enceladus : Souffle
*   Iapetus : Effacer
*   Umbriel : décontracté
*   Algieba : Lisse
*   Despina : Lisse
*   Erinome : dégagé
*   Algenib : Graveleux
*   Rasalgethi : informatif
*   Laomedeia : Upbeat
*   Achernar – Soft
*   Alnilam : Ferme
*   Schedar : pair
*   Gacrux -- Contenu réservé aux adultes
*   Pulcherrima : Transférer
*   Achird : amical
*   Zubenelgenubi : Décontracté
*   Vindemiatrix : Doux
*   Sadachbia : Lively
*   Sadaltager : connaissances
*   Sulafat : chaude

Vous pouvez écouter toutes les options vocales dans AI Studio.

## Langues disponibles
Les modèles TTS détectent automatiquement la langue d'entrée. Ils sont disponibles dans les 24 langues suivantes :

| Langue | Code BCP-47 | Langue | Code BCP-47 |
| :--- | :--- | :--- | :--- |
| Arabe (Égypte) | ar-EG | Allemand (Allemagne) | de-DE |
| Anglais (États-Unis) | en-US | Espagnol (États-Unis) | es-US |
| Français (France) | fr-FR | Hindi (Inde) | hi-IN |
| Indonésien (Indonésie) | id-ID | Italien (Italie) | it-IT |
| Japonais (Japon) | ja-JP | Coréen (Corée) | ko-KR |
| Portugais (Brésil) | pt-BR | Russe (Russie) | ru-RU |
| Néerlandais (Pays-Bas) | nl-NL | Polonais (Pologne) | pl-PL |
| Thaï (Thaïlande) | th-TH | Turc (Turquie) | tr-TR |
| Vietnamien (Viêt Nam) | vi-VN | Roumain (Roumanie) | ro-RO |
| Ukrainien (Ukraine) | uk-UA | Bengali (Bangladesh) | bn-BD |
| Anglais (Inde) | Lot en-IN et hi-IN | Marathi (Inde) | mr-IN |
| Tamoul (Inde) | ta-IN | Télougou (Inde) | te-IN |

## Modèles compatibles

| Modèle | Locuteur unique | Multihaut-parleur |
| :--- | :--- | :--- |
| TTS Gemini 2.5 Flash (preview) | ✔️ | ✔️ |
| TTS Gemini 2.5 Pro (preview) | ✔️ | ✔️ |

## Limites
*   Les modèles de synthèse vocale ne peuvent recevoir que des entrées de texte et générer des sorties audio.
*   Une session TTS est limitée à une fenêtre de contexte de 32 000 jetons.
*   Consultez la section Langues pour connaître les langues disponibles.

## Guide sur les requêtes
Le modèle Gemini Native Audio Generation Text-to-Speech (TTS) se distingue des modèles TTS traditionnels en utilisant un grand modèle de langage qui sait non seulement quoi dire, mais aussi comment le dire.

Pour débloquer cette fonctionnalité, les utilisateurs peuvent se considérer comme des réalisateurs qui mettent en scène un talent vocal virtuel. Pour créer une requête, nous vous recommandons de tenir compte des éléments suivants : un profil audio qui définit l'identité et l'archétype du personnage, une description de la scène qui établit l'environnement physique et l'ambiance émotionnelle, et des notes du réalisateur qui offrent des conseils plus précis sur le style, l'accent et le rythme.

En fournissant des instructions nuancées, comme un accent régional précis, des caractéristiques paralinguistiques spécifiques (par exemple, un souffle) ou un rythme, les utilisateurs peuvent tirer parti de la conscience du contexte du modèle pour générer des performances audio très dynamiques, naturelles et expressives. Pour des performances optimales, nous vous recommandons d'aligner les transcriptions et les instructions de mise en scène, afin que "qui le dit" corresponde à "ce qui est dit" et à "comment c'est dit".

L'objectif de ce guide est de vous fournir des instructions de base et de vous donner des idées pour développer des expériences audio à l'aide de la génération audio Gemini TTS. Nous avons hâte de découvrir vos créations !

### Structure des requêtes
Une requête robuste inclut idéalement les éléments suivants qui, ensemble, permettent d'obtenir d'excellentes performances :

1.  **Profil audio :** établit une personnalité pour la voix, en définissant une identité de personnage, un archétype et toute autre caractéristique comme l'âge, l'origine, etc.
2.  **Scène :** plante le décor. Décris l'environnement physique et l'ambiance.
3.  **Notes du réalisateur :** conseils sur les performances qui vous permettent de préciser les instructions importantes que votre talent virtuel doit prendre en compte. Par exemple, le style, la respiration, le rythme, l'articulation et l'accent.
4.  **Exemple de contexte :** fournit au modèle un point de départ contextuel, de sorte que votre acteur virtuel entre naturellement dans la scène que vous avez configurée.
5.  **Transcription :** texte que le modèle prononcera. Pour des performances optimales, n'oubliez pas que le thème et le style d'écriture de la transcription doivent correspondre aux instructions que vous donnez.

**Remarque :** Demandez à Gemini de vous aider à créer votre requête. Il vous suffit de lui fournir un plan vide du format ci-dessous et de lui demander de vous esquisser un personnage.

Exemple de requête complète :

```text
# AUDIO PROFILE: Jaz R.
## "The Morning Hype"

## THE SCENE: The London Studio
It is 10:00 PM in a glass-walled studio overlooking the moonlit London skyline,
but inside, it is blindingly bright. The red "ON AIR" tally light is blazing.
Jaz is standing up, not sitting, bouncing on the balls of their heels to the
rhythm of a thumping backing track. Their hands fly across the faders on a
massive mixing desk. It is a chaotic, caffeine-fueled cockpit designed to wake
up an entire nation.

### DIRECTOR'S NOTES
Style:
* The "Vocal Smile": You must hear the grin in the audio. The soft palate is
always raised to keep the tone bright, sunny, and explicitly inviting.
* Dynamics: High projection without shouting. Punchy consonants and elongated
vowels on excitement words (e.g., "Beauuutiful morning").

Pace: Speaks at an energetic pace, keeping up with the fast music.  Speaks
with A "bouncing" cadence. High-speed delivery with fluid transitions — no dead
air, no gaps.

Accent: Jaz is from Brixton, London

### SAMPLE CONTEXT
Jaz is the industry standard for Top 40 radio, high-octane event promos, or any
script that requires a charismatic Estuary accent and 11/10 infectious energy.

#### TRANSCRIPT
Yes, massive vibes in the studio! You are locked in and it is absolutely
popping off in London right now. If you're stuck on the tube, or just sat
there pretending to work... stop it. Seriously, I see you. Turn this up!
We've got the project roadmap landing in three, two... let's go!
```

### Stratégies de requête détaillées
Décomposons chaque élément de la requête.

#### Profil audio
Décrivez brièvement le personnage.

*   **Nom.** Donner un nom à votre personnage permet d'ancrer le modèle et de resserrer les performances. Faites référence au personnage par son nom lorsque vous définissez la scène et le contexte.
*   **Rôle.** Identité et archétype fondamentaux du personnage qui se déroulent dans la scène. Par exemple : Animateur radio, podcasteur, journaliste, etc.

Exemples :

```text
# AUDIO PROFILE: Jaz R.
## "The Morning Hype"
```

```text
# AUDIO PROFILE: Monica A.
## "The Beauty Influencer"
```

#### Scene
Définissez le contexte de la scène, y compris le lieu, l'ambiance et les détails environnementaux qui établissent le ton et l'atmosphère. Décrivez ce qui se passe autour du personnage et comment cela l'affecte. La scène fournit le contexte environnemental pour l'ensemble de l'interaction et guide le jeu d'acteur de manière subtile et naturelle.

Exemples :

```text
## THE SCENE: The London Studio
It is 10:00 PM in a glass-walled studio overlooking the moonlit London skyline,
but inside, it is blindingly bright. The red "ON AIR" tally light is blazing.
Jaz is standing up, not sitting, bouncing on the balls of their heels to the
rhythm of a thumping backing track. Their hands fly across the faders on a
massive mixing desk. It is a chaotic, caffeine-fueled cockpit designed to
wake up an entire nation.
```

```text
## THE SCENE: Homegrown Studio
A meticulously sound-treated bedroom in a suburban home. The space is
deadened by plush velvet curtains and a heavy rug, but there is a
distinct "proximity effect."
```

#### Notes du réalisateur
Cette section essentielle inclut des conseils spécifiques sur les performances. Vous pouvez ignorer tous les autres éléments, mais nous vous recommandons d'inclure celui-ci.

Définissez uniquement ce qui est important pour les performances, en veillant à ne pas trop spécifier. Si vous définissez trop de règles strictes, vous limiterez la créativité des modèles et risquez de réduire leurs performances. Équilibrez la description du rôle et de la scène avec les règles de performance spécifiques.

Les consignes les plus courantes sont Style, Rythme et Accent, mais le modèle n'est pas limité à celles-ci et ne les exige pas. N'hésitez pas à inclure des instructions personnalisées pour couvrir tous les détails supplémentaires importants pour vos performances. Soyez aussi précis que nécessaire.

Exemple :

```text
### DIRECTOR'S NOTES

Style: Enthusiastic and Sassy GenZ beauty YouTuber

Pacing: Speaks at an energetic pace, keeping up with the extremely fast, rapid
delivery influencers use in short form videos.

Accent: Southern california valley girl from Laguna Beach |
```

**Style :**

Définit le ton et le style de la voix générée. Indiquez l'ambiance souhaitée (joyeuse, énergique, détendue, ennuyée, etc.) pour guider la performance. Soyez descriptif et fournissez autant de détails que nécessaire : "Enthousiasme contagieux. L'auditeur doit avoir l'impression de participer à un événement communautaire passionnant et de grande envergure." est plus efficace que énergique et enthousiaste.

Vous pouvez même essayer des termes populaires dans le secteur de la voix off, comme "sourire vocal". Vous pouvez superposer autant de caractéristiques de style que vous le souhaitez.

Exemples :

*Émotion simple*

```text
DIRECTORS NOTES
...
Style: Frustrated and angry developer who can't get the build to run.
...
```

*Plus de profondeur*

```text
DIRECTORS NOTES
...
Style: Sassy GenZ beauty YouTuber, who mostly creates content for YouTube Shorts.
...
```

*Complexe*

```text
DIRECTORS NOTES
Style:
* The "Vocal Smile": You must hear the grin in the audio. The soft palate is
always raised to keep the tone bright, sunny, and explicitly inviting.
*Dynamics: High projection without shouting. Punchy consonants and
elongated vowels on excitement words (e.g., "Beauuutiful morning").
```

**Accent :**

Décrivez l'accent souhaité. Plus vous serez précis, meilleurs seront les résultats. Par exemple, utilisez *accent anglais britannique tel qu'il est parlé à Croydon, en Angleterre* au lieu de *accent britannique*.

Exemples :

```text
### DIRECTORS NOTES
...
Accent: Southern california valley girl from Laguna Beach
...
```

```text
### DIRECTORS NOTES
...
Accent: Jaz is a from Brixton, London
...
```

**Rythme**

Rythme global et variations de rythme tout au long de la pièce.

Exemples :

*Simple*

```text
### DIRECTORS NOTES
...
Pacing: Speak as fast as possible
...
```

*Plus de précision*

```text
### DIRECTORS NOTES
...
Pacing: Speaks at a faster, energetic pace, keeping up with fast paced music.
...
```

*Complexe*

```text
### DIRECTORS NOTES
...
Pacing: The "Drift": The tempo is incredibly slow and liquid. Words bleed into each other. There is zero urgency.
...
```

### Essayer

Essayez vous-même certains de ces exemples dans AI Studio, testez notre application TTS et laissez Gemini vous mettre dans le fauteuil du réalisateur. Voici quelques conseils pour réaliser d'excellentes performances vocales :

*   N'oubliez pas de veiller à la cohérence de l'ensemble de la requête : le script et la mise en scène vont de pair pour créer une performance de qualité.
*   Ne vous sentez pas obligé de tout décrire. Parfois, laisser au modèle la possibilité de combler les lacunes contribue à la fluidité. (tout comme un acteur talentueux).
*   Si vous êtes bloqué, demandez à Gemini de vous aider à rédiger votre script ou à préparer votre prestation.

## Étape suivante
*   Essayez le cookbook de génération audio.
*   L'API Live de Gemini propose des options de génération audio interactives que vous pouvez entrelacer avec d'autres modalités.
*   Pour savoir comment utiliser les entrées audio, consultez le guide Compréhension audio.

___

Sauf indication contraire, le contenu de cette page est régi par une licence Creative Commons Attribution 4.0, et les échantillons de code sont régis par une licence Apache 2.0. Pour en savoir plus, consultez les Règles du site Google Developers. Java est une marque déposée d'Oracle et/ou de ses sociétés affiliées.

Dernière mise à jour le 2025/12/25 (UTC).

Conditions d'utilisation
Règles de confidentialité