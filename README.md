## Development setup with Docker
This project ships with a `docker-compose.yml` that runs both the backend (FastAPI) and the frontend (React).

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/) installed on your machine
- An OpenAI API key (you can run w/o it, but AI won't work)

### Environment variables
You need to create a file named `.env` in the repo root and define a number of environment variables. See `.env.example` to find out which variables have to be set.

### Pre-commit hooks
As the name implies, these hooks (scripts) are run automatically before `git commit`. They won't allow you to commit your changes unless all tests pass first. Some of them just fix formatting (e.g., remove trailing whitespaces), while others flag unusud variables, incorrect return types, etc. The same hooks are also run automatically on GitHub.

#### Installation
Copy the `pre-commit` hook from `.dev-setup/pre-commit` to `.git/hooks` and make it executable. E.g., on Linux:

```bash
cp .dev-setup/pre-commit .git/hooks
cmod +x .git/hooks/pre-commit
```

#### Usage

The hooks will run automatically whenever you run `git commit`. However, you can run them without actually comitting using the following command:

```bash
docker compose run --rm -T pre-commit run --color always --all-files
```

It might be useful to create an alias for it (e.g., `alias prc="..."`) if you run it frequently.

#### Bypassing

You can temporarily disable the checks (e.g., if you want to commit and push unfinished work) by using the `--no-verify` flag:

```bash
git commit -m "This commit won't trigger the hooks" --no-verify
```

### Start the stack
From the project root:

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (FastAPI docs at /docs)

Edits to your code are reflected immediately because the repo is mounted into the containers.

### Stop the stack

Either `Ctrl+C` or:

```bash
docker compose down
```

## Misc
### Updating Frontend API

Our frontend uses **OpenAPI-generated TypeScript types** to stay in sync with backend models. These types are derived from the backend's `http://backend:8000/openapi.json` spec.

When backend endpoints or models change:

1. Ensure that the backend is running:
```bash
docker compose up
```

2. Regenerate the frontend types inside Docker to update `frontend/src/types/api.ts`:
```bash
docker compose run --rm frontend npm run gen-types
```
