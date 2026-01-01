# Manga Recap Generator

Automated manga recap video creator using Gemini 2.0 and MoviePy.

## Setup
1. Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`.
2. Ensure dependencies are installed (already done in this environment).
3. Install system dependencies if needed (`poppler-utils` for `pdf2image`):
   ```bash
   sudo apt-get install poppler-utils
   ```

## Workflow

Le processus est maintenant **entièrement automatisé**.

### Commande unique
Il vous suffit de lancer la commande suivante :
```bash
python src/main.py
```

### 📂 Exemple de Données

Le projet inclut des fichiers d'exemple pour vous permettre de tester rapidement :
*   `docs/boruto-two-blue-vortex-chap28.pdf` : Un chapitre de manga complet pour tester l'analyse.
*   `assets/music/` : Dossier pour vos MP3 (Action, Sad, etc.).

Pour lancer un test avec ce fichier :
```bash
python src/main.py
# Entrez: docs/boruto-two-blue-vortex-chap28.pdf
```

## 🎬 Résultat (Démo)

Vous pouvez voir un exemple de vidéo générée ici :
[Voir le récapitulatif généré](output/boruto-two-blue-vortex-chap28_recap.mp4)

Le dossier `output/` contient les vidéos finales avec :
-   Zoom "Infini"
-   Fond flou
-   Musique d'ambiance mixée
-   Narration en Arabe

### Étapes automatiques
1.  **Analyse** : L'IA extrait les images du PDF et écrit le script.
2.  **Synthèse Vocale** : L'IA génère automatiquement les fichiers audio avec le ton approprié (plus besoin d'AI Studio).
3.  **Montage** : Le script assemble les images et les audios pour créer la vidéo finale.

Le résultat final sera disponible dans le dossier `output/`.
