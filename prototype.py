from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

slides = [
    {"id": 1, "title": "Cost Optimization in Logistics", "content": "Reducing distribution center costs", "link": "https://company.sharepoint.com/slides/1"},
    {"id": 2, "title": "Strategic Growth in Country A", "content": "Growth levers and EBITDA impact", "link": "https://company.sharepoint.com/slides/2"},
    {"id": 3, "title": "Inventory Management Best Practices", "content": "Lowering inventory levels", "link": "https://company.sharepoint.com/slides/3"},
    # Aggiungi qui altre slide se vuoi
]

class SlideOut(BaseModel):
    id: int
    title: str
    content: str
    link: str
    score: float

def search_slides(query):
    results = []
    for s in slides:
        text = f"{s['title']} {s['content']}".lower()
        score = sum(word in text for word in query.lower().split())
        if score > 0:
            results.append((s, score))
    results.sort(key=lambda x: -x[1])
    return results

@app.get("/search", response_model=list[SlideOut])
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
