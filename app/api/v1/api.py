from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, histories
from app.api.v1.endpoints import (
    programs,
    categories,
    program_categories,
    option_groups,
    options,
    favorites,
    examples,
    man_pages
)

api_router = APIRouter()

# Gắn router của programs vào với tiền tố /programs
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"]) 
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
api_router.include_router(histories.router, prefix="/histories", tags=["Histories"])
api_router.include_router(programs.router, prefix="/programs", tags=["Programs"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(program_categories.router, prefix="/program-categories", tags=["Program - Categories Link"])
api_router.include_router(option_groups.router, prefix="/option-groups", tags=["Option Groups"])
api_router.include_router(options.router, prefix="/options", tags=["Options"])
api_router.include_router(examples.router, prefix="/examples", tags=["Examples"])
api_router.include_router(man_pages.router, prefix="/man-pages", tags=["Man Pages"])