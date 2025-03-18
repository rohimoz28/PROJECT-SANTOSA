## v7.0.0 (2025-03-01)

### Production Release

### New
- 5b8d2de [FEAT] PAM: Printout Form Konfirmasi Promosi Mutasi (FKPM) ~ Fix outdate commit
- d86c513 [FEAT] TMS: Payroll Summary
- bfa2e80 [FEAT] PAM: Monitoring Off Contract

### Improvement
- c673211 [IMP] TMS : Mandatory field Period pada Permission Entry dan Overtime Request
- e16c084 [IMP] TMS : Tambahan UI untuk Tampilan Kolom di TMS Summary (1)
- 32dce51 [IMP] TMS : Menambah page Absent pada TMS Entry Summary
- b46252e [IMP] TMS : Mengganti field status menjadi field status_attendance
- 44fd6e7 [IMP] TMS : Perhitungan absen long shift

---

### Main branch - Development 

### New
- b81b567 [FEAT]PAM : Monitoring Contract
- a9412d6 [FEAT] PAM: Printout Form Konfirmasi Promosi Mutasi (FKPM)
- b7336ba [FEAT] TMS: Payroll Summary

### Improvement
- ee9a76d [IMP] TMS : Mandatory field Period pada Permission Entry dan Overtime Request
- 220a9e1 [IMP] TMS : Menambah page Absent pada TMS Entry Summary

### Fix
- eae683f [FIX] TMS : Update fungsi button Close di Period

## v6.0.0 (2025-02-22)

### Production Release

### New
- f5cda10 TMS : View Mapping PinCode (0658631f)
- b0a574b PAM: Printout Form Konfirmasi Pengunduran Diri (FKPD)
- 093c0fb TMS : View Mapping PinCode
- 2c6adde PAM : Hide field Contract Type yang berada sebelum field Contract Time
- b21875b PAM: Printout Paklaring format Taman Sari
- c527469 TMS : Report Excel, PDF, dan View di Overtime Bundling

### Improvement
- a81f266 TMS: Tambahan UI untuk Tampilan Kolom di TMS Summary (2)
- ea487ba PAM : Set readonly field ketika state bukan Draft
- b6c59dd PAM : Mengubah Flag EOC -> Rehire di Employee Exit & Mutation
- 976c88c PAM : Menambahkan field Contract Number di bawah field Contract Type
- ecf0b58 PAM : Menambah Field Leave Calc di Benefit/Allowance
- 2cd72bd TMS : (Update SP) Leave Allocation kebuat record baru berdasarkan tanggal
- 7020131 PAM : Menampilkan field join date & marital status untuk Mutasi Correction
- 06f6acf TMS : Menampilkan field detail Date di sheet Overtime TMS Entry Summary
- bab5e8b PAM : Field Overtime dibuat radio button di Personal Admin
- 4036ea9 TMS : Leave Allocation kebuat record baru berdasarkan tanggal

### Fix
- 1d23bb0 PAM: Fix HRMS Address
- e2c63da TMS : Memperbaiki Delay 10 jadi 9, 8 jadi 7 TMS Entry Summary
- 761bb16 TMS : OT Reguler delay nya belum diberi toleransi, fix perhitungan OT & ANS
- 99200bc TMS : Memperbaiki Delay 10 jadi 9, 8 jadi 7 TMS Entry Summary
- 124826b TMS : Fix Perhitungan Keterlambatan (10 min)
- 4918fe4 PAM: Fix Printout Parklaring format Cimareme
- 4f644bd recompute periode from to di tms summary
- e7f7795 Fix Perhitungan OT Holiday
- 5e81724 TMS : Fix delay status attendance = Delay In
---

### Main branch - Development 

### New
- 5091fa5 PA:Read Only When not Draft
- 5a72022 PAM:Monitoring Off Contract
- 6694183 PAM: Printout Form Konfirmasi Pengunduran Diri (FKPD)

### Improvement
- 447b39c TMS: Mengganti field status menjadi field status_attendance
- b2e89eb TMS : Perhitungan absen long shift
- 6cd67d1 PAM : Mengubah Flag EOC -> Rehire di Employee Exit & Mutation
- 342c383 TMS : (Update SP) Leave Allocation kebuat record baru berdasarkan tanggal
- 89bb39a PAM : Set readonly field ketika state bukan Draft
- 8ac78b0 PAM : Menambah Field Leave Calc di Benefit/Allowance
- c17e70e PAM:Menambahkan field Contract Number di bawah field Contract Type
- e0174b2 TMS : menambah yang kurang pada task Tambahan UI untuk Tampilan Kolom di TMS Summary (1) (53e8e913)
- 133dff8 PAM : Menampilkan field join date & marital status untuk Mutasi Correction

### Fix
- 25a5dad PAM: Fix HRMS Address
- 8bbe7e9 TMS : OT Reguler delay nya belum diberi toleransi, fix perhitungan OT & ANS
- 48a6c24 TMS : Memperbaiki Delay 10 jadi 9, 8 jadi 7 TMS Entry Summary

## v5.0.0 (2025-02-15)

### Production Release

