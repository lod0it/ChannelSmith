# ChannelSmith Essentials

**Status:** Beta complete (525 tests, 85% coverage) + Web UI MVP | **Phase:** Post-Beta | **Branch:** dev

## Running ChannelSmith

### Web UI
```bash
python -m channelsmith
```
Opens http://localhost:5000 in your browser. Dark theme with Tailwind CSS, pack/unpack workflows, drag-drop support.

## Core Rules (MANDATORY)
- **Naming:** snake_case files/functions, PascalCase classes, UPPER_CASE constants
- **Types:** Type hints REQUIRED on all functions: `def fn(x: Type) -> ReturnType:`
- **Docs:** Google-style docstrings only
- **Code:** No GUI in core/, logging only (no print), no sys.exit in widgets
- **Tests:** pytest, >90% core coverage

## API (core/)
- `load_template(path) → Template`
- `pack_texture(imgs: List[PIL.Image], template) → PIL.Image`
- `unpack_texture(img: PIL.Image, template) → Dict[str, PIL.Image]`

## Architecture
```
core/           Engine (no GUI deps)
api/            Flask REST API endpoints
frontend/       HTML/CSS/JS Web UI
templates/      JSON: orm.json, ord.json + loader.py
utils/          image_utils, constants
```

## Web UI Endpoints
- `GET /` - Serve frontend
- `GET /api/health` - Health check
- `GET /api/templates` - List available templates
- `POST /api/pack` - Pack texture channels (multipart/form-data)
- `POST /api/unpack` - Unpack texture (multipart/form-data)

## Defaults
AO=1.0 | Roughness=0.5 | Metallic=0.0 | Displacement=0.5 | Alpha=1.0

## Git
- **Branches:** main (stable) | dev (work)
- **Format:** `<type>(<scope>): <desc>` (feat/fix/docs/test/refactor)

## Quick Commands
`pytest` | `pytest tests/api/` | `black channelsmith/` | `pylint channelsmith/` | `python -m channelsmith`
