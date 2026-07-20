from fastapi import APIRouter, HTTPException

from app.models.item import Item, ItemCreate

router = APIRouter(tags=["items"])

_db: dict[int, Item] = {}


def clear_items() -> None:
    _db.clear()


@router.post("/items", response_model=Item, status_code=201)
def create_item(payload: ItemCreate) -> Item:
    item_id = len(_db) + 1
    item = Item(id=item_id, **payload.model_dump())
    _db[item_id] = item
    return item


@router.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    if item_id not in _db:
        raise HTTPException(status_code=404, detail="Item not found")
    return _db[item_id]


@router.get("/items", response_model=list[Item])
def list_items() -> list[Item]:
    return list(_db.values())