### New
- 3e7cc66 purchase_request: Install Module Purchase Request
- 093c0fb TMS : View Mapping PinCode
- 2c6adde PAM : Hide field Contract Type yang berada sebelum field Contract Time
- 752fd1b TMS : setting action button function
- 272717d TMS: Create new model Overtime Bundling
- b21875b PAM: Printout Paklaring format Taman Sari
- c527469 TMS: Report Excel, PDF, dan View di Overtime Bundling

### Improvement
- 06f6acf TMS : Menampilkan field detail Date di sheet Overtime TMS Entry Summary
- bab5e8b PAM : Field Overtime dibuat radio button di Personal Admin
- 8b0d5e9 TMS : Filtering TMS Summary
- 76bd427 TMS : Menampilkan saldo Cuti di transaksi Permission Entry
- 00997dc TMS : Filter search di Data Upload Attendance
- ecd9dbc PAM : Menambah field boolean End of Contract di Checking ID
- 094ab41 TMS : flag dibuat optional hide di tms
- 23c5d4c PAM : Readonly Field ketika state Hold (samakan dengan state Approved)
- 9469ab4 PAM : Domain Filter Sub Department dan Job Position di Employee Mutation
- cc18643 TMS : Perhitungan Keterlambatan

### Fix
- 124826b TMS : Fix Perhitungan Keterlambatan (10 min)
- 4918fe4 PAM : Fix Printout Parklaring format Cimareme
- 4f644bd TMS : recompute periode from to di tms summary
- e7f7795 TMS : Fix Perhitungan OT Holiday
- 5e81724 TMS : Fix delay status attendance = Delay In
- c15bf25 TMS : TMS Summary Move notes dibawah and UI fix bug line
- a4dfa4c TMS : Fix Perhitungan waktu cuti di Permission Entry

---

### Main branch - Development 

### New
- 41406b2 purchase_request: Install Module Purchase Request
- ee14732 PAM: Printout Paklaring format Taman Sari
- 0d7cc6b PAM : Hide field Contract Type yang berada sebelum field Contract Time
- 8c32164 PAC : Hide field Contract Type
- 29e38ee TMS : View Mapping PinCode
- 92b227d TMS: Report Excel, PDF, dan View di Overtime Bundling

### Improvement
- 133dff8 PAM : Menampilkan field join date & marital status untuk Mutasi Correction
- 389ec81 PAM : Set readonly field ketika state bukan Draft
- c088658 TMS : Leave Allocation kebuat record baru berdasarkan tanggal
- 7f5b023 TMS : Menampilkan field detail Date di sheet Overtime TMS Entry Summary
- 45b0cbc TMS : Menampilkan saldo Cuti di transaksi Permission Entry
- 3161dee TMS : Filtering TMS Summary
- 05e474c PAM : Field Overtime dibuat radio button di Personal Admin
- 199d57e PAM : Menambah field boolean End of Contract di Checking ID

### Fix
- 2b78c51 TMS : Fix Perhitungan waktu cuti di Permission Entry
- 224e554 PAM : Fix Printout Parklaring format Cimareme
- 263b8fa TMS : TMS Summary Move notes dibawah and UI fix bug line
- 5dd0b0a TMS : Fix Perhitungan Keterlambatan (10 min)
- 94970bb TMS : Fix delay status attendance = Delay In
- 675c81a TMS : Fix Perhitungan OT Holiday
- 8596049 TMS : recompute periode from to di tms summary

## v4.0.0 (2025-02-08)

### Production Release

### Improvement

### New
- 7deffa6 default filter pages besides all
- 1c12be2 [TMS] : Menambah Group By default berdasarkan flag OT & ANS di TMS Summary

### Improvement
- 9930a87 [TMS] : Menambahkan field Bundling OT di overtime request list tree
- 607ee7d [TMS] : Menambah filter Date di wizard Report Overtime Attendances &...
- 02a5123 [TMS] : Revisi Report PDF Overtime Request
- 9f9faa5 [PAM] : Link tabel Employment Details dengan tabel Product
- b416eae [PAM] : Menambah field Employment Status untuk Mutasi dengan Service Type ACTV
- c89dfd5 [TMS] : Perhitungan Cuti 1/2 Hari di TMS Entry Summary

### Fix
- 4f37832 [TMS] : Fix Field OT, OT Flat dan Night Shift di TMS Summary
- e4e2b25 [TMS] : Perbaiki UI TMS Summary
- 0269293 [TMS] : Fix field Appv OT Fr dan Appv OT To di detail TMS entry details
- 7b9928c [TMS] : Fix OT 2 minus

---

### Main branch - Development 

### New
- 11979e5 setting action button function
- c739bc4 [TMS] : Create new model Overtime Bundling
- fe5274e default filter pages besides all

