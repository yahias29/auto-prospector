🚀 Auto-Prospector AI
Un pipeline d'automatisation IA cloud-native pour l'enrichissement de leads et la génération de messages de prospection personnalisés.

📜 Aperçu
Auto-Prospector AI est un pipeline de données de bout en bout qui automatise entièrement le processus de prospection commerciale. Le système prend une liste de profils LinkedIn, l'enrichit avec des informations pertinentes trouvées en temps réel sur le web, et génère des e-mails d'approche uniques et personnalisés grâce à une équipe d'agents IA autonomes.

✨ Fonctionnalités Clés
Intégration de Source de Données : Se connecte à des outils comme Phantombuster pour l'acquisition automatique de leads.

Orchestration de Workflow : Utilise n8n pour gérer le flux de données de manière fiable entre les différents services.

Cerveau IA Multi-Agents : Exploite une équipe d'agents IA (Chercheur, Analyste, Rédacteur) avec CrewAI pour une analyse approfondie et une rédaction de haute qualité.

Dédoublonnage Automatique : Une base de données SQLite persistante empêche de traiter deux fois le même prospect.

Déploiement CI/CD : Un pipeline entièrement automatisé avec GitHub Actions pour les tests et le déploiement sur Microsoft Azure.

🛠️ Architecture et Stack Technique
Backend : Python, FastAPI, Pydantic

IA / ML : Azure OpenAI, CrewAI (Agents IA), Serper (Recherche Web)

Automatisation : n8n, Phantombuster

Base de Données : SQLite

DevOps & Déploiement : GitHub Actions (CI/CD), Microsoft Azure App Service, Docker (implicite via Azure)

⚙️ Installation et Lancement
Pour lancer ce projet localement, suivez ces étapes :

Clonez le repository :

Bash

git clone https://github.com/yahias29/auto-prospector.git
cd auto-prospector
Créez un environnement virtuel et installez les dépendances :

Bash

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Configurez les variables d'environnement :

Créez un fichier .env à la racine du projet à partir de .env.example.

Remplissez les clés API requises :

AZURE_OPENAI_ENDPOINT="VOTRE_ENDPOINT"
AZURE_OPENAI_API_KEY="VOTRE_CLÉ"
AZURE_OPENAI_DEPLOYMENT_NAME="VOTRE_NOM_DE_DÉPLOIEMENT"
OPENAI_API_VERSION="2024-02-15-preview"
SERPER_API_KEY="VOTRE_CLÉ_SERPER"

Lancez le serveur API :
Bash

uvicorn app.main:app --reload

🧠 Défis et Apprentissages
Le principal défi de ce projet a été de le déployer dans un environnement cloud de production et d'assurer sa stabilité. J'ai dû résoudre plusieurs problèmes complexes :

Conflits de Dépendances Système : J'ai résolu un problème de version de sqlite3 sur Azure en intégrant pysqlite3-binary.

Problèmes de Réseau Cloud : J'ai diagnostiqué et corrigé des erreurs de certificat SSL pour les appels sortants en utilisant certifi.

Blocages de Sécurité : J'ai géré un blocage de sécurité (403 Forbidden) sur la ressource Azure en créant une nouvelle instance propre.

Optimisation des Performances : J'ai résolu les erreurs de timeout (502 Bad Gateway) en ajustant la configuration du serveur Gunicorn.
