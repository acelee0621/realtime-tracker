
from pathlib import Path
from fastapi import APIRouter,Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core import dependencies as deps
from app.models.model import Inventory
from app.schemas.schemas import InventoryCreate, InventoryUpdate, InventoryResponse

router = APIRouter(tags=["Tracker"])


STATIC_DIR = Path(__file__).parent.parent.parent / "static" 


@router.get("/")
async def read_root():
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/api/inventory", response_model=list[InventoryResponse])
async def get_inventory(db: AsyncSession = Depends(get_db)):
    """Get all inventory items"""
    result = await db.execute(select(Inventory).order_by(Inventory.updated_at.desc()))
    items = result.scalars().all()
    return items


@router.post("/api/inventory", response_model=InventoryResponse)
async def create_inventory_item(
    item: InventoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new inventory item"""
    db_item = Inventory(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.put("/api/inventory/{item_id}", response_model=InventoryResponse)
async def update_inventory_item(
    item_id: int,
    item_update: InventoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an inventory item's quantity"""
    result = await db.execute(select(Inventory).where(Inventory.id == item_id))
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.quantity = item_update.quantity
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.delete("/api/inventory/{item_id}")
async def delete_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an inventory item"""
    result = await db.execute(select(Inventory).where(Inventory.id == item_id))
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(db_item)
    await db.commit()
    return {"message": "Item deleted successfully"}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await deps.manager.connect(websocket)
    try:
        async for message in websocket.iter_text():            
            pass
    except WebSocketDisconnect:
        deps.manager.disconnect(websocket)