### Improvement
- 2d4df7d [PAM] : Domain Filter Sub Department dan Job Position di Employee Mutation
- e11d17a [PAM] : Readonly Field ketika state Hold (samakan dengan state Approved)
- ee9aff7 [TMS] : field flag dibuat optional hide di tms
- 2759f32 [TMS] : Menambahkan field Bundling OT di overtime request list tree
- 23d7c29 [TMS] : Menambah filter Date di wizard Report Overtime Attendances & merapihkan nama Field
- 7184926 [TMS] : Menampilkan saldo Cuti di transaksi Permission Entry
- 6571924 [TMS] : Perhitungan Keterlambatan
- 329f0be [TMS] : Revisi Report PDF Overtime Request
- c1a275b [TMS] : Perhitungan Cuti 1/2 Hari di TMS Entry Summary

### Fix
- ea173df [TMS] : Fix Field OT, OT Flat dan Night Shift di TMS Summary
- e2520b0 [TMS] : Fix field Appv OT Fr dan Appv OT To di detail TMS entry details
- b6936dc [TMS] : Fix OT 2 minus
- 88b7aa1 [TMS] : Perbaiki UI TMS Summary
- 091f1f7 [TMS] : Fix Perhitungan waktu cuti di Permission Entry

## v3.0.0 (2025-02-01)

### Production Release

### New
- f735197 [TMS] : Report Overtime Attendances (Request vs Realization)
- 2bf0f6c [PAM] : Menambahkan fields employment details di personal admin
- b9a517e [TMS] : Report PDF dan Excel Overtime Request 2
- 8e9538e [TMS] : Mengubah susunan field pada form [TMS] Entry Summary
- 5c4a113 [TMS] : Menukar posisi field Rel Time dengan App Time di OT Attendances
- 3c914b3 [TMS] : Menambahkan field OT, OT Flat, dan Night Shift pada header [TMS] Entry Summary

### Improvement
- 11113c5 [TMS] : Mengubah susunan field pada form Permission Entry
- 8f6138f [TMS] : Mengubah susunan field pada form Overtime Request
- d070a11 [TMS] : Mengubah susunan field pada form Adjustment Request

### Fix
- 05ae2aa TMS : Fix field Sub Department yang terfilter karena Area & BU readonly di Overtime Request

---
### Main branch - Development 

### Improvement
- 23576d6 [PAM]: Link tabel Employment Details dengan tabel Product
- 1b966ec [PAM] : Menambah field Employment Status untuk Mutasi dengan Service Type ACTV
- 3b9c27c [TMS]: Menambah State Cancel by System di form Permission Entry


## v2.0.0 (2025-01-25)

### Production Release

### Fix
- b1e48e0 [TMS] Fix button Mass Approve HRD, Mass Approve CA dan Mass Approve TMS Summary
- a854d8e [PAM] NIK ke replace dengan yang terbaru ketika ada transaksi di Mutation

---

### Main branch - Development 

### New
- eb62df9 [TMS] adding new feature leave allocation
- 09326d1 [TMS] Menambahkan field OT, OT Flat, dan Night Shift pada header TMS Entry Summary

### Improvement
- d6758ec [TMS] Mengubah susunan field pada form Adjustment Request
- 28f3d44 [TMS] Mengubah susunan field pada form Overtime Request
- 88ec98f [TMS] Mengubah susunan field pada form TMS Entry Summary
- 3d4f04e [TMS] Menukar posisi field Rel Time dengan App Time di OT Attendances

### Fix
-  6eb1f10 [TMS] Fix button Mass Approve HRD, Mass Approve CA dan Mass Approve TMS Summary

## v1.0.0 (2025-01-18)

### Production Release

### New
- 72a72ae [PAM] Penambahan field Employment Status ketika Service Type = CORR di Employee Mutation

### Bug fixes
- 7176a623 [TMS] Perbaiki OT Holiday yang masuk tanpa approval
- 7176a623 [PAM] Field Workingday Menghilang
- 41045dd0 [PAM] Issue kurang library '_'
- 4e2660b6 [TMS] Tambah field employee_id di Absen Staging
- 5c2cdd3  [PAM] Fix Group Button Close
- f7d2f83  [PAM] fix field WD di benefit/allowance
- 99508297 [PAM] Menambahkan field flag OT Flat
- b06f47e1 [TMS] Perbaiki hitungan Approval TMS Entry Summary di Tree setelah Proses ulang
- e5e50191 [PAM] Employment Status disesuaikan berdasarkan Job Status
- 9882c7a8 [PAM] fix kondisi readonly field emp_status state == approved
- 6730d846 [TMS] Menghilangkan widget timepicker pada field datetime
- 6730d846 [TMS] Mengubah field employee_id di TMSEntry Detail
  
---

### Main branch - Development 

### New
- 7c37066 [PAM] Penambahan field Tanggal diterima & Tanggal dikembalikan

### Fix
- c1a6a04 [PAM] NIK ke replace dengan yang terbaru ketika ada transaksi di Mutation
- 966c2d3 [TMS] Tambah field employee_id di Absen Staging
- 61b43c5 [TMS] Perbaiki OT Holiday yang masuk tanpa approval
- 4f0481f [TMS] fix widget pada field time
- f4d3b06 [PAM] Update 'Employment Status' dan 'Employment Tracking' berdasarkan transaksi Employee Exit
- 7c37066 [PAM] Location berdasarkan Business Unit