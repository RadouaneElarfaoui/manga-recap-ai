<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Tavily Search API – Guide d’intégration Python

## Introduction

Tavily est un moteur de recherche web **optimisé** pour les agents IA et les applications basées sur des LLMs, offrant des résultats factuels, ciblés et filtrables via une simple API HTTP et des SDKs officiels.[^1][^2]
Il fournit des fonctionnalités de recherche, d’extraction et de crawling conçues pour le Retrieval Augmented Generation (RAG), permettant de générer facilement du contexte structuré à partir du web pour l’injection dans vos prompts LLM.[^3][^2]

***

## Installation

Pour intégrer Tavily dans un projet Python, utilisez le SDK officiel `tavily-python`.[^1]

```bash
pip install tavily-python
```

Pour un environnement JavaScript/TypeScript, un SDK existe également via `@tavily/core` (hors scope de ce guide Python).[^1]

***

## Configuration

L’authentification se fait via une clé d’API Tavily, généralement fournie sous la forme `tvly-XXXX...`.[^1]
Vous pouvez la configurer soit en dur dans le code, soit via la variable d’environnement `TAVILY_API_KEY` recommandée pour la production.

### 1. Configuration avec variable d’environnement

```bash
export TAVILY_API_KEY="tvly-YOUR_API_KEY"
```

Puis dans Python :

```python
from tavily import TavilyClient
import os

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
```


### 2. Configuration directe dans le code (développement)

```python
from tavily import TavilyClient

tavily_client = TavilyClient(api_key="tvly-YOUR_API_KEY")
```

Dans les deux cas, le client initialisé permet ensuite d’appeler `search` ou `get_search_context` pour interagir avec l’API Tavily.[^3][^1]

***

## Exemple de code (Python)

### Recherche simple avec TavilyClient

Cet exemple montre un script minimal complet effectuant une recherche textuelle et affichant la réponse brute.

```python
from tavily import TavilyClient
import os

def main():
    # 1. Récupération de la clé API depuis l'environnement
    api_key = os.environ.get("TAVILY_API_KEY", "tvly-YOUR_API_KEY")

    # 2. Initialisation du client Tavily
    tavily_client = TavilyClient(api_key=api_key)

    # 3. Exécution d'une recherche simple
    query = "Who is Leo Messi?"
    response = tavily_client.search(query)

    # 4. Affichage de la réponse complète (JSON dict)
    print(response)

if __name__ == "__main__":
    main()
```

L’exemple de base d’appel `search("Who is Leo Messi?")` est conforme à la démonstration fournie dans la documentation Tavily.[^1]

### Exemple RAG : génération de contexte pour un LLM

Tavily fournit une méthode dédiée `get_search_context` qui retourne directement une chaîne de contexte condensée à injecter dans un prompt de LLM pour du RAG.[^3]

```python
from tavily import TavilyClient
import os
from openai import OpenAI  # ou un autre client LLM compatible

def build_rag_answer(question: str) -> str:
    # 1. Initialisation des clients
    tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY", "tvly-YOUR_API_KEY"))
    llm_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_KEY"))

    # 2. Récupération du contexte web avec Tavily
    context = tavily_client.get_search_context(
        query=question
        # Vous pouvez ici passer des paramètres avancés (search_depth, include_domains, etc.)
    )

    # 3. Construction du prompt RAG
    prompt = f"""
You are a helpful AI assistant.
Use the following web context to answer the user question as accurately and concisely as possible.

Web context:
{context}

Question:
{question}
"""

    # 4. Appel du LLM avec le contexte Tavily
    completion = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant using verified web context."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return completion.choices[^0].message.content

if __name__ == "__main__":
    q = "What happened during the Burning Man floods?"
    answer = build_rag_answer(q)
    print(answer)
```

L’appel `get_search_context(query="What happened during the Burning Man floods?")` suit la forme indiquée dans le dépôt officiel `tavily-python` pour générer un contexte RAG en une seule ligne.[^3]

***

## Paramètres importants de l’API

La Tavily Search API accepte plusieurs paramètres permettant d’ajuster la profondeur, la portée et le format des résultats.[^4][^5][^6][^7]

### Paramètres principaux de recherche

- `query` (str, requis)
    - Texte de la requête de recherche.
    - Exemple : `"Who is Leo Messi?"`.[^1]
- `search_depth` (str, optionnel)
    - Contrôle la profondeur de la recherche, typiquement `"basic"` ou `"advanced"`.[^5][^6][^4]
    - `"basic"` : plus rapide, couvre les résultats principaux.
    - `"advanced"` : extraction plus fine de contenu aligné à la requête, utile pour RAG et analyses détaillées.[^5]
- `max_results` (int, optionnel)
    - Nombre maximum de résultats à retourner, valeur par défaut souvent 5 dans les intégrations LangChain/Tavily.[^6][^7][^4]
    - Permet de limiter la taille du contexte et la consommation de crédits.
- `include_answer` (bool, optionnel)
    - Indique si Tavily doit inclure une réponse synthétique à la requête, en plus des résultats bruts.[^4][^6]
    - Par défaut `False` dans certains wrappers outils, à activer pour obtenir un résumé rapide.
- `include_raw_content` (bool, optionnel)
    - Si `True`, retourne le contenu textuel brut des pages, utile pour des pipelines d’analyse ou embeddings personnalisés.[^6][^4]
- `include_images` (bool, optionnel)
    - Si `True`, inclut des images liées aux résultats, ainsi que des métadonnées possibles dans certains wrappers.[^4][^6]
- `include_image_descriptions` (bool, optionnel, côté intégrations tools)
    - Active le retour de descriptions textuelles d’images pour les agents multimodaux.[^6]
