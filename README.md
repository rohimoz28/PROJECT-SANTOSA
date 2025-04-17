# Project Santosa

## Install
1. clone project <br>
   `git clone ssh://git@192.168.16.133:2224/sanbe-it-corp/development/it-corp/project-santosa.git`
2. masuk ke direktori conf <br>
   `cd project-santosa/conf`
3. build image custom-odoo:17.0 (optional) <br>
   `docker build -t custom-odoo:17.0 .`
4. jalankan docker compose <br>
   `docker compose -f docker-compose.yaml -f dev.yaml up -d`
## FaQ
Umumnya, semua masalah pada docker bisa telusuri melalui logs-nya menggunakan command:
`docker compose logs -f --tail 200`. <br> Namun, jika setelah membaca logs belum ditemukan akar masalah-nya. Bisa
terlebih dulu memastikan bahwa container sudah berjalan dengan command : `docker ps`. <br> Pastikan container yang tertera
pada `docker-compose.yaml`, tertera juga ketika menjalankan command tersebut.

Masalah lainnya yang mungkin terjadi, 
1. Konfigurasi port tidak tepat. <br> Silahkan cek konfigurasi pada file `docker-compose.yaml` / `dev.yaml`.
Pastikan, port tidak digunakan (bentrok) dengan yang sudah berjalan pada lokal. 

## Workflow
![workflow](/images/workflow.png)
1. setelah clone project, pastikan kita ada di branch `main`. <br>
   `git status`
2. lalu buat branch baru dengan nama feature/feature_name <br>
   `git checkout -b feature/feature_name`
3. jika perubahan sudah selesai dibuat, silahkan commit perubahan tersebut. <br>
   `git commit -m "commit_description"`
4. lalu push branch feature tersebut ke remote repository. <br>
   `git push origin HEAD`
5. buka akun gitlab, lalu buat Merge Request ke branch `staging`
6. jika ada conflict, cek tingkat kerumitannya. jika mudah, langsung solve di halaman gitlab.
7. **WAJIB!** Untuk proses pembuatan fitur baru selanjutnya, dimulai dari branch `main`.
   `git checkout main`
   `git pull origin main`