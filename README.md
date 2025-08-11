# **cdktf-stack**

## Requirements

- Python 3.13
- cdktf version: 0.21.0
- cdktf-cli: 0.21.0

---

# **Setup Instructions**

## **Linux/macOS**

#### 1. Install Dependencies

```sh
yes | sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.13
sudo apt-get install pipenv -y
npm install --global cdktf-cli@0.21.0
```

#### 2. Set Environment Variables

```sh
export PIPENV_VENV_IN_PROJECT=1
export PIPENV_IGNORE_VIRTUALENVS="1"
```

#### 3. Install Python Dependencies

```sh
pipenv --python=/bin/python3.13 install
```

#### 4. Download Providers

```sh
cdktf get --force
```

#### 5. Run CDKTF Commands

```sh
ENV=dev cdktf synth
ENV=dev cdktf plan
ENV=dev cdktf deploy --auto-approve

# Or for other environments:
ENV=preprod cdktf synth
ENV=prod cdktf synth
```

---

## **Windows (PowerShell)**

#### 1. Set Environment Variables

```powershell
$env:PIPENV_VENV_IN_PROJECT=1
$env:PIPENV_IGNORE_VIRTUALENVS = "1"
```

#### 2. Install Python Dependencies

```powershell
pipenv install
```

#### 3. Download Providers

```powershell
cdktf get --force
```

#### 4. Run CDKTF Commands

```powershell
$env:ENV = "dev"; cdktf synth
$env:ENV = "dev"; cdktf plan
$env:ENV = "dev"; cdktf deploy --auto-approve

# Or for other environments:
$env:ENV = "preprod"; cdktf synth
$env:ENV = "preprod"; cdktf plan
$env:ENV = "preprod"; cdktf deploy --auto-approve

$env:ENV = "prod"; cdktf synth
$env:ENV = "prod"; cdktf plan
$env:ENV = "prod"; cdktf deploy --auto-approve
```

#### 5. Remove PowerShell Variable

```powershell
Remove-Item Env:ENV
```

---

## **Environments**

Your environment files should be placed under the **envs** folder:

```
envs/
  dev.yaml
  preprod.yaml
  prod.yaml
```