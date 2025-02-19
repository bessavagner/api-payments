from app.config import settings

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{settings.APP_DIR}.main:app",
        host=settings.ALLOWED_HOSTS[0],
        port=settings.APP_PORT,
        reload=True,
        reload_includes=[
            "app/*.py",
            "app/api/*.py",
            "app/api/endpoints/*.py",
            "app/services/*.py",
            "app/core/*.py",
        ]
    )
