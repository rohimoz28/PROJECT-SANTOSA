# Santosa HRMS

## Objective
Sukses install project untuk keperluan local development.

## Tech
- Docker
- Git

## Persiapan
- Install Docker
  - Linux bisa ikuti tutorial [disini](https://docs.docker.com/engine/install/)
  - Windows bisa menggunakan windows desktop, tutorial [disini](https://docs.docker.com/desktop/setup/install/windows-install/) 
  
- Install Git
  - Tutorial [disini](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## Install Project
1. Git clone project sekaligus dengan submodule-nya <br> `git clone --recurse-submodules ssh://git@192.168.16.133:2224/sanbe-it-corp/devops/docker-santosa-hrms.git`
2. Nanti akan ada folder baru dengan nama `docker-santosa-hrms`. Di dalam folder tersebut ada 2 folder, <br> - `conf` ->> folder konfigurasi docker <br> - `customize` ->> folder kustomisasi odoo
3. Masuk ke folder `conf`. Untuk menjalankan project pertama kali, gunakan command berikut <br> - `docker compose -f docker-compose.yaml -f dev.yaml up -d`
4. Selanjutnya, jika ingin restart project untuk keperluan update module, bisa gunakan command berikut <br> `docker container restart odoo-santosa-hrms`

## Project Kustomisasi Odoo
1. Seluruh modul kustomisasi odoo berada di folder `customize/santosa-hrms`
2. Penjelasan folder sebagai berikut <br> - `addons-customize` ->> berisi folder kustomisai buatan sendiri <br> - `addons-thirdparty` ->> berisi modul yang didapatkan dari pihak ketiga
3. Untuk melakukan push dan pull project menggunakan Git, bisa dilakukan di `customize/santosa-hrms`
4. Pengerjaan project ini menggunakan GitLab Workflow, lebih detail bisa cek [disini](http://192.168.16.133:8188/sanbe-it-corp/sanbe-it-corp-wiki/-/wikis/Development-Workflow)

Terima Kasih dan Happy Code!!!