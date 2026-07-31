"""
Jarvis AIOS — Prompt Studio FastAPI REST & SSE API Router
"""

import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.Prompts.prompt_manager import PromptManager
from app.Prompts.models import PromptFolder
from app.Auth.dependencies import get_current_user

# NOTE: previously this was the only Studio router with no auth dependency —
# Models/Memory/Workflows/Deployments/RAG all require get_current_user. That
# looked like an oversight rather than an intentional public API, so it's
# brought in line with the rest of the platform here.
router = APIRouter(
    prefix="/api/v1/prompts",
    tags=["Prompt Studio"],
    dependencies=[Depends(get_current_user)],
)
manager = PromptManager()


class CreatePromptRequest(BaseModel):
    title: str
    description: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    folder_id: Optional[str] = None
    tags: List[str] = []
    default_model: str = "gpt-4o"


class CommitVersionRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    commit_message: str = "Update prompt"
    model: str = "gpt-4o"
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 2048


class ParseVariablesRequest(BaseModel):
    text: str


class RunPlaygroundRequest(BaseModel):
    prompt_id: Optional[str] = None
    system_prompt: str
    user_prompt: str
    variables: Dict[str, Any] = {}
    model: str = "gpt-4o"
    temperature: float = 0.7


class ComparePromptsRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    variables: Dict[str, Any] = {}
    models: List[str] = ["gpt-4o", "claude-3.5-sonnet", "gemini-1.5-pro"]


class EvaluateRequest(BaseModel):
    execution_id: str
    correctness: float = 10.0
    hallucination: float = 0.0
    tone: float = 9.5
    clarity: float = 9.5
    relevance: float = 10.0


class AIAssistRequest(BaseModel):
    text: str
    action: str = "IMPROVE"  # IMPROVE, OPTIMIZE, FORMAT, EXPLAIN


class RestoreVersionRequest(BaseModel):
    version_id: str


@router.get("", response_model=List[Dict[str, Any]])
async def list_prompts(
    folder_id: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    is_favorite: Optional[bool] = Query(None),
):
    prompts = manager.repo.list_prompts(folder_id=folder_id, tag=tag, query=query, is_favorite=is_favorite)
    return [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "folder_id": p.folder_id,
            "tags": p.tags,
            "is_favorite": p.is_favorite,
            "current_version_id": p.current_version_id,
            "updated_at": p.updated_at.isoformat(),
        }
        for p in prompts
    ]


@router.post("", status_code=201)
async def create_prompt(req: CreatePromptRequest):
    res = manager.create_prompt(
        title=req.title,
        description=req.description,
        system_prompt=req.system_prompt,
        user_prompt=req.user_prompt,
        folder_id=req.folder_id,
        tags=req.tags,
        default_model=req.default_model,
    )
    return res


@router.get("/folders")
async def list_folders():
    return manager.repo.list_folders()


@router.post("/folders", status_code=201)
async def create_folder(name: str, parent_id: Optional[str] = None):
    folder = PromptFolder(name=name, parent_id=parent_id)
    return manager.repo.save_folder(folder)


@router.get("/templates")
async def list_templates():
    return manager.repo.list_templates()


@router.post("/templates/{template_id}/clone", status_code=201)
async def clone_template(template_id: str, title: Optional[str] = None):
    res = manager.clone_template(template_id, title_override=title)
    if not res:
        raise HTTPException(status_code=404, detail="Template not found")
    return res


@router.get("/analytics")
async def get_analytics():
    return manager.get_analytics()


@router.post("/parse-variables")
async def parse_variables(req: ParseVariablesRequest):
    vars_list = manager.extract_variables(req.text)
    return {"variables": vars_list}


@router.post("/playground/run")
async def run_playground(req: RunPlaygroundRequest):
    execution = manager.run_playground(
        prompt_id=req.prompt_id,
        system_prompt=req.system_prompt,
        user_prompt=req.user_prompt,
        variables=req.variables,
        model=req.model,
        temperature=req.temperature,
    )
    return execution


@router.post("/playground/stream")
async def stream_playground(req: RunPlaygroundRequest):
    async def sse_generator():
        async for chunk in manager.stream_playground(
            system_prompt=req.system_prompt,
            user_prompt=req.user_prompt,
            variables=req.variables,
            model=req.model,
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")


@router.post("/compare")
async def compare_prompts(req: ComparePromptsRequest):
    results = []
    for model in req.models:
        exec_item = manager.run_playground(
            prompt_id=None,
            system_prompt=req.system_prompt,
            user_prompt=req.user_prompt,
            variables=req.variables,
            model=model,
        )
        results.append(exec_item)
    return {"comparisons": results}


@router.post("/evaluate")
async def evaluate_prompt(req: EvaluateRequest):
    eval_item = manager.evaluate_execution(
        execution_id=req.execution_id,
        correctness=req.correctness,
        hallucination=req.hallucination,
        tone=req.tone,
        clarity=req.clarity,
        relevance=req.relevance,
    )
    return eval_item


@router.post("/ai-assist")
async def ai_assist_prompt(req: AIAssistRequest):
    improved = req.text
    if req.action == "IMPROVE":
        improved = f"{req.text}\n\nEnsure clear, structured output with zero ambiguity."
    elif req.action == "OPTIMIZE":
        improved = f"System: You are an expert AI assistant.\n\nUser: {req.text}"
    elif req.action == "FORMAT":
        improved = req.text.strip()
    return {"suggested_text": improved, "action": req.action}


@router.get("/{prompt_id}")
async def get_prompt(prompt_id: str):
    details = manager.get_prompt_details(prompt_id)
    if not details:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return details


@router.patch("/{prompt_id}")
async def update_prompt(prompt_id: str, updates: Dict[str, Any]):
    prompt = manager.repo.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    if "title" in updates:
        prompt.title = updates["title"]
    if "description" in updates:
        prompt.description = updates["description"]
    if "is_favorite" in updates:
        prompt.is_favorite = updates["is_favorite"]
    if "tags" in updates:
        prompt.tags = updates["tags"]
    manager.repo.save_prompt(prompt)
    return prompt


@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: str):
    success = manager.repo.delete_prompt(prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"status": "ARCHIVED", "id": prompt_id}


@router.get("/{prompt_id}/versions")
async def get_versions(prompt_id: str):
    return manager.repo.get_versions(prompt_id)


@router.post("/{prompt_id}/versions", status_code=201)
async def commit_version(prompt_id: str, req: CommitVersionRequest):
    ver = manager.commit_version(
        prompt_id=prompt_id,
        system_prompt=req.system_prompt,
        user_prompt=req.user_prompt,
        commit_message=req.commit_message,
        model=req.model,
        temperature=req.temperature,
        top_p=req.top_p,
        max_tokens=req.max_tokens,
    )
    if not ver:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return ver


@router.post("/{prompt_id}/restore")
async def restore_version(prompt_id: str, req: RestoreVersionRequest):
    ver = manager.restore_version(prompt_id, req.version_id)
    if not ver:
        raise HTTPException(status_code=404, detail="Prompt or version not found")
    return ver
