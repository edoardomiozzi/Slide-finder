from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

app = FastAPI(title="Slide Finder API", description="API per ricerca semantica slide")

# CORS per Power Automate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# I tuoi dati esistenti (aggiungi altre slide qui se vuoi)
slides = [
    {"id": 1, "title": "Cost Optimization in Logistics", "content": "Reducing distribution center costs", "link": "https://company.sharepoint.com/slides/1"},
    {"id": 2, "title": "Strategic Growth in Country A", "content": "Growth levers and EBITDA impact", "link": "https://company.sharepoint.com/slides/2"},
    {"id": 3, "title": "Inventory Management Best Practices", "content": "Lowering inventory levels", "link": "https://company.sharepoint.com/slides/3"},
    # Aggiungi qui altre slide se vuoi
]

# I tuoi modelli esistenti
class SlideOut(BaseModel):
    id: int
    title: str
    content: str
    link: str
    score: float

# NUOVI MODELLI per Power Automate
class PowerAutomateRequest(BaseModel):
    action: str
    query: Optional[str] = None
    top_k: Optional[int] = 5
    slides: Optional[List[dict]] = None

class PowerAutomateResponse(BaseModel):
    success: bool
    results: Optional[List[dict]] = None
    totalResults: Optional[int] = 0
    error: Optional[str] = None
    message: Optional[str] = None

# La tua funzione esistente
def search_slides(query, limit=None):
    results = []
    for s in slides:
        text = f"{s['title']} {s['content']}".lower()
        score = sum(word in text for word in query.lower().split())
        if score > 0:
            results.append((s, score))
    results.sort(key=lambda x: -x[1])
    
    if limit:
        results = results[:limit]
    
    return results

# Root endpoint per health check
@app.get("/")
async def root():
    return {
        "message": "Slide Finder API is running",
        "endpoints": ["/search", "/power-automate-webhook"],
        "total_slides": len(slides),
        "timestamp": datetime.now().isoformat()
    }

# Il tuo endpoint esistente - FIX per Python 3.8 compatibility
@app.get("/search")
def search(query: str = Query(...)):
    results = search_slides(query)
    return [
        SlideOut(
            id=s["id"],
            title=s["title"],
            content=s["content"],
            link=s["link"],
            score=round(score, 3)
        ) for s, score in results
    ]

# NUOVO ENDPOINT per Power Automate
@app.post("/power-automate-webhook")
async def power_automate_webhook(request: PowerAutomateRequest):
    """
    Endpoint per integrazione con Power Automate
    Supporta azioni: search, index
    """
    try:
        if request.action == "search":
            if not request.query:
                return PowerAutomateResponse(
                    success=False,
                    error="Query richiesta per la ricerca"
                )
            
            # Usa la tua funzione esistente
            search_results = search_slides(request.query, request.top_k)
            
            # Formato per Power Automate
            pa_results = []
            for slide, score in search_results:
                pa_results.append({
                    "slideId": str(slide["id"]),
                    "title": slide["title"],
                    "content": slide["content"][:200] + "..." if len(slide["content"]) > 200 else slide["content"],
                    "similarityScore": round(score, 3),
                    "sharepointUrl": slide["link"],
                    "author": "System"
                })
            
            return PowerAutomateResponse(
                success=True,
                results=pa_results,
                totalResults=len(pa_results),
                message=f"Trovate {len(pa_results)} slide per '{request.query}'"
            )
            
        elif request.action == "index":
            # Logica per aggiungere nuove slide
            if not request.slides:
                return PowerAutomateResponse(
                    success=False,
                    error="Nessuna slide fornita per l'indicizzazione"
                )
            
            # Aggiungi le nuove slide alla lista esistente
            indexed_count = 0
            for new_slide in request.slides:
                # Genera nuovo ID
                new_id = max([s["id"] for s in slides]) + 1 if slides else 1
                
                slide_data = {
                    "id": new_id,
                    "title": new_slide.get("title", "Titolo non disponibile"),
                    "content": new_slide.get("content", ""),
                    "link": new_slide.get("sharepoint_url", new_slide.get("link", ""))
                }
                
                slides.append(slide_data)
                indexed_count += 1
            
            return PowerAutomateResponse(
                success=True,
                totalResults=indexed_count,
                message=f"Indicizzate {indexed_count} slide con successo"
            )
            
        else:
            return PowerAutomateResponse(
                success=False,
                error=f"Azione non supportata: {request.action}. Usa 'search' o 'index'"
            )
            
    except Exception as e:
        return PowerAutomateResponse(
            success=False,
            error=f"Errore interno: {str(e)}"
        )
