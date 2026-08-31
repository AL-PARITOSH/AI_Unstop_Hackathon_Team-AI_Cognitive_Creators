from fastapi import APIRouter, HTTPException, Response
from app.services.storage_service import StorageService

viewer_router = APIRouter()

@viewer_router.get("/visuals/{visual_id}", summary="Standalone Visual Viewer", description="Directly serves the rendered HTML/SVG visual page for embedding via iframe or direct preview.")
def view_visual_page(visual_id: str):
    html_content = StorageService.read_visual_artifact(visual_id)
    if not html_content:
        raise HTTPException(status_code=404, detail=f"Visual artifact '{visual_id}' not found.")
    return Response(content=html_content, media_type="text/html")
