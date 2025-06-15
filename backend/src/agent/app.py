# backend/src/agent/app.py

# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
import os # Import os
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware # <--- ADD THIS IMPORT

# Define the FastAPI app
app = FastAPI()

# --- vvv ADD THIS WHOLE BLOCK vvv ---
# Set up CORS middleware
# This is crucial for allowing the frontend to communicate with the backend
# when they are hosted on the same domain but served from different paths.
origins = [
    # In a real production app, you might want to be more restrictive.
    # For this example, allowing all origins is fine for simplicity.
    # Or, you can get the specific frontend URL from an environment variable.
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)
# --- ^^^ END OF BLOCK ^^^ ---


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    return StaticFiles(directory=build_path, html=True)


# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)