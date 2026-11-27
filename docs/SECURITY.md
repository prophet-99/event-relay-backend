## LocalStack scripts

LocalStack executes its initialization scripts directly from the mounted Docker volume. For that reason, both lifecycle hooks need execution permission.

Run this once after cloning the project:

```bash
chmod +x docker/localstack/init/boot.d/00-boot-banner.sh
chmod +x docker/localstack/init/ready.d/00-create-queue.sh
```

Then start the local infrastructure:
```bash
docker compose -f docker-compose-dev.yml up --build
```
Once committed with execution permission, Git preserves it for collaborators using Unix-based systems.
