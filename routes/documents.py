from datetime import datetime
from config.database import document_collection
from models.documents import DocumentBase, DocumentCreate, DocumentResponse, DocumentUpdate
import os 
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File 
from bson import ObjectId
from routes.users import current_user, admin_access
from fastapi.responses import FileResponse
from utils.file_utils import save_file, extract_metadata


router = APIRouter(prefix= "/documents", tags=["documents"])

@router.post("/documents")
async def upload_document(
    title: str,
    description: str = None,
    tags: list[str] = None,
    file: UploadFile = File(...),
    user=Depends(current_user)
):
    
    contents = await file.read()
    file_path = save_file(contents, file.filename)
    metadata = extract_metadata(file_path)

    docs = {
        "title": title,
        "description": description,
        "tags": tags,
        "file_path": file_path,
        "file_type": metadata["file_type"],
        "file_size": metadata["file_size"],
        "word_count": metadata["word_count"],
        "uploaded_by": user["id"],
        "created_at": datetime.now,
        "updated_at": datetime.now
    }

    result = document_collection.insert_one(docs)
    return {"message": "Document uploaded", "id": str(result.inserted_id)}


@router.get("/documents")
async def list_document(user=Depends(current_user)):
    query = {} if user["role"] == "admin" else {"uploaded_by": user["id"]}
    docs = list(document_collection.find(query))
    for doc in docs:
        doc["id"] = str(d["_id"])
        del doc["_id"]
    return docs

@router.get("/{id}", response_model=DocumentResponse)
def get_document(id: str, user=Depends(current_user)):
    doc = document_collection.find_one({"_id": ObjectId(id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if user["role"] != "admin" and doc["uploaded_by"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not allowed")
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@router.put("/{id}")
def update_document(id: str, data: DocumentUpdate, user=Depends(current_user)):
    doc = document_collection.find_one({"_id": ObjectId(id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if user["role"] != "admin" and doc["uploaded_by"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    update_data = {k: v for k, v in data.dit().items() if v is not None}
    update_data["updated_at"] = datetime.now()

    document_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return {"msg": "Document updated"}


@router.delete("/{id}")
def delete_document(id: str, user=Depends(current_user)):
    doc = document_collection.find_one({"_id": ObjectId(id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if user["role"] != "admin" and doc["uploaded_by"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not allowed")
    os.remove(doc["file_path"])  
    document_collection.delete_one({"_id": ObjectId(id)})
    return {"message": "Document deleted"}

@router.get("/{id}/download")
def download_document(id: str, user=Depends(current_user)):
    doc = document_collection.find_one({"_id": ObjectId(id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if user["role"] != "admin" and doc["uploaded_by"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    return FileResponse(path=doc["file_path"], filename=os.path.basename(doc["file_path"]))