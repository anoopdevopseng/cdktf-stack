# cdktf-stack

## Run the project 

```
pipenv install
```

## envs Folder
Your environemtn files under **envs** folder
```
dev.yaml 
preprod.yaml
prod.yaml
```

## if you are window user you can run it like this
```
$env:ENV = "dev"; cdktf synth
$env:ENV = "dev"; cdktf plan
        OR
$env:ENV = "preprod"; cdktf synth
$env:ENV = "preprod"; cdktf plan

        OR
$env:ENV = "prod"; cdktf synth
$env:ENV = "prod"; cdktf plan
```

## Remvoe the powershell Variable
```
Remove-Item Env:ENV
```
## If you are linux user

```
ENV=dev cdktf synth
ENV=dev cdktf plan
        OR
ENV=preprod cdktf synth
ENV=preprod cdktf plan
        OR
ENV=prod cdktf synth
ENV=prod cdktf plan
```