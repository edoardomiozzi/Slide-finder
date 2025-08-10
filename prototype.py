from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

app = FastAPI(title="Slide Finder API", description="API per ricerca semantica slide")

# POWER AUTOMATE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# FAKE DATA
slides = [
    {"id": 1, "title": "Cost Optimization in Logistics", "content": "Reducing distribution center costs", "link": "https://company.sharepoint.com/slides/1"},
    {"id": 2, "title": "Strategic Growth in Country A", "content": "Growth levers and EBITDA impact", "link": "https://company.sharepoint.com/slides/2"},
    {"id": 3, "title": "Inventory Management Best Practices", "content": "Lowering inventory levels", "link": "https://company.sharepoint.com/slides/3"},
    # Aggiungi qui altre slide se vuoi
]

# MODEL
class SlideOut(BaseModel):
    id: int
    title: str
    content: str
    link: str
    score: float

# MODELS 4 POW AUT
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

# FUNCTION
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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Slide Finder API is running",
        "endpoints": ["/search", "/power-automate-webhook"],
        "total_slides": len(slides),
        "timestamp": datetime.now().isoformat()
    }

# EX END-POINT
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

# ENDPOINT 4 POW AUT
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
            
            # EX FUNCTION
            search_results = search_slides(request.query, request.top_k)
            
            # Format POW AUT
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
            
