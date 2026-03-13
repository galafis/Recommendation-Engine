# Recommendation Engine

Motor de recomendacao com filtragem colaborativa, baseada em conteudo e hibrida.

Recommendation engine with collaborative, content-based, and hybrid filtering.

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)](Dockerfile)

[Portugues](#portugues) | [English](#english)

---

## Portugues

### Visao Geral

Sistema de recomendacao que implementa tres abordagens:

- **Filtragem Colaborativa**: Recomenda itens com base na similaridade entre usuarios (cosseno e Pearson).
- **Filtragem Baseada em Conteudo**: Recomenda itens similares aos que o usuario ja avaliou positivamente, utilizando vetores de caracteristicas.
- **Recomendacao Hibrida**: Combina ambas as abordagens com pesos configuraveis.

### Arquitetura

```mermaid
graph TD
    A[Cliente HTTP] --> B[Flask API]
    B --> C[HybridRecommender]
    C --> D[CollaborativeFilter]
    C --> E[ContentBasedFilter]
    D --> F[Similaridade entre Usuarios]
    D --> G[Predicao de Rating]
    E --> H[Perfil do Usuario]
    E --> I[Similaridade de Itens]

    style B fill:#0d1117,color:#c9d1d9,stroke:#58a6ff
    style C fill:#161b22,color:#c9d1d9,stroke:#8b949e
    style D fill:#161b22,color:#c9d1d9,stroke:#8b949e
    style E fill:#161b22,color:#c9d1d9,stroke:#8b949e
```

### Fluxo de Recomendacao

```mermaid
sequenceDiagram
    participant U as Usuario
    participant API as Flask API
    participant H as HybridRecommender
    participant CF as CollaborativeFilter
    participant CB as ContentBasedFilter

    U->>API: GET /api/recommend/user_1
    API->>H: recommend(user_1, k=10)
    H->>CF: recommend_items(user_1)
    CF->>CF: Encontrar usuarios similares
    CF-->>H: Recomendacoes CF
    H->>CB: recommend_items(user_1)
    CB->>CB: Comparar perfil com itens
    CB-->>H: Recomendacoes CB
    H->>H: Combinar scores
    H-->>API: Lista ordenada
    API-->>U: JSON Response
```

### Inicio Rapido

```bash
git clone https://github.com/galafis/Recommendation-Engine.git
cd Recommendation-Engine
pip install -r requirements.txt
python app.py
```

### Endpoints

| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | `/api/ratings` | Adicionar avaliacao |
| POST | `/api/items` | Adicionar item com features |
| GET | `/api/recommend/<user_id>` | Obter recomendacoes |
| GET | `/api/similar/<item_id>` | Encontrar itens similares |
| GET | `/api/stats` | Estatisticas do motor |

### Estrutura do Projeto

```
Recommendation-Engine/
├── engine.py             # Motores de recomendacao
├── app.py                # API Flask
├── tests/
│   └── test_engine.py    # Testes unitarios
├── requirements.txt
├── LICENSE
└── README.md
```

---

## English

### Overview

Recommendation system implementing three approaches:

- **Collaborative Filtering**: Recommends items based on user similarity (cosine and Pearson).
- **Content-Based Filtering**: Recommends items similar to those the user has rated positively, using feature vectors.
- **Hybrid Recommendation**: Combines both approaches with configurable weights.

### Architecture

```mermaid
graph TD
    A[HTTP Client] --> B[Flask API]
    B --> C[HybridRecommender]
    C --> D[CollaborativeFilter]
    C --> E[ContentBasedFilter]
    D --> F[User Similarity]
    D --> G[Rating Prediction]
    E --> H[User Profile]
    E --> I[Item Similarity]

    style B fill:#0d1117,color:#c9d1d9,stroke:#58a6ff
    style C fill:#161b22,color:#c9d1d9,stroke:#8b949e
    style D fill:#161b22,color:#c9d1d9,stroke:#8b949e
    style E fill:#161b22,color:#c9d1d9,stroke:#8b949e
```

### Quick Start

```bash
git clone https://github.com/galafis/Recommendation-Engine.git
cd Recommendation-Engine
pip install -r requirements.txt
python app.py
```

### Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/ratings` | Add a user rating |
| POST | `/api/items` | Add item with features |
| GET | `/api/recommend/<user_id>` | Get recommendations |
| GET | `/api/similar/<item_id>` | Find similar items |
| GET | `/api/stats` | Engine statistics |

### Tests

```bash
python -m pytest tests/ -v
```

---

## Autor / Author

**Gabriel Demetrios Lafis**
- GitHub: [@galafis](https://github.com/galafis)
- LinkedIn: [Gabriel Demetrios Lafis](https://linkedin.com/in/gabriel-demetrios-lafis)

## Licenca / License

MIT License - veja [LICENSE](LICENSE) / see [LICENSE](LICENSE).
