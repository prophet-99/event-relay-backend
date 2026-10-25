## LocalStack scripts

LocalStack executes its initialization scripts directly from the mounted Docker volume. For that reason, both lifecycle hooks and the development bootstrap script need execution permission.

Run this once after cloning the project:

```bash
chmod +x docker/localstack/init/boot.d/00-boot-banner.sh
chmod +x docker/localstack/init/ready.d/00-create-queue.sh
chmod +x docker/dev-up.sh
```

Then start the local infrastructure:
```bash
./docker/dev-up.sh
```
Once committed with execution permission, Git preserves it for collaborators using Unix-based systems.