- `time_range` (str, optionnel)
    - Filtre temporel relatif : `"day"`, `"week"`, `"month"`, `"year"` pour restreindre les résultats aux contenus récents.[^6]
    - Utile pour les sujets d’actualité, finance ou news.
- `topic` (str, optionnel)
    - Spécifie la catégorie de recherche : `"general"`, `"news"`, `"finance"` dans certaines intégrations.[^6]
    - Aide Tavily à ajuster les sources et la pertinence.
- `include_domains` (List[str], optionnel)
    - Restreint la recherche à certains domaines ou sous-domaines.[^7][^5][^6]
    - Exemple : `["linkedin.com/in"]` pour cibler des profils professionnels.[^5]
    - Supporte des patterns comme `"*.com"` pour limiter à un TLD.[^5]
- `exclude_domains` (List[str], optionnel)
    - Exclut certains domaines des résultats, par exemple pour éviter des sources non désirées.[^7][^5][^6]
- `include_usage` (bool, optionnel)
    - Indique si l’API doit inclure les informations d’usage/crédits consommés dans la réponse JSON.[^7]


### Exemple d’appel Python avec paramètres

```python
from tavily import TavilyClient

tavily_client = TavilyClient(api_key="tvly-YOUR_API_KEY")

response = tavily_client.search(
    query="Should I invest in Apple right now?",
    search_depth="basic",
    include_answer=True,
    include_raw_content=False,
    include_images=False,
    max_results=5,
    include_domains=["*.com"],
    exclude_domains=["example.com"],
)
```

Les paramètres illustrés (`search_depth`, `include_answer`, `include_images`, `max_results`, `include_domains`, `exclude_domains`) correspondent aux usages montrés dans les issues GitHub et intégrations d’outils.[^4][^7][^5][^6]

***

## Intégrations Frameworks

### Intégration LangChain

LangChain fournit un outil `TavilySearch` qui encapsule l’API de Tavily et expose les mêmes paramètres principaux (max_results, search_depth, include_domains, etc.).[^7][^6]

#### Installation

```bash
pip install langchain-core langchain-community langchain-tavily tavily-python
```


#### Exemple d’utilisation

```python
from langchain_tavily import TavilySearch

tool = TavilySearch(
    max_results=5,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None,
)
```

L’outil peut ensuite être utilisé comme un `Tool` standard LangChain dans une chaîne ou un agent pour permettre à un LLM de lancer des recherches web.[^7][^6]

### Intégration LlamaIndex

Tavily est aussi intégré dans LlamaIndex via `TavilyToolSpec`, permettant d’ajouter la recherche web comme outil d’un agent LlamaIndex.[^8][^9]

#### Installation

```bash
pip install llama-index-tools-tavily-research llama-index llama-hub tavily-python
```


#### Exemple d’utilisation

```python
from llama_index.tools.tavily_research.base import TavilyToolSpec
from llama_index.agent.openai import OpenAIAgent

tavily_tool = TavilyToolSpec(
    api_key="tvly-YOUR_API_KEY",
)

agent = OpenAIAgent.from_tools(tavily_tool.to_tool_list())
response = agent.chat("What happened in the latest Burning Man festival?")
print(response)
```

L’outil `TavilyToolSpec` expose des méthodes comme `search` pour obtenir des URLs et contenus pertinents, intégrables directement dans un flux RAG LlamaIndex.[^8]

***

## Structure de la réponse JSON

La réponse de l’API Tavily est renvoyée sous forme de JSON comprenant généralement :

- Un champ de synthèse (souvent `answer` dans certains wrappers).
- Une liste de `results` contenant le détail des pages trouvées, avec titre, URL et contenu.[^4][^6][^7]


### Exemple de réponse JSON simplifiée

```json
{
  "query": "Who is Leo Messi?",
  "answer": "Lionel Messi is an Argentine professional footballer widely regarded as one of the greatest players of all time.",
  "results": [
    {
      "title": "Lionel Messi - Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Lionel_Messi",
      "content": "Lionel Andrés Messi is an Argentine professional footballer who plays as a forward...",
      "score": 0.98,
      "published_date": "2025-06-10T00:00:00Z"
    },
    {
      "title": "Official profile of Leo Messi",
      "url": "https://www.psg.fr/players/lionel-messi",
      "content": "Lionel Messi is a forward for Paris Saint-Germain and the Argentina national team...",
      "score": 0.93
    }
  ],
  "usage": {
    "total_credits": 1,
    "remaining_credits": 999
  }
}
```

La structure précise peut varier selon le wrapper ou l’intégration, mais les champs typiques incluent `title`, `url`, `content`, des métadonnées de score ou date, ainsi qu’un bloc éventuel `usage` si `include_usage` est activé.[^4][^6][^7]


<span style="display:none">[^10][^11]</span>

<div align="center">⁂</div>

[^1]: https://docs.tavily.com/welcome

[^2]: https://www.tavily.com/tutorials/tavily-101

[^3]: https://github.com/tavily-ai/tavily-python

[^4]: https://github.com/assafelovic/tavily-python/issues/6

[^5]: https://docs.tavily.com/documentation/best-practices/best-practices-search

[^6]: https://docs.langchain.com/oss/python/integrations/tools/tavily_search

[^7]: https://docs.tavily.com/documentation/integrations/langchain

[^8]: https://docs.tavily.com/documentation/integrations/llamaindex

[^9]: https://docs.tavily.com/llms.txt

[^10]: https://www.ibm.com/think/tutorials/build-corrective-rag-agent-granite-tavily

[^11]: https://developers.llamaindex.ai/python/framework/understanding/agent/tools/

