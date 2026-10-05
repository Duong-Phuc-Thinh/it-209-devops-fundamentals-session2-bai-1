# Bài tập 1: Thay đổi cổng kết nối SSH (SSH Port Hardening)

## Giới thiệu
Bài tập này hướng dẫn cách thay đổi cổng dịch vụ SSH mặc định của máy chủ từ cổng `22` sang cổng `2222`. Mục tiêu nhằm hạn chế tối đa các cuộc quét cổng tự động và giảm nguy cơ bị tấn công Brute-force từ Botnet.

Tài liệu này bao gồm hướng dẫn cấu hình thủ công và script tự động hóa bằng Python chạy dưới quyền tài khoản `devops` có quyền `sudo`.

---

## Cách chạy script cấu hình tự động

Bạn có thể chạy script Python đi kèm để cấu hình tự động chỉ với 1 dòng lệnh:

```bash
python3 harden_ssh.py
```
Script sẽ tự động yêu cầu quyền `sudo` nếu cần thiết, thực hiện backup file cấu hình SSH, đổi cổng sang `2222`, cấu hình UFW và khởi động lại dịch vụ SSH.

---

## Hướng dẫn thực hiện thủ công từng bước

### Bước 1: Sao lưu cấu hình cũ và thay đổi cổng SSH
Chỉnh sửa tệp tin `/etc/ssh/sshd_config`:
```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo nano /etc/ssh/sshd_config
```
Tìm dòng chứa `#Port 22` hoặc `Port 22`, thay đổi thành:
```text
Port 2222
```
Lưu lại và thoát (`Ctrl+O` -> `Enter` -> `Ctrl+X`).

### Bước 2: Cấu hình tường lửa UFW
Trước khi khởi động lại dịch vụ SSH, bắt buộc phải mở cổng `2222` trên tường lửa để tránh bị khóa truy cập (Lockout):
```bash
sudo ufw allow 2222/tcp
sudo ufw reload
sudo ufw status
```

### Bước 3: Khởi động lại dịch vụ SSH
Áp dụng cấu hình mới bằng cách khởi động lại SSH service:
```bash
sudo systemctl restart ssh
# Hoặc sử dụng lệnh dưới nếu hệ thống sử dụng service name 'sshd'
# sudo systemctl restart sshd
```

---

## Nhật ký log kiểm tra kết nối (Terminal Outputs)

### 1. Kiểm tra trạng thái tường lửa UFW sau khi cấu hình:
```bash
devops@ubuntu-server:~$ sudo ufw status verbose
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
2222/tcp                   ALLOW IN    Anywhere                  
2222/tcp (v6)              ALLOW IN    Anywhere (v6)             
```

### 2. Kiểm tra kết nối từ máy cá nhân qua cổng mới (2222):
```bash
$ ssh -p 2222 devops@192.168.1.100
Welcome to Ubuntu 22.04 LTS (GNU/Linux 5.15.0-88-generic x86_64)
...
Last login: Fri Oct 27 10:00:00 2023 from 192.168.1.5
devops@ubuntu-server:~$
```
*(Kết nối thành công qua cổng 2222)*

### 3. Kiểm tra kết nối từ máy cá nhân qua cổng mặc định cũ (22):
```bash
$ ssh -p 22 devops@192.168.1.100
ssh: connect to host 192.168.1.100 port 22: Connection refused
```
*(Kết nối qua cổng 22 hoàn toàn bị từ chối)*
