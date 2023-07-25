# Server Setup

## Prerequisites
1. Remote server is running
2. Ports 22, 80, 443 and 5432 are forwarded (home server)
3. Sudo access to server
4. System user is created:
   1. useradd ```$SSH_USERNAME```
   2. usermod -aG sudo ```$SSH_USERNAME```
5. Login as that user
6. [Set up GitHub for SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

## Setup: Remote Server
1. Run ```git clone YOUR_FORKED_REPO_NAME```
2. Run ```chmod +x ./.setups/server_init.sh```
3. Run ```./.setups/server_init.sh```

## Setup: External PC
1. Generate SSH Key using ssh-keygen:
   - ```ssh-keygen -t rsa -b 4096 -C "user@email.com"```
2. Bring ssh-key to remote server by running
   - ```ssh-copy-id $SSH_USERNAME@$HOSTNAME```
3. On external PC add private key to GitHub Secrets as ```$SSH_PRIVATE_KEY``` (@ home/USER/.ssh/rsa_id)
4. Add all env vars ```(.sample_env)``` to GitHub Secrets and add ```$SSH_USERNAME```

## Post Setup: Remote Server
1. Add ```$SSH_USERNAME``` to passwordless sudo @ ```sudo visudo```:
   1. for docker compose commands ``` ```
   2. for all sudo commands ```$SSH_USERNAME ALL=(ALL) NOPASSWD: ALL```
2. Optional: Remove password entry to remote server (sudo nano /etc/ssh/sshd_config)

## Result
Remote Server setup with SSH for CICD via Github Actions for docker compose stack. Every pull request into ```main``` will trigger a pipeline execution ```./.github/workflows/main.yml```. 
The pipeline will:
1. Checkout and pull the ```main``` branch onto the server
2. Connect to the remote server via SSH using the ```$SSH_PRIVATE_KEY``` for ```$SSH_USERNAME```@```$HOSTNAME```
3. Navigate to the repo directory (might need to be modified based on the repo name)
4. Run ```docker compose down```, ```docker compose build``` and ```docker compose up```

## Helpers

- `git checkout BRANCHNAME`
- `git pull origin BRANCHNAME`
