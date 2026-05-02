"""Blog CRUD API router."""

from fastapi import APIRouter, HTTPException, Request

from app.models.blog import BlogPost, BlogPostCreate, BlogPostUpdate, BlogResponse
from app.utils.auth import require_admin
from app.utils.blog_storage import (
    get_all_posts,
    get_post_by_slug,
    create_post,
    update_post,
    delete_post
)

router = APIRouter(prefix="/api/blogs", tags=["blogs"])


@router.get("/", response_model=BlogResponse)
async def list_blogs():
    """List all published blog posts (public endpoint, no auth required)."""
    posts = get_all_posts(include_unpublished=False)
    return BlogResponse(
        success=True,
        data=[post.model_dump() for post in posts]
    )


@router.get("/{slug}", response_model=BlogResponse)
async def get_blog(slug: str):
    """Get a single published blog post by slug (public endpoint)."""
    post = get_post_by_slug(slug, include_unpublished=False)
    if not post:
        return BlogResponse(success=False, error="Blog post not found")
    return BlogResponse(success=True, data=post.model_dump())


@router.post("/", response_model=BlogResponse)
async def create_blog(request: Request):
    """Create a new blog post (admin only, requires JWT)."""
    # Verify admin
    try:
        await require_admin(request)
    except HTTPException as e:
        return BlogResponse(success=False, error=e.detail)

    import json
    body = await request.body()
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return BlogResponse(success=False, error="Invalid JSON body")

    try:
        # Validate input using Pydantic model
        new_post_data = BlogPostCreate(**data)

        # Create full BlogPost with ALL fields from validated data
        new_post = BlogPost(**new_post_data.model_dump())

        created = create_post(new_post)
        return BlogResponse(success=True, data=created.model_dump())
    except ValueError as e:
        return BlogResponse(success=False, error=str(e))
    except Exception as e:
        return BlogResponse(success=False, error=f"Failed to create blog post: {str(e)}")


@router.put("/{slug}", response_model=BlogResponse)
async def update_blog(slug: str, request: Request):
    """Update an existing blog post (admin only, requires JWT)."""
    # Verify admin
    try:
        await require_admin(request)
    except HTTPException as e:
        return BlogResponse(success=False, error=e.detail)

    import json
    body = await request.body()
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return BlogResponse(success=False, error="Invalid JSON body")

    try:
        # Validate input using Pydantic model
        update_data = BlogPostUpdate(**data)

        updated = update_post(slug, update_data)
        if not updated:
            return BlogResponse(success=False, error="Blog post not found")
        return BlogResponse(success=True, data=updated.model_dump())
    except ValueError as e:
        return BlogResponse(success=False, error=str(e))
    except Exception as e:
        return BlogResponse(success=False, error=f"Failed to update blog post: {str(e)}")


@router.delete("/{slug}", response_model=BlogResponse)
async def delete_blog(slug: str, request: Request):
    """Delete a blog post (admin only, requires JWT)."""
    # Verify admin
    try:
        await require_admin(request)
    except HTTPException as e:
        return BlogResponse(success=False, error=e.detail)

    deleted = delete_post(slug)
    if not deleted:
        return BlogResponse(success=False, error="Blog post not found")
    return BlogResponse(success=True, data={"message": f"Blog post '{slug}' deleted successfully"})
