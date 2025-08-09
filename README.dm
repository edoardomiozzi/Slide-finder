# Slide Finder API

FastAPI Service to look for slides for relevance, with PowerAutomate Integration


```bash
pip install -r requirements.txt
uvicorn prototype:app --reload
```

#Endpoints

#1.  Standard
```bash
GET /search?query=logistics
```

# 2. Power Automate Webhook
```bash
POST /power-automate-webhook
{
  "action": "search",
  "query": "cost optimization",
  "top_k": 5
}
```

# 3. Health Check
```bash
GET /
```

# Power Automate Integration

### URL Webhook
```
https://slide-finder.onrender.com/power-automate-webhook
```

### Example
```json
{
  "action": "search",
  "query": "inventory management",
  "top_k": 3
}
```

### Reply
```json
{
  "success": true,
  "results": [
    {
      "slideId": "3",
      "title": "Inventory Management Best Practices",
      "content": "Lowering inventory levels",
      "similarityScore": 1.0,
      "sharepointUrl": "https://company.sharepoint.com/slides/3",
      "author": "System"
    }
  ],
  "totalResults": 1,
  "message": "Trovate 1 slide per 'inventory management'"
}
```

### Example2
```json
{
  "action": "index",
  "slides": [
    {
      "title": "Nuova Slide Marketing",
      "content": "Strategie di marketing digitale 2024",
      "sharepoint_url": "https://company.sharepoint.com/new-slide"
    }
  ]
}
```

# Features

- ✅ Ricerca semantica semplice
- ✅ Integrazione Power Automate
- ✅ CORS abilitato
- ✅ Health check
- ✅ Documentazione automatica su `/docs`
- ✅ Aggiunta dinamica di nuove slide

# Development

### Local test
```bash
# Dependencies
pip install -r requirements.txt

# Avvia server di sviluppo
uvicorn prototype:app --reload

# Visita http://localhost:8000/docs per Swagger UI
```

### Test API
```bash
# Test ricerca
curl "http://localhost:8000/search?query=logistics"

# Test Power Automate
curl -X POST "http://localhost:8000/power-automate-webhook" \
  -H "Content-Type: application/json" \
  -d '{"action": "search", "query": "cost", "top_k": 2}'
```

## 🚀 Deploy su Render

1. Push codice su GitHub
2. Connetti repository a Render
3. L'API sarà disponibile su `https://slide-finder.onrender.com`

## 🔗 Power Automate Setup

1. Crea nuovo flow su https://make.powerautomate.com
2. Aggiungi azione HTTP POST
3. URL: `https://slide-finder.onrender.com/power-automate-webhook`
4. Body: `{"action": "search", "query": "tua query", "top_k": 5}`
5. Aggiungi azioni per processare risultati (email, Teams, ecc.